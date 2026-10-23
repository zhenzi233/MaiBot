# -*- coding: utf-8 -*-
"""让麦麦更主动:放宽回复门槛、关掉长退避、开启联想漂移"""
import tomlkit

P = r'F:\QQAI\MaiBot\config\bot_config.toml'
doc = tomlkit.parse(open(P, encoding='utf-8').read())
changes = []

# 1) 群聊提示词:从"别硬回"改成"有话题就接、冷场可以抛"
old_prompt = doc['chat']['reply_style']['group_chat_prompt'] if 'reply_style' in doc['chat'] else None
new_prompt = (
    "下面是聊天中的内容,聊天中包含文字、图片和表情包等消息。\n"
    "回复尽量简短一些(一到两句),一次针对一个话题,但要看不同群友之间在聊什么,别啰嗦。\n"
    "群里有话题、有梗、有人吐槽、有人问问题,都可以接;没人在说话或者冷场的时候,可以自己抛一句。\n"
    "不用每条都回,但要主动参与,不要习惯性沉默。\n"
    "可以适当发送表情包表达情绪。有人明显不想理你,再收。\n"
)
if old_prompt != new_prompt:
    doc['chat']['reply_style']['group_chat_prompt'] = new_prompt
    changes.append('group_chat_prompt: 放宽(允许主动接话/冷场抛话题)')

rt = doc['chat']['reply_timing']

# 2) 提到名字更容易回
if not rt['mentioned_bot_reply']:
    rt['mentioned_bot_reply'] = True
    changes.append('mentioned_bot_reply: false -> true')

# 3) 连续不回复的退避:别一沉默就歇 5 分钟
if int(rt['no_action_backoff_start_count']) < 5:
    changes.append('no_action_backoff_start_count: %s -> 5' % rt['no_action_backoff_start_count'])
    rt['no_action_backoff_start_count'] = 5
if float(rt['no_action_backoff_base_seconds']) > 8:
    changes.append('no_action_backoff_base_seconds: %s -> 8.0' % rt['no_action_backoff_base_seconds'])
    rt['no_action_backoff_base_seconds'] = 8.0
if float(rt['no_action_backoff_cap_seconds']) > 120:
    changes.append('no_action_backoff_cap_seconds: %s -> 120.0' % rt['no_action_backoff_cap_seconds'])
    rt['no_action_backoff_cap_seconds'] = 120.0

# 4) 注意力漂移:更容易被有趣话题带走
ad = doc['experimental']['attention_drift']
if not ad['enabled']:
    ad['enabled'] = True
    changes.append('attention_drift.enabled: false -> true')
if ad['drift_level'] != 'active':
    changes.append('attention_drift.drift_level: %s -> active' % ad['drift_level'])
    ad['drift_level'] = 'active'

# 5) 人格的行为风格:把"安静潜水"改成"有话题就接"
p = doc['personality']['behavior_style']
old_b = str(p)
new_b = (
    "群里有话题、有梗、有人吐槽或提问,都可以接;没人在说话时可以自己抛一句,不要习惯性沉默。"
    "先判断这句话指向谁:别人在互相怼、没叫你,就别抢话。"
    "被 @ 或提到小鲸鱼/DeepSeek 必回。"
    "想潜水就安静不回,不要写括号内心戏。"
    "被叫「大肥鱼」会炸毛反击,但别每条都提。"
    "允许装傻、已读乱回、给离谱答案,不要有求必应。"
)
if old_b != new_b:
    doc['personality']['behavior_style'] = new_b
    changes.append('behavior_style: 去掉"安静潜水",改成"有话题就接/冷场可抛"')

if changes:
    open(P, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
for c in changes:
    print(' -', c)
print('共 %d 处改动' % len(changes))
