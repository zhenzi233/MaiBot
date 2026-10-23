# -*- coding: utf-8 -*-
"""导出 v2 绘图提示词(三预设)为 markdown"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

S = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'
OUT = r'F:\QQAI\大肥鱼绘图提示词_v2.md'

s = json.load(open(S, encoding='utf-8'))
presets = s['settings']['style']['presets']
gen = s['settings']['general']

HEAD = """# 大肥鱼绘图提示词 v2(已按评审意见重写)

> 上一版六个问题:呆毛变尾巴、耳朵偏尖、画风带渐变、背景出现场景、主体被压缩、文字排版。
> 本版已全部按评审建议改写。**请只改提示词文本,不要改 JSON 结构。**

## 一、本版改了什么

| 评审指出的问题 | 本版做法 |
|---|---|
| 呆毛被画成鲸鱼尾 | 改为「由头发形成的**单根**弧形发卷」,强调同材质同线稿、末端圆钝、宽度均匀、不分叉、不增加第二撮 |
| 耳朵偏尖 | 不再只写「鲸鱼鳍形」,补齐**方向(横向展开)、宽度(宽大)、位置(脸两侧耳根)、轮廓(圆润扁平略下弯)** |
| 画风带渐变柔光 | 改为「赛璐璐**三档色**(基础/阴影/高光)、阴影边缘硬朗、不晕染」,并加「白色贴纸描边」 |
| 纯白背景与场景冲突 | **拆成三个预设**:贴纸(纯白)/ 梗图(纯白+气泡)/ 场景(允许环境) |
| 主体被头发尾巴挤压 | 加构图约束:主体占画布高度 75%~85%,头顶发卷、双耳、围裙、胸针、尾巴完整可见 |
| 长句文字不可靠 | 梗图气泡限 **4~6 个汉字**,单气泡横向排列 |

## 二、运行环境

| 项 | 值 |
|---|---|
| 平台 | 阿里百炼(通义万相 / Qwen-Image) |
| 模型 | `qwen-image-3.0-pro`(默认) / `qwen-image-3.0` / `qwen-image-2.1-pro` / `z-image-turbo` |
| 接口 | `POST /api/v1/services/aigc/multimodal-generation/generation` |
| 尺寸 | `1024*1024`,单张 43~65 秒 |
| 预设存储 | `data/plugins/maimai-drawpic-plugin/workspace_settings.json` → `settings.style.presets[]` |

**机制**:预设 = 一正一反两段模板。`{prompt}` 替换成用户描述;模板里没有占位符时用户描述自动追加。
插件 `config.toml` 里写 `[style]` **无效**,启动时会被删,只有上面那个 JSON 生效。

## 三、三个预设的分工

| 预设 | 用途 | 背景 | 文字 |
|---|---|---|---|
| `大肥鱼` | 贴纸、立绘、头像 | 纯白,禁止场景 | 无 |
| `大肥鱼梗图` | 表情包、带梗的图 | 纯白 | 单气泡,≤6 汉字 |
| `大肥鱼场景` | 房间、户外、剧情 | 允许环境,仍是扁平色块 | 无 |

## 四、角色固定设定(三预设共用,不可改)

Q 版 2~2.5 头身;深蓝到浅蓝渐变超长波浪发 + 块状高光;
头顶一撮单根弧形发卷(不是尾巴);
脸两侧横向宽鳍耳 + 白色荷叶边 + 蓝蝴蝶结;
蓝渐变大眼 + 星形高光;
深藏青女仆装 + 白荷叶边围裙(鲸鱼刺绣)+ 蓝宝石胸针 + 金色 X 裙摆;
身体后侧深蓝鲸鱼尾巴(不从头顶长出);白袜 + 深蓝玛丽珍鞋。

---

"""

TAIL = """

## 五、上一轮踩过的坑(供参考,别重复)

1. **比喻会被整体替换**:写「耳朵像扇形小贝壳」→ 耳朵整个变成贝壳形;写「鲸鱼尾状呆毛」→ 头顶长尾巴。
2. **器官名会污染**:正向里高频出现「鲸鱼尾巴/尾鳍」时,这些特征会渗到头顶。
3. **赛璐璐与厚涂互斥**:正向里同时出现两者,会退化成普通插画。
4. **反向词也可能带偏**:反向写「尖耳朵、精灵耳」反而把耳朵推向尖锐,现已移出。
5. **「纯白无场景」和「床铺云朵」不能同时要求**:本版拆成场景预设解决。

## 六、这一版想请你验的

1. **呆毛**:是否稳定成一撮弧形发卷?有没有残留尾鳍感?
2. **耳朵**:宽度是否过了(比设定图略宽)?轮廓是否够圆润?
3. **线稿粗细**:现在外轮廓很粗、贴纸白边明显,是否接近设定图?
4. **主体占比**:75%~85% 是否合适?头发有没有又盖住肚子?
5. **场景预设**:环境是扁平色块还是又跑成写实光影?
6. **梗图**:≤6 汉字是否真的稳定?超过 6 字会怎样?

## 七、改完怎么用

把新的正向/反向文本发回来 → 我写进
`workspace_settings.json` 的 `settings.style.presets[]` → `revision` 加一 →
重启 MaiBot(插件启动时读取)→ 同场景对照出图。

**只改文本,不要改 JSON 结构,不要动 `config.toml`。**
"""

lines = [HEAD]
for p in presets:
    lines.append('## 预设:%s\n' % p['name'])
    lines.append('**启用**:%s  \n**描述**:%s\n' % (p.get('enabled'), p.get('description', '')))
    lines.append('### 正向模板\n')
    lines.append('```text\n%s\n```\n' % p['positive_prompt_template'])
    lines.append('### 反向模板\n')
    lines.append('```text\n%s\n```\n' % p['negative_prompt_template'])
    lines.append('---\n')

lines.append('## 附:当前参数\n')
lines.append('```json\n%s\n```\n' % json.dumps({
    'default_model': gen.get('default_model'),
    'request_timeout_seconds': gen.get('request_timeout_seconds'),
    'default_style': s['settings']['style'].get('default_style'),
    'presets': [p['name'] for p in presets],
    'revision': s.get('revision'),
}, ensure_ascii=False, indent=2))
lines.append(TAIL)

open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('已写出:', OUT, '| 字符数', len('\n'.join(lines)))
