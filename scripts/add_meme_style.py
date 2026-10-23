# -*- coding: utf-8 -*-
"""新增「大肥鱼梗图」预设:自带手绘气泡 + 中文大字"""
import io
import json
import sys
import tomlkit

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SP = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'
BP = r'F:\QQAI\MaiBot\config\bot_config.toml'

POSITIVE = (
    "{prompt}，"
    "【角色:严格遵循 DeepSeek 鲸鱼娘固定设定】"
    "Q版二头身幼儿体型（头身比约 1:2~1:2.5），圆脸、短手短脚，体型不可改；"
    "深蓝到浅蓝渐变超长波浪长发，发丝厚块面带块状高光，头顶鲸鱼尾呆毛；"
    "鲸鱼鳍耳（白荷叶边、蓝蝴蝶结）；蓝色渐变大眼；"
    "深藏青女仆装 + 白荷叶边围裙（鲸鱼刺绣）+ 蓝宝石胸针 + 鲸鱼尾巴 + 白袜玛丽珍鞋；"
    "【梗图构图】"
    "夸张情绪表情（大喊、崩溃、无语、得意、心虚选一），肢体动作有动感；"
    "画面中有手绘对话气泡或爆炸框，气泡里用粗黑体中文写清指定文字，"
    "文字居中排版、笔画完整、不要错字、不要英文乱码、不要重复；"
    "【画风】"
    "日系卡哇伊梗图风，粗深藏青描边，赛璐璐上色，硬边两到三个色阶，"
    "纯白背景，配手绘装饰（汗滴、爱心、星星、速度线、闪光）；"
    "角色居中，明确要求多个角色时按数量画同一个角色"
)

NEGATIVE = (
    "错别字，乱码，英文乱码，繁体字，多余文字，文字重复，文字变形，文字被裁切，"
    "厚涂，油画，写实，照片感，3D渲染，CG感，真实光影，无描边，极细线，模糊边缘，"
    "成熟体型，成人化，性感化，长腿，高挑，细腰，巨乳，暴露，短裙，写实比例，"
    "复杂背景，场景细节过多，红眼，金发，短发，人类耳朵，无尾巴，"
    "水印，署名，logo，畸形手指，多余肢体"
)

PRESET = {
    "enabled": True,
    "name": "大肥鱼梗图",
    "description": "鲸鱼娘梗图:夸张表情 + 手绘气泡写中文大字,同款卡哇伊画风",
    "positive_prompt_template": POSITIVE,
    "negative_prompt_template": NEGATIVE,
}

s = json.load(open(SP, encoding='utf-8'))
presets = s['settings']['style']['presets']
names = [p.get('name') for p in presets]
if '大肥鱼梗图' in names:
    presets[names.index('大肥鱼梗图')].update(PRESET)
    print('~ 已更新「大肥鱼梗图」')
else:
    presets.append(PRESET)
    print('+ 已新增「大肥鱼梗图」')
s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('预设列表:', [p['name'] for p in presets])

RULE = (
    "有人要「梗图」「表情包」「带字的图」时,用风格预设「大肥鱼梗图」,"
    "并把它要写的那句话原样放进提示词里,写法是:气泡文字：那句话。"
    "只要普通插画或立绘时用「大肥鱼」。"
)

doc = tomlkit.parse(open(BP, encoding='utf-8').read())
b = str(doc['personality']['behavior_style'])
if '大肥鱼梗图' not in b:
    doc['personality']['behavior_style'] = b + RULE
    print('~ behavior_style 追加梗图规则')
open(BP, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('完成')
