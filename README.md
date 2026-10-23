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

## 注意

- `data/` 与 `config/` 不进版本库（含聊天记录、记忆库与 API Key）
- 本分支不追求与上游同步；上游有修复时按需 cherry-pick
