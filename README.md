# MaiBot（本地定制分支）

本仓库 fork 自 [Mai-with-u/MaiBot](https://github.com/Mai-with-u/MaiBot)，只记录本机运行所需的改动。

- 基线：`c602a27`
- 分支：`local/custom`
- `main` 保持上游原样，开发都在本分支

## 本机改了什么

### 1. GIF 图片写入长期记忆会失败

`src/services/memory_flow_service.py`

A-Memorix 的资产层白名单只有 BMP / JPEG / PNG / WEBP：

```python
_FORMAT_TO_MIME = {"BMP": ..., "JPEG": ..., "PNG": ..., "WEBP": ...}   # src/A_memorix/core/image/asset_store.py
```

群里发动图时，`image_memory(action="ingest")` 直接抛
`RuntimeError: 不支持的图片格式: GIF`，那张图记录不下来（消息不中断，但记忆丢失）。

改法：在调用 ingest 之前先做格式降级——GIF / APNG 取第 0 帧转成 PNG，
其余格式原样透传。函数 `_to_static_image_bytes()` 是纯本地转换，失败时回落原始字节，
不影响其他链路（动图理解仍走抽帧那条路）。

升级后补丁会被覆盖，重跑即可（幂等）：

```bash
python scripts/patch_gif_memory.py
```

### 2. 本机运维与配置脚本

`scripts/` 下是与本机部署相关的脚本，均不参与运行时：

| 脚本 | 用途 |
|---|---|
| `patch_gif_memory.py` | 重放上面的 GIF 补丁（程序升级后用） |
| `add_vision_model.py` / `add_embedding_model.py` | 向 `model_config.toml` 追加视觉、向量模型 |
| `add_aliyun_drawpic.py` / `config_drawpic.py` | 配置绘图插件的阿里百炼平台与参数 |
| `apply_prompts_v21.py` / `rewrite_presets_v2.py` / `tighten_ears_v3.py` | 按 markdown 源批量写入绘图风格预设 |
| `add_meme_style.py` / `add_dafeiyu_style.py` / `style_kawaii.py` | 追加风格预设 |
| `backfill_emoji_desc.py` / `import_emojis.py` | 表情库描述回填与导入 |
| `export_chat_transcript.py` / `export_transcript_xiaojingyu.py` / `export_dafeiyu_memory.py` | 导出聊天记录、记忆包 |
| `analyze_dafeiyu_style.py` / `fetch_dafeiyu_style_data.py` | 从协议端消息库统计某个账号的说话风格 |
| `tune_proactive.py` / `tune_bot_banter.py` / `strict_dafeiyu_persona.py` | 调整发言频率、对话风格、人设 |
| `patch_adapter_config.py` / `patch_bot_config.py` / `patch_model_config.py` / `switch_account.py` | 配置补丁与账号切换 |

## 本机插件

### `plugins/store_emoji_plugin/` — 表情入库（v1.0.0）

MaiBot 的表情库只有「后台每 10 分钟扫 `data/emoji` 自动注册」，**没有任何工具能按群友
要求把某张图存进库**。后果是群友说「存起来」时，模型只能编一个理由（实测说过
「我库满了 塞不进去」，当时库是 346/2000，根本没满）。

本插件补两个工具：

| 工具 | 作用 |
|---|---|
| `store_emoji` | 取消息里的图片 → `emoji.register` → 返回哈希与当前库存 |
| `emoji_library_status` | 返回真实库存（总数 / 上限 / 剩余），让它被问「满了吗」时说真话 |

取图策略是「递归找」而不是按固定字段读 —— `message.get_by_id` 与 `message.get_recent`
返回结构不同（后者直接是 list，前者可能没有 `raw_message`），字段层级也随版本变。
现在的做法：递归遍历任意结构，遇到非空 `binary_data_base64` 直接解码；
遇到 `type=image/emoji` 且带 `hash` 的，按哈希去 `data/images`、`data/prompt_imgs`
找同名文件（MaiBot 的图片缓存就是按 sha256 命名的）。两种都取不到才报错。

### 写 MaiBot 插件要过的 6 关

踩了一遍才凑齐，记下来省下次：

1. `_manifest.json` 必须有 `i18n` 段（`default_locale` / `locales_path` / `supported_locales`）
2. `display.icon` 必须是对象：`{"icon": {"type": "emoji", "value": "⭐"}}`，不能是字符串
3. 模块级必须有 `create_plugin()` 工厂函数
4. 必须实现 `on_load()`
5. 必须实现 `on_config_update()`（哪怕空实现）
6. `config.toml` 必须有 `[plugin]` 段且含 `config_version`

另有一条不会在加载期报错、只在调用时炸的：**能力入口是 `self.ctx.*`，不是 `self.api.*`**。
manifest 里 `capabilities` 没声明的能力会直接返回 `E_CAPABILITY_DENIED`。

## 注意

- `data/` 与 `config/` 不进版本库（含聊天记录、记忆库与 API Key）
- `plugins/` 默认被上游 gitignore，本仓库对 `store_emoji_plugin` 单独开了例外
- 本分支不追求与上游同步；上游有修复时按需 cherry-pick
