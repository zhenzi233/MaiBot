# -*- coding: utf-8 -*-
"""导出大肥鱼绘图提示词为 markdown,交给其他 agent 调整"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

S = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'
OUT = r'F:\QQAI\大肥鱼绘图提示词.md'

s = json.load(open(S, encoding='utf-8'))
presets = s['settings']['style']['presets']
gen = s['settings']['general']

HEAD = """# 大肥鱼绘图提示词(交给你调整)

> 这是 DeepSeek 鲸鱼娘「大肥鱼」的绘图提示词现状。
> 角色固定人设 + 两个画风预设,供你优化。**请只改提示词文本,不要改结构。**

## 一、运行环境

| 项 | 值 |
|---|---|
| 出图平台 | 阿里百炼(通义万相 / Qwen-Image) |
| 模型 | `qwen-image-3.0-pro`(默认) / `qwen-image-3.0` / `qwen-image-2.1-pro` / `z-image-turbo` |
| 接口 | `POST /api/v1/services/aigc/multimodal-generation/generation` |
| 尺寸 | `1024*1024` |
| 出图耗时 | 43~65 秒 |
| 接入方式 | MaiBot 绘图插件(`maimai-drawpic-plugin`)的「风格预设」 |

**预设机制**:风格预设 = 一正一反两段文本模板。
- `{prompt}` 会被替换成用户这次的描述(如果模板里没有这个占位符,用户描述会自动追加到末尾)
- `{negative_prompt}` 同理
- 预设存储在 `data/plugins/maimai-drawpic-plugin/workspace_settings.json` 的 `settings.style.presets[]`
- **注意**:插件的 `config.toml` 里写 `[style]` 无效,启动时会被删掉,只有上面那个 JSON 生效

## 二、角色固定设定(所有预设共用,不可改)

来自社区设定图(鲸鱼娘二创):

| 部位 | 特征 |
|---|---|
| 体型 | Q 版,2~2.5 头身,圆脸,短手短脚,**体型不可改** |
| 头发 | 深蓝到浅蓝渐变超长波浪发,发梢浅蓝半透明,发丝厚块面带块状/水滴状高光 |
| 头顶 | **一撮弯钩状呆毛**(深蓝到浅蓝的头发卷),不是鲸鱼尾巴 |
| 耳朵 | **横向伸出的深蓝色鲸鱼鳍状耳**,鳍下缘一圈白色荷叶边,耳侧系蓝色蝴蝶结 |
| 眼睛 | 大圆眼,蓝色渐变虹膜,白色大高光 + 星形闪光;闭眼是弯月 |
| 服装 | 深藏青长袖女仆装 + 白色荷叶边围裙(围裙中央鲸鱼刺绣)+ 蓝宝石胸针 + 裙摆金色 X 缝线 |
| 尾巴 | 身后一条深蓝色鲸鱼尾巴带尾鳍 |
| 腿脚 | 白色荷叶边小腿袜 + 深蓝色玛丽珍小皮鞋 |
| 画风 | 日系卡哇伊贴纸风:粗且带色的深藏青描边,赛璐璐上色,硬边 2~3 色阶,白底 + 手绘小装饰(爱心、汗滴、星星、速度线) |

## 三、两个预设的定位

| 预设名 | 用途 | 是否写字 |
|---|---|---|
| `大肥鱼` | 立绘、场景图、日常配图 | 不写 |
| `大肥鱼梗图` | 表情包、带梗的图 | **写**,气泡内中文大字 |

"""

TAIL = """

## 四、已知问题与踩过的坑

### 1. 模型对"比喻"是整体替换,不是局部微调

| 我写过 | 模型画出 | 结论 |
|---|---|---|
| 鲸鱼尾状呆毛 | 头顶长了一条鲸鱼尾巴 | 别用生物器官名做比喻 |
| 耳朵像两片扇形小贝壳 | 耳朵变成了贝壳/蝴蝶翅膀,连方向都变了 | 同上 |
| 鲸鱼鳍形状的耳朵 | 有时被画成尖三角(像精灵耳) | 见第 2 条 |

**有效写法**:直接描述形态 + 材质,例如「横向伸出的鳍形,下缘一圈白色荷叶边」。

### 2. 耳朵最容易画错

参考图里耳朵是:横向、略宽、深蓝、下缘白色荷叶边、上方蓝色蝴蝶结。
模型容易画成:尖三角精灵耳 / 蝴蝶翅膀 / 贝壳。

### 3. 中文文字渲染不稳定

- 3~8 字:基本准确
- 10 字以上:容易糊、缺笔画、重复

业界做法(参考 `SeOgi-Tsu/character-sticker-studio`)是**不让模型写字**,出图后本地用字体排字。我们目前仍让模型直接写,只在提示词里限制字数。

### 4. 画风漂移的元凶

早期写过「日系厚涂、柔和打光」,与目标画风(赛璐璐硬边)正好相反,导致出一堆插画感厚涂图。
**赛璐璐与厚涂是互斥的**,不要在正向里同时出现两者的词。

### 5. 多角色与单人的冲突

预设原本写「单人构图」并在反向里写「多个角色」,结果用户要画两只时被拦。
现改为「角色居中;默认单人,明确要求多个角色时按数量画同一个角色」。

### 6. 负面词里不要放「尖耳朵」

我们的目标是圆润鳍形,但反向写「尖耳朵,精灵耳」时反而把耳朵往尖锐方向带。
已改为只排「贝壳耳,蝴蝶翅膀耳」。

## 五、想请你优化的方向

1. **耳朵与呆毛的稳定性**:有没有更不容易被误解的说法?现在大概 7 成能对。
2. **两个角色的区分度**:画多只时,怎么让它们看起来是同一角色而不是姐妹?
3. **梗图文字**:在仍然让模型写字的前提下,怎么提高长句准确率?
4. **画风锁定**:有没有更硬的说法,让模型不往厚涂/3D 跑?
5. **构图**:1024×1024 正方形贴纸构图,有没有更好的取景建议(半身/全身/大头)?

## 六、改完怎么用

1. 把新的正向/反向文本发回来
2. 我写进 `workspace_settings.json` 的 `settings.style.presets[]`,并把 `revision` 加一
3. 重启 MaiBot(插件启动时读取该 JSON)
4. 用同一句场景跑对照图,确认没退化

**只改文本,不要改 JSON 结构、不要动 `config.toml`。**
"""

lines = [HEAD]
for p in presets:
    lines.append('## 预设:%s\n' % p['name'])
    lines.append('**启用**: %s  \n**描述**: %s\n' % (p.get('enabled'), p.get('description', '')))
    lines.append('### 正向模板\n')
    lines.append('```text\n%s\n```\n' % p['positive_prompt_template'])
    lines.append('### 反向模板\n')
    lines.append('```text\n%s\n```\n' % p['negative_prompt_template'])
    lines.append('---\n')

lines.append('## 附:当前参数\n')
lines.append('```json\n%s\n```\n' % json.dumps({
    'default_model': gen.get('default_model'),
    'request_timeout_seconds': gen.get('request_timeout_seconds'),
    'command_reply_mode': gen.get('command_reply_mode'),
    'default_style': s['settings']['style'].get('default_style'),
    'presets': [p['name'] for p in presets],
}, ensure_ascii=False, indent=2))

lines.append(TAIL)

open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('已写出:', OUT)
print('字数约', len('\n'.join(lines)))
