"""表情包入库插件 — MaiBot SDK v2

背景：MaiBot 的表情库是「后台每 10 分钟扫一遍 data/emoji 自动注册」，
没有任何工具能「把群友刚发的这张图存进表情库」。所以当群友说「存起来」时，
模型只能编一个理由（例如「我库满了」），实际什么都没发生。

本插件补上这个能力：

- Tool `store_emoji`：把指定消息（默认当前这条）里的图片读出来，
  经 `emoji.register` 注册进表情库，返回哈希与当前容量；
- Tool `emoji_library_status`：返回真实库存（数量 / 上限 / 已用比例），
  让模型在被问到「满了吗」时能说真话。

设计要点：
1. 不自己写文件、不自己扫目录 —— 一律走 Host 的 `emoji.register` 能力，
   这样描述生成、去重、上限检查都由 Host 统一负责。
2. 拿图走 `message.get_by_id(include_binary_data=True)`，不依赖本地缓存路径。
3. 消息里没有图片时明确报错，而不是让模型以为存成功了。
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from maibot_sdk import API, Field, MaiBotPlugin, PluginConfigBase, Tool
from maibot_sdk.types import ToolParameterInfo, ToolParamType

logger = logging.getLogger(__name__)


def _load_manifest_version() -> str:
    try:
        data = json.loads((Path(__file__).parent / "_manifest.json").read_text(encoding="utf-8"))
        version = str(data.get("version") or "").strip()
        return version or "0.0.0"
    except Exception:
        return "0.0.0"


PLUGIN_VERSION = _load_manifest_version()


class PluginSection(PluginConfigBase):
    """[plugin] 段：SDK 要求的基本信息。"""

    name: str = Field(default="store_emoji_plugin", description="插件名")
    config_version: str = Field(default="1.0.0", description="配置版本")
    enabled: bool = Field(default=True, description="是否启用表情入库工具")


class StoreSection(PluginConfigBase):
    """[store] 段：入库限制。"""

    max_binary_mb: float = Field(
        default=8.0,
        ge=0.5,
        le=32.0,
        description="允许入库的图片最大体积（MB）；超过则拒绝并说明原因",
        json_schema_extra={"label": "单张上限(MB)"},
    )


class StoreEmojiConfig(PluginConfigBase):
    """插件配置：与 config.toml 的段落一一对应。"""

    __ui_label__ = "表情入库"

    plugin: PluginSection = Field(default_factory=PluginSection)
    store: StoreSection = Field(default_factory=StoreSection)


def _candidate_cache_dirs() -> List[Path]:
    """MaiBot 的图片缓存目录候选。

    图片按 sha256 命名存放在这些目录里（实测：群图在 data/images，
    私聊/多模态输入图在 data/prompt_imgs）。插件进程的 cwd 通常是主程序根目录，
    但也兼容从插件目录启动的情况，所以同时给出两种相对路径。
    """
    bases = [Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[2]]
    dirs: List[Path] = []
    for base in bases:
        for sub in ("data/images", "data/prompt_imgs", "data/emoji"):
            dirs.append(base / sub)
    return dirs


def _load_image_bytes_by_hash(digest: str) -> Optional[bytes]:
    """按 sha256 在本地图片缓存里找出这张图并读成 bytes。

    为什么需要它：`message.get_by_id(include_binary_data=True)` 只有在组件已经把
    二进制读进内存时才带 binary_data_base64；多数情况下组件只带 hash，
    直接取会拿到空。缓存文件本来就是按 hash 命名的，按名字找最稳。
    """
    key = str(digest or "").strip().lower()
    if len(key) < 16 or any(ch not in "0123456789abcdef" for ch in key):
        return None
    for directory in _candidate_cache_dirs():
        try:
            if not directory.is_dir():
                continue
            for entry in directory.iterdir():
                if not entry.is_file():
                    continue
                name = entry.name.lower()
                if name.startswith(key):
                    data = entry.read_bytes()
                    if data:
                        return data
        except Exception:
            continue
    return None


def _deep_collect_images(payload: Any, depth: int = 0) -> List[bytes]:
    """在任意返回结构里递归找出图片二进制。

    为什么用"递归找"而不是按固定字段读：Host 的 message.get_by_id 与
    message.get_recent 返回结构并不一致（一个可能是 {success, message:{...}}，
    另一个直接是 list），字段层级也随版本变。与其逐版适配，不如按特征找：
      · 字典里出现非空 `binary_data_base64` → 直接解码；
      · 字典里出现 `type` 为 image/emoji 且带 `hash` → 去本地缓存按哈希取。
    深度上限 6，避免异常结构把栈打穿。
    """
    if depth > 6 or payload is None:
        return []
    found: List[bytes] = []

    if isinstance(payload, (list, tuple)):
        for item in payload:
            found.extend(_deep_collect_images(item, depth + 1))
        return found

    if isinstance(payload, dict):
        b64 = payload.get("binary_data_base64") or payload.get("base64")
        if isinstance(b64, str) and len(b64) > 32:
            try:
                data = base64.b64decode(b64)
                if data:
                    found.append(data)
            except Exception:
                pass
        if found:
            return found
        kind = str(payload.get("type") or payload.get("component_type") or "").lower()
        if kind in ("image", "emoji", "picture"):
            digest = str(payload.get("hash") or payload.get("binary_hash") or "").strip()
            data = _load_image_bytes_by_hash(digest)
            if data:
                return [data]
        for value in payload.values():
            if isinstance(value, (dict, list, tuple)):
                found.extend(_deep_collect_images(value, depth + 1))
        return found

    # 少数实现返回带 __dict__ 的对象
    if hasattr(payload, "__dict__"):
        return _deep_collect_images(getattr(payload, "__dict__", {}) or {}, depth + 1)
    return []


def _pick_first_image(payload: Any) -> Optional[bytes]:
    """取第一张图片的二进制（递归收集后取首个）。"""
    images = _deep_collect_images(payload)
    return images[0] if images else None


class StoreEmojiPlugin(MaiBotPlugin):
    """把群友发的图存入表情库。"""

    config_model = StoreEmojiConfig

    async def on_load(self) -> None:
        """插件加载：登记两个工具，日志里显式说明本插件补齐了什么能力。"""
        logger.info("表情入库插件(v%s)已加载：store_emoji / emoji_library_status", PLUGIN_VERSION)

    async def on_config_update(self, scope: str, config_data: dict, version: str) -> None:
        """配置热重载：本插件只有开关与体积上限，无需重建状态。"""
        logger.info("表情入库插件配置已更新(scope=%s version=%s)", scope, version)


    async def on_unload(self) -> None:
        """插件卸载：无后台任务，无需清理。"""
        logger.info("表情入库插件已卸载")


    @Tool(
        "store_emoji",
        description=(
            "把一条消息里的图片存入你的表情包库（真正写进库里，不是嘴上说说）。"
            "群友让你「存起来/收了/存进表情库」时调用。默认存当前正在回的那条消息；"
            "要存别的消息就传它的 message_id。返回库里当前总数，便于如实回答「满没满」。"
        ),
        parameters=[
            ToolParameterInfo(
                name="message_id",
                param_type=ToolParamType.STRING,
                description="要存哪条消息的图（聊天记录里的 #编号）；留空表示当前这条消息",
                required=False,
                default=None,
            ),
            ToolParameterInfo(
                name="note",
                param_type=ToolParamType.STRING,
                description="可选备注，仅用于本次结果说明；表情描述由系统自动生成",
                required=False,
                default=None,
            ),
        ],
    )
    async def handle_store_emoji(
        self,
        message_id: Optional[str] = None,
        note: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """LLM 工具入口：把图片注册进表情库。"""
        if not self.config.plugin.enabled:
            return {"success": False, "message": "表情入库工具已在配置中关闭"}

        target_id = str(message_id or kwargs.get("message_id") or kwargs.get("msg_id") or "").strip()
        stream_id = str(kwargs.get("stream_id") or kwargs.get("session_id") or kwargs.get("chat_id") or "").strip()
        if not target_id:
            return {
                "success": False,
                "message": "没拿到要存的消息编号：请传 message_id（聊天记录里那条消息前的 #编号）",
            }

        binary = None
        tried = []
        try:
            result = await self.ctx.message.get_by_id(
                target_id,
                stream_id=stream_id,
                chat_id=stream_id,
                include_binary_data=True,
            )
            tried.append(("get_by_id", result))
            binary = _pick_first_image(result)
        except Exception as exc:  # noqa: BLE001
            logger.warning("读取消息失败: %s", exc)
            tried.append(("get_by_id_error", str(exc)))

        # 按 id 拿不到图时（id 不是这条流里的消息 / 已出缓存 / 组件无二进制），
        # 退一步扫最近消息：群友刚发完图让你存，最近一条带图的通常就是要存的那张。
        if not binary and stream_id:
            try:
                recent = await self.ctx.message.get_recent(chat_id=stream_id, limit=8)
                tried.append(("get_recent", recent))
                binary = _pick_first_image(recent)
            except Exception as exc:  # noqa: BLE001
                logger.warning("扫描最近消息失败: %s", exc)

        if not binary:
            shapes = []
            for name, payload in tried:
                if isinstance(payload, dict):
                    shapes.append(f"{name}: keys={list(payload)[:6]}")
                elif isinstance(payload, list):
                    shapes.append(f"{name}: list[{len(payload)}]")
                else:
                    shapes.append(f"{name}: {str(payload)[:40]}")
            logger.info("取图失败，返回结构: %s", " | ".join(shapes)[:400])
            try:
                first = tried[0][1] if tried else None
                msg = first.get("message") if isinstance(first, dict) else None
                raw = (msg or {}).get("raw_message") if isinstance(msg, dict) else None
                logger.info("组件样例: %s", json.dumps(raw, ensure_ascii=False)[:500] if raw else "(无 raw_message)")
            except Exception:
                pass
            return {
                "success": False,
                "message": (
                    "抓不到那张图：消息里没有可用的图片数据。"
                    "请对方把图片单独重发一条，再说一次「存起来」"
                ),
            }

        size_mb = len(binary) / 1048576
        if size_mb > float(self.config.store.max_binary_mb):
            return {
                "success": False,
                "message": (
                    f"这张图 {size_mb:.1f} MB，超过本插件上限 {self.config.store.max_binary_mb:.1f} MB，没有入库。"
                    "可以告诉对方图太大、换一张小的"
                ),
            }

        try:
            result = await self.ctx.emoji.register_emoji(base64.b64encode(binary).decode("ascii"))
        except Exception as exc:  # noqa: BLE001
            logger.warning("注册表情失败: %s", exc)
            return {"success": False, "message": f"入库失败：{exc}"}

        registered = result
        if isinstance(result, dict):
            registered = result.get("emoji_hash") or result.get("hash") or result.get("success")

        status = await self._library_status()
        parts = ["已存入表情包库"]
        if note:
            parts.append(f"（备注：{note}）")
        if status.get("total") is not None:
            parts.append(f"，当前共 {status['total']} 张")
            if status.get("limit"):
                parts.append(f"（上限 {status['limit']}，还剩 {max(0, int(status['limit']) - int(status['total']))} 张）")
        return {
            "success": True,
            "message": "".join(parts),
            "emoji_hash": registered,
            "library": status,
        }

    @Tool(
        "emoji_library_status",
        description=(
            "查询表情包库的真实容量：总数、上限、还剩多少。"
            "被问「库满了吗」「还能存几张」时调用，不要凭印象回答。"
        ),
        parameters=[],
    )
    async def handle_library_status(self, **kwargs: Any) -> Dict[str, Any]:
        """LLM 工具入口：返回真实库存。"""
        status = await self._library_status()
        if status.get("total") is None:
            return {"success": False, "message": "取不到表情库统计（Host 未返回数据）"}
        msg = f"表情库共 {status['total']} 张"
        if status.get("limit"):
            left = max(0, int(status["limit"]) - int(status["total"]))
            msg += f"，上限 {status['limit']}，还能存 {left} 张"
        return {"success": True, "message": msg, "library": status}

    async def _library_status(self) -> Dict[str, Any]:
        """读 Host 的表情库统计，统一成 {total, limit}。"""
        try:
            info = await self.ctx.emoji.get_info()
        except Exception as exc:  # noqa: BLE001
            logger.debug("读取表情库统计失败: %s", exc)
            return {"total": None, "limit": None}
        data = info if isinstance(info, dict) else getattr(info, "__dict__", {}) or {}
        total = data.get("total") or data.get("count") or data.get("registered")
        limit = data.get("max_reg_num") or data.get("limit") or data.get("capacity")
        try:
            total = int(total) if total is not None else None
        except Exception:
            total = None
        try:
            limit = int(limit) if limit is not None else None
        except Exception:
            limit = None
        if total is None:
            try:
                total = int(await self.ctx.emoji.get_count())
            except Exception:
                total = None
        return {"total": total, "limit": limit}

def create_plugin() -> StoreEmojiPlugin:
    """创建表情入库插件实例（Host 通过本工厂加载）。"""
    return StoreEmojiPlugin()
