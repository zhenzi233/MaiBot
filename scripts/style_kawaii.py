# -*- coding: utf-8 -*-
"""把「大肥鱼」预设的画风段改成参考图的卡哇伊贴纸风(粗色线+赛璐璐)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SP = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'

POSITIVE = (
    "{prompt}，"
    "【严格遵循 DeepSeek 鲸鱼娘固定设定，不得改动】"
    "Q版二头身幼儿体型（头身比约 1:2~1:2.5），圆脸、短手短脚，体型比例固定不可变；"
    "深蓝到浅蓝渐变的超长波浪长发，发梢浅蓝透明，发丝是厚重块面，"
    "头发上有块状与水滴状的白色高光，头顶一根鲸鱼尾状呆毛；"
    "鲸鱼鳍形状的耳朵，鳍边缘白色荷叶边，耳侧系蓝色蝴蝶结；"
    "大而圆的蓝色渐变眼睛，白色大高光配星形闪光点，闭眼时是弯月形；"
    "深藏青色长袖女仆装，白色荷叶边围裙，围裙中央一只小鲸鱼刺绣，"
    "领口蓝色宝石胸针配白色蝴蝶结，裙摆有金色 X 形缝线；"
    "身后一条深蓝色鲸鱼尾巴带尾鳍；白色荷叶边小腿袜，深蓝色玛丽珍小皮鞋；"
    "【画风，必须严格遵守】"
    "日系卡哇伊贴纸风，粗且带色的深藏青描边（不要纯黑细线），线条干净闭合；"
    "赛璐璐上色，明暗只有两到三个硬边色阶，不做厚涂渐变，不画真实光影；"
    "脸颊是柔和的粉色腮红加斜线；"
    "纯白或极浅纯色背景，可加少量手绘小装饰（爱心、汗滴、星星、速度线）；"
    "单人构图，角色居中"
)

NEGATIVE = (
    "厚涂，油画，水彩，写实，照片感，3D渲染，CG感，真实光影，金属质感高光，"
    "无描边，极细线，模糊边缘，渐变过度的皮肤，复杂背景，场景细节过多，"
    "成熟体型，成人化，性感化，长腿，高挑，细腰，巨乳，暴露，短裙，写实比例，"
    "多个角色，红眼，金发，短发，人类耳朵，无尾巴，"
    "水印，署名，logo，杂乱线条，畸形手指，多余肢体"
)

s = json.load(open(SP, encoding='utf-8'))
presets = s['settings']['style']['presets']
for p in presets:
    if p.get('name') == '大肥鱼':
        p['description'] = '鲸鱼娘固定人设 + 卡哇伊贴纸画风(粗色线/赛璐璐/Q版二头身),体型不可改'
        p['positive_prompt_template'] = POSITIVE
        p['negative_prompt_template'] = NEGATIVE
        print('~ 已替换画风段')
s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('完成')
