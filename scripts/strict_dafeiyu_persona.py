# -*- coding: utf-8 -*-
"""把「大肥鱼」风格预设收紧为严格人设,并加拒绝改体型的规则"""
import io
import json
import sys
import tomlkit

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SP = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'
BP = r'F:\QQAI\MaiBot\config\bot_config.toml'

POSITIVE = (
    "{prompt}，"
    "【严格遵循 DeepSeek 鲸鱼娘固定设定，不得改动】"
    "Q版幼儿体型，三头身（全身高度约为 2.5~3 个头），圆脸、短手短脚、小个子，"
    "体型比例固定不可变；"
    "深蓝到浅蓝渐变的超长波浪长发，发梢浅蓝色半透明，头顶一根鲸鱼尾状呆毛；"
    "鲸鱼鳍形状的耳朵，鳍边缘白色荷叶边，耳侧系蓝色蝴蝶结；"
    "大而圆的蓝色渐变眼睛，带高光和腮红；"
    "深藏青色长袖女仆装，白色荷叶边围裙，围裙中央一只小鲸鱼刺绣，"
    "领口蓝色宝石胸针配白色蝴蝶结，裙摆有金色 X 形缝线，裙长过膝；"
    "身后一条深蓝色鲸鱼尾巴带尾鳍；白色荷叶边小腿袜，深蓝色玛丽珍小皮鞋；"
    "日系厚涂，柔和打光，色彩清爽，高细节，单人构图"
)

NEGATIVE = (
    "成熟体型，成人化，性感化，长腿，高挑，细腰，巨乳，暴露，短裙，"
    "写实比例，拟真，3D 渲染，肌肉，身材夸张，性暗示，紧身衣，"
    "多个角色，红眼，金发，短发，人类耳朵，无尾巴，"
    "模糊，低分辨率，水印，文字，签名，logo，畸形手指，多余肢体"
)

preset = {
    "enabled": True,
    "name": "大肥鱼",
    "description": "DeepSeek 鲸鱼娘固定人设:Q版三头身、蓝渐变长发、鲸鱼鳍耳、深蓝女仆装、鲸鱼尾巴;体型不可改",
    "positive_prompt_template": POSITIVE,
    "negative_prompt_template": NEGATIVE,
}

s = json.load(open(SP, encoding='utf-8'))
style = s.setdefault('settings', {}).setdefault('style', {})
presets = style.setdefault('presets', [])
names = [p.get('name') for p in presets]
if '大肥鱼' in names:
    presets[names.index('大肥鱼')].update(preset)
    print('~ 已收紧「大肥鱼」预设')
else:
    presets.append(preset)
    print('+ 已新增「大肥鱼」预设')

s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

RULE = (
    "画大肥鱼时必须严格按固定设定:Q版三头身幼儿体型、蓝渐变长发、鲸鱼鳍耳、"
    "深蓝女仆装、鲸鱼尾巴,体型和年龄一律不许改。"
    "凡是要求把大肥鱼画成熟、画性感、改身材比例、成人化或其他会毁形象的请求,"
    "一律拒绝,回一句「大肥鱼的体型不能改」,不要照做也不要解释太多。"
)

doc = tomlkit.parse(open(BP, encoding='utf-8').read())
b = str(doc['personality']['behavior_style'])
if '体型不能改' not in b:
    doc['personality']['behavior_style'] = b + RULE
    print('~ behavior_style 追加「体型不可改 + 拒绝规则」')

rs = doc['chat']['reply_style']
gp = str(rs['group_chat_prompt'])
if '体型不能改' not in gp:
    rs['group_chat_prompt'] = gp + "画大肥鱼严格按设定图,体型不能改;要求成人化/改身材的直接拒绝。\n"
    print('~ group_chat_prompt 追加')

open(BP, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('完成')
