# -*- coding: utf-8 -*-
"""把「画大肥鱼时用风格预设」写进人设与聊天提示词"""
import io
import sys
import tomlkit

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'F:\QQAI\MaiBot\config\bot_config.toml'

RULE_PLANNER = "有人让你画「大肥鱼」「鲸鱼娘」「小鲸鱼」的图时,调用绘图工具并把 style 参数填「大肥鱼」,这样人设才统一;画别的主题不要带这个风格。"
RULE_CHAT = "让你画大肥鱼/鲸鱼娘时,记得用绘图工具并带上风格「大肥鱼」,画别的东西不要带。"

doc = tomlkit.parse(open(P, encoding='utf-8').read())

# 1) 行为风格(Planner 看)
b = str(doc['personality']['behavior_style'])
if '风格' not in b or '大肥鱼' not in b:
    doc['personality']['behavior_style'] = b + RULE_PLANNER
    print('~ behavior_style 已追加绘图规则')

# 2) 群聊提示词
rs = doc['chat']['reply_style']
gp = str(rs['group_chat_prompt'])
if 'style' not in gp:
    rs['group_chat_prompt'] = gp + RULE_CHAT + '\n'
    print('~ group_chat_prompt 已追加绘图规则')

# 3) 私聊提示词
pp = str(rs['private_chat_prompts'])
if 'style' not in pp:
    rs['private_chat_prompts'] = pp + RULE_CHAT + '\n'
    print('~ private_chat_prompts 已追加绘图规则')

open(P, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('已保存')
