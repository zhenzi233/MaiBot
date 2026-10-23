# MaiBot 插件开发踩坑记录

> 基于 MaiBot 1.3.12 + SDK 2.15.0，在 Windows 上从零写一个「表情入库」插件的完整过程。
> 这份文档记录的是**官方文档没写、只有踩过才知道**的部分。
> 如果你只想快速抄一个能跑的最小插件，直接看第二章的模板。

---

## 一、先搞清楚运行模型

MaiBot 的插件**不是**在主进程里 import 进来的模块，而是：

```
主程序 (bot.py)
  └── 扩展插件 Runner 进程（独立 python 进程）
        └── 你的 plugin.py
              ↓ RPC（命名管道）
        主程序的能力层（emoji.register / send.text / message.get_by_id ...）
```

几个直接影响写法的结论：

1. **你的插件拿不到主程序的任何内部对象**，只能用 `self.ctx.<能力名>` 通过 RPC 请求。
2. **插件进程的 cwd 通常是主程序根目录**（但也可能是插件目录），所以找文件要么用绝对路径，要么多给几个候选路径。
3. 日志里能看到 `RPC=\\.\pipe\maibot-plugin-<主程序pid>-<hash>`，这就是插件与主程序的通道。
4. 主程序重启 = 插件全部重新加载；改 `plugin.py` 必须重启（`config.toml` 可以热重载）。

日志位置（Windows 部署）：

```
<MaiBot>/logs/svc.err.log     # 我们用 redirect 起的，GBK 编码
<MaiBot>/logs/bot.err.log     # 早期手动启动时的日志
```

读取时注意编码：

```python
open('logs/svc.err.log','rb').read().decode('gbk', errors='replace')
```

---

## 二、最小可运行插件（照着抄）

### 2.1 目录结构

```
plugins/
└── my_plugin/
    ├── _manifest.json     # 必需
    ├── plugin.py          # 必需
    └── config.toml        # 强烈建议（没有会有告警）
```

> ⚠️ 上游 `.gitignore` 默认忽略整个 `plugins/*`。要把它纳入你的仓库，得加例外：
>
> ```gitignore
> /plugins/*
> !/plugins
> !/plugins/my_plugin        # ← 你的插件
> ```

### 2.2 `_manifest.json` 完整模板

```json
{
  "manifest_version": 2,
  "id": "yourname.my-plugin",
  "version": "1.0.0",
  "name": "插件显示名",
  "description": "一句话说明它做什么",
  "author": { "name": "yourname", "url": "https://github.com/yourname" },
  "license": "MIT",
  "urls": {
    "repository": "https://github.com/yourname/repo",
    "homepage": "https://github.com/yourname/repo",
    "documentation": "https://github.com/yourname/repo",
    "issues": "https://github.com/yourname/repo/issues"
  },
  "host_application": { "min_version": "1.3.0", "max_version": "1.3.99" },
  "sdk": { "min_version": "2.8.0", "max_version": "2.99.99" },
  "dependencies": [],
  "capabilities": [
    "send.text",
    "emoji.register"
  ],
  "i18n": {
    "default_locale": "zh-CN",
    "locales_path": "_locales",
    "supported_locales": ["zh-CN"]
  },
  "plugin_type": "tool",
  "display": {
    "icon": { "type": "emoji", "value": "⭐" }
  }
}
```

### 2.3 `config.toml` 最小形态

```toml
[plugin]
name = "my_plugin"
config_version = "1.0.0"
enabled = true

[my_section]
some_option = 8.0
```

### 2.4 `plugin.py` 最小形态

```python
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from maibot_sdk import Field, MaiBotPlugin, PluginConfigBase, Tool
from maibot_sdk.types import ToolParameterInfo, ToolParamType

logger = logging.getLogger(__name__)


class PluginSection(PluginConfigBase):
    """[plugin] 段：SDK 要求的基本信息。"""

    name: str = Field(default="my_plugin", description="插件名")
    config_version: str = Field(default="1.0.0", description="配置版本")
    enabled: bool = Field(default=True, description="是否启用")


class MyPluginConfig(PluginConfigBase):
    """配置模型：字段分组要和 config.toml 的段一一对应。"""

    plugin: PluginSection = Field(default_factory=PluginSection)


class MyPlugin(MaiBotPlugin):
    """插件主类。"""

    config_model = MyPluginConfig

    async def on_load(self) -> None:
        logger.info("我的插件已加载")

    async def on_config_update(self, scope: str, config_data: dict, version: str) -> None:
        logger.info("配置已更新 scope=%s version=%s", scope, version)

    async def on_unload(self) -> None:
        logger.info("我的插件已卸载")

    @Tool(
        "my_tool",
        description="给模型看的工具说明。说清楚什么时候该调、调了会发生什么。",
        parameters=[
            ToolParameterInfo(
                name="text",
                param_type=ToolParamType.STRING,
                description="参数说明",
                required=False,
                default=None,
            ),
        ],
    )
    async def handle_my_tool(self, text: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        # 能力全部走 self.ctx，绝对不能写成 self.api
        count = await self.ctx.emoji.get_count()
        return {"success": True, "message": f"当前表情 {count} 张"}


def create_plugin() -> MyPlugin:
    """Host 通过这个工厂函数加载插件，必须有。"""
    return MyPlugin()
```

---

## 三、6 + 1 条硬要求

前 6 条会在**加载期**报错（容易发现），最后 1 条只在**调用工具时**炸（最坑）。

| # | 要求 | 不满足时的报错 |
|---|---|---|
| 1 | `_manifest.json` 必须有 `i18n` 段 | `Manifest 校验失败: 缺少必需字段: i18n` |
| 2 | `display.icon` 必须是对象，不能是字符串 | `字段 display.icon 必须为对象` |
| 3 | `display` 里不能有未声明字段（如 `color`） | `存在未声明字段: display.color` |
| 4 | 模块级必须有 `create_plugin()` | `缺少 create_plugin 函数或未检测到可按 BasePlugin` |
| 5 | 必须实现 `on_load()` | `必须实现 on_load()` |
| 6 | 必须实现 `on_config_update()` | `必须实现 on_config_update()` |
| 7 | `config.toml` 必须有 `[plugin]` 且含 `config_version` | `插件配置文件缺少 [plugin] 配置节，且必须提供 plugin.config_version 版本号` |
| **8** | **能力入口是 `self.ctx.*` 不是 `self.api.*`** | 加载正常，调用时报 `'XxxPlugin' object has no attribute 'api'` |

`display.icon` 的正确写法（三种都行，看 SDK 版本支持）：

```json
"display": { "icon": { "type": "emoji", "value": "⭐" } }
"display": { "icon": { "type": "local", "value": "./icon.webp" } }
```

---

## 四、能力（capabilities）：声明 + 调用

### 4.1 两步走，缺一不可

1. 在 `_manifest.json` 的 `capabilities` 数组里**声明**；
2. 代码里用 `await self.ctx.<组>.<方法>(...)` 调用。

只做第 2 步不做第 1 步，会得到：

```
[E_CAPABILITY_DENIED] 插件 xxx 未获授权能力: message.get_recent
```

### 4.2 常用能力速查

| 能力 | 调用方式 | 说明 |
|---|---|---|
| `send.text` | `self.ctx.send.text(text, stream_id)` | 发文本 |
| `send.emoji` | `self.ctx.send.emoji(...)` | 发表情库里的表情 |
| `send.image` | `self.ctx.send.image(...)` | 发图 |
| `emoji.get_count` | `await self.ctx.emoji.get_count()` | 表情总数 |
| `emoji.get_info` | `await self.ctx.emoji.get_info()` | 库存统计（总数/上限等） |
| `emoji.get_random` | `await self.ctx.emoji.get_random(count=5)` | 随机取表情 |
| `emoji.get_by_description` | `await self.ctx.emoji.get_by_description("开心", limit=5)` | 按语义找 |
| `emoji.register` | `await self.ctx.emoji.register_emoji(base64_str)` | **注册新表情**（描述由 Host 生成） |
| `emoji.delete` | `await self.ctx.emoji.delete_emoji(hash)` | 删除表情 |
| `message.get_by_id` | `await self.ctx.message.get_by_id(mid, stream_id=..., include_binary_data=True)` | 按 id 取消息 |
| `message.get_recent` | `await self.ctx.message.get_recent(chat_id=..., limit=8)` | 取最近消息 |
| `message.get_by_time_in_chat` | 同上，按时间段 | 翻历史 |
| `chat.get_group_streams` | `await self.ctx.chat.get_group_streams()` | 列群会话 |
| `llm.generate` | `await self.ctx.llm.generate(...)` | 让模型生成一段文字 |
| `database.query` | `await self.ctx.database.query(...)` | 查宿主数据库 |
| `llm.get_available_models` | — | 列可用模型 |

> 能力名以 `src/plugin_runtime/capabilities/registry.py` 的 `_register(...)` 为准，
> SDK 侧的封装在 `maibot_sdk/capabilities/` 下，每个文件对应一类能力。

### 4.3 返回值结构：别猜，要递归找

**这是本次踩坑最久的地方。** `message.get_by_id` 和 `message.get_recent` 的返回结构**不一致**：

```
get_by_id   → {"success": true, "message": {...}}
get_recent  → [ {...}, {...} ]          # 直接是 list，没有 messages 包一层
```

而且 `message` 里可能**没有** `raw_message` 字段；图片组件的 `binary_data_base64`
只有在宿主已经把图片读进内存时才存在，多数时候只有 `hash`。

结论：**不要按固定字段路径硬读**。用递归找特征：

```python
def deep_collect_images(payload, depth=0):
    """递归找出任意结构里的图片二进制。"""
    if depth > 6 or payload is None:
        return []
    found = []
    if isinstance(payload, (list, tuple)):
        for item in payload:
            found.extend(deep_collect_images(item, depth + 1))
        return found
    if isinstance(payload, dict):
        b64 = payload.get("binary_data_base64") or payload.get("base64")
        if isinstance(b64, str) and len(b64) > 32:
            try:
                data = base64.b64decode(b64)
                if data:
                    return [data]
            except Exception:
                pass
        kind = str(payload.get("type") or "").lower()
        if kind in ("image", "emoji", "picture"):
            data = load_by_hash(payload.get("hash"))
            if data:
                return [data]
        for value in payload.values():
            if isinstance(value, (dict, list, tuple)):
                found.extend(deep_collect_images(value, depth + 1))
        return found
    if hasattr(payload, "__dict__"):
        return deep_collect_images(payload.__dict__, depth + 1)
    return []
```

### 4.4 图片二进制的两条路

MaiBot 把图片按 **sha256** 命名存在本地：

```
<MaiBot>/data/images/        # 群聊图
<MaiBot>/data/prompt_imgs/   # 私聊图、多模态输入
<MaiBot>/data/emoji/         # 表情库本体
```

所以拿不到 base64 时，用组件里的 `hash` 去这些目录按文件名前缀找：

```python
def load_by_hash(digest):
    key = str(digest or "").strip().lower()
    if len(key) < 16 or any(c not in "0123456789abcdef" for c in key):
        return None
    for base in (Path.cwd(), Path(__file__).resolve().parent):
        for sub in ("data/images", "data/prompt_imgs", "data/emoji"):
            directory = base / sub
            if not directory.is_dir():
                continue
            for entry in directory.iterdir():
                if entry.is_file() and entry.name.lower().startswith(key):
                    return entry.read_bytes()
    return None
```

实测：一张 1.6 MB 的图按 hash 读出来字节数完全一致。

---

## 五、调试方法论

### 5.1 改完怎么生效

| 改了什么 | 需要做什么 |
|---|---|
| `plugin.py` | **必须重启主程序** |
| `config.toml` | 热重载（Host 会调 `on_config_update`） |
| `_manifest.json` | 需要重启 |

Windows 上重启麦麦的可用命令（detached，不挂控制台）：

```powershell
$owner = (Get-NetTCPConnection -State Listen -LocalPort 8001 | Select-Object -First 1).OwningProcess
$kids = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $owner } | Select-Object -ExpandProperty ProcessId
foreach ($p in @($kids) + @($owner)) { Stop-Process -Id $p -Force }

$cmd = 'cmd /c "set EULA_AGREE=...&& set PRIVACY_AGREE=...&& cd /d F:\QQAI\MaiBot&& F:\QQAI\venv\Scripts\python.exe bot.py >> logs\svc.out.log 2>> logs\svc.err.log"'
Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = 'F:\QQAI\MaiBot' }
```

### 5.2 看插件加载结果

搜索日志里的 `已加载=`：

```
[扩展插件] 已启动：pid=..., 已加载=5（..., zhenzi233.store-emoji-plugin），失败=0
```

`失败=0` 且列表里有你的插件 id = 加载成功。**注意「加载成功」不等于「工具能调」**——
本项目的第 8 条坑就是加载成功但调用炸。

### 5.3 工具调用失败怎么查

1. 日志搜 `工具=<你的工具名>`，确认模型到底调没调；
2. 再看紧随其后的 `[你的插件日志]` 一行——**在工具里多打日志，别省**：

```python
logger.info("取图失败，返回结构: %s", shapes)          # 结构诊断
logger.info("组件样例: %s", json.dumps(raw)[:500])     # 原始数据
```

3. 报错 `E_CAPABILITY_DENIED` → 回 manifest 补 `capabilities`；
4. 报错 `object has no attribute 'api'` → 改成 `self.ctx`。

### 5.4 单测技巧

插件不需要跑起来才能测。把纯函数（解析、找文件）抽成模块级函数，
用 `importlib` 直接加载 `plugin.py` 测：

```python
import importlib.util
spec = importlib.util.spec_from_file_location("p", "plugins/my_plugin/plugin.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

assert m.my_pure_function({"a": 1}) == ...
```

本次就是靠这招在五次修改中验证四种返回结构都能解析，省了好几轮重启。

---

## 六、实战案例：表情入库插件的 4 轮踩坑

背景：群友说「把这张图存进表情库」，麦麦回「我库满了 塞不进去」——实际库是 346/2000。

### 第 1 轮：加载失败 × 4 次

依次撞上：缺 `i18n` → `display.icon` 类型错 → 缺 `create_plugin` → 缺 `on_load`
→ 缺 `on_config_update` → 缺 `[plugin]` 配置节。详见第三章。

### 第 2 轮：工具能调，但 `no attribute 'api'`

`self.api.emoji.register_emoji(...)` → `'StoreEmojiPlugin' object has no attribute 'api'`。
改成 `self.ctx.emoji.register_emoji(...)`。

### 第 3 轮：能调，但「抓不到图」

按 `message.raw_message[].binary_data_base64` 硬读，永远拿到空。原因：组件只有 `hash`。

### 第 4 轮：兜底路径被拒 + 结构不对

- `message.get_recent` 返回 `list`，代码却按 `{messages: [...]}` 读 → 空
- 该能力没在 manifest 声明 → `E_CAPABILITY_DENIED`

最终方案 = **递归找特征 + 按 hash 读本地缓存 + get_recent 兜底**。

顺带修掉的一个模型行为问题：因为插件之前一直失败，模型学会了编理由
（「我库满了」）。补上 `emoji_library_status` 工具让它能查真实库存后，
它才不再瞎说——**给模型一个能查真相的工具，比在提示词里叮嘱一百遍有用**。

---

## 七、设计经验

1. **不要在插件里重复实现宿主已有逻辑。** 表情入库就走 `emoji.register`，
   让宿主去管去重、描述生成、上限检查，别自己写文件再扫目录。
2. **工具描述写清楚「什么时候该调」。** 模型只按 description 判断，
   写「群友让你存图时调用」比写「存入表情」有效得多。
3. **失败要说出可执行的动作。** 返回「抓不到那张图，请对方单独重发一条」，
   比返回 `success:false` 有用——模型会把这句话转述给用户。
4. **给能力的工具要附带状态查询工具。** 有「存」就要有「查」，
   否则模型只能猜，猜错就开始编。
5. **所有魔数（路径、大小限制）都放到配置里**，别写死在代码中。

---

## 八、清单：从零到能用

- [ ] 建目录 `plugins/<id>/`
- [ ] 抄 `_manifest.json`，改 id / name / capabilities
- [ ] 抄 `plugin.py` 骨架（含 `config_model`、`on_load`、`on_config_update`、`create_plugin`）
- [ ] 写 `config.toml`，`[plugin]` 段带 `config_version`
- [ ] 在 `_manifest.json` 声明要用的能力（少一个就 DENIED）
- [ ] 工具内一律 `self.ctx.*`
- [ ] 纯函数抽出来，`importlib` 单测跑通再重启
- [ ] 重启后用日志确认 `已加载=N，失败=0` 且列表里有你的 id
- [ ] 真机调用一次，看 `[你的插件]` 日志确认进入代码
- [ ] 失败分支打结构日志，别静默返回
- [ ] 要给版本库就改 `.gitignore` 加 `!/plugins/<id>`
