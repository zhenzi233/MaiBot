# -*- coding: utf-8 -*-
"""给绘图插件加一个「大肥鱼」风格预设(用文本锁定人设,插件原生支持)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SP = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'

POSITIVE = (
    "{prompt}，"
    "Q版三头身少女，鲸鱼娘，深蓝到浅蓝渐变的超长波浪长发，发梢浅蓝色半透明，"
    "头顶一根鲸鱼尾状的呆毛，"
    "鲸鱼鳍形状的耳朵，鳍边缘是白色荷叶边，耳侧系蓝色蝴蝶结，"
    "大而圆的蓝色渐变眼睛带高光和腮红，圆脸，开心表情，"
    "深藏青色女仆装，白色荷叶边围裙，围裙中央有一只小鲸鱼刺绣，"
    "领口蓝色宝石胸针配白色蝴蝶结，裙摆有金色 X 形缝线，"
    "身后一条深蓝色鲸鱼尾巴带尾鳍，"
    "白色荷叶边小腿袜，深蓝色玛丽珍小皮鞋，"
    "干净白色背景，日系厚涂，柔和打光，色彩清爽，高细节"
)

NEGATIVE = (
    "模糊，低分辨率，水印，文字，签名，logo，多个角色，"
    "写实风格，3D 渲染，噪点，畸形手指，多余肢体，"
    "红眼，金发，短发，人类耳朵"
)

preset = {
    "enabled": True,
    "name": "大肥鱼",
    "description": "DeepSeek 鲸鱼娘的固定人设:蓝长发、鲸鱼鳍耳、深蓝女仆装、鲸鱼尾巴",
    "positive_prompt_template": POSITIVE,
    "negative_prompt_template": NEGATIVE,
}

s = json.load(open(SP, encoding='utf-8'))
style = s.setdefault('settings', {}).setdefault('style', {})
presets = style.setdefault('presets', [])

names = [p.get('name') for p in presets]
if '大肥鱼' in names:
    idx = names.index('大肥鱼')
    presets[idx].update(preset)
    print('已更新「大肥鱼」预设')
else:
    presets.append(preset)
    print('已新增「大肥鱼」预设')

s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('风格数:', len(presets), '| 名称:', [p.get('name') for p in presets])
print('default_style:', style.get('default_style'))
