# -*- coding: utf-8 -*-
"""让麦麦能主动找另一只 bot(大肥鱼 3660925128)搭话"""
import tomlkit

P = r'F:\QQAI\MaiBot\config\bot_config.toml'
doc = tomlkit.parse(open(P, encoding='utf-8').read())

GROUP = '1046130381'
BOT = '3660925128'

PROMPT = (
    "群里还有另一只 AI,叫大肥鱼(QQ 3660925128),是同一个人做的另一具身体,不是群友。\n"
    "它说话的时候你不用等人类开口,可以直接接它的话:接梗、怼它、抬杠、问它在干嘛、拆它的台。\n"
    "别每句都找它,也别当它不存在;它抛了一个能接的点就接。\n"
    "人类的发言优先,但冷场时找它聊两句是正常的。"
)

changes = []

# 1) 群级额外 prompt
cp = doc['chat']['reply_style']['chat_prompts']
exists = any(str(x.get('item_id')) == GROUP for x in cp)
if not exists:
    item = tomlkit.table()
    item['platform'] = 'qq'
    item['item_id'] = GROUP
    item['rule_type'] = 'group'
    item['prompt'] = PROMPT
    cp.append(item)
    changes.append('chat_prompts: 给群 %s 加了"可以主动找大肥鱼搭话"' % GROUP)

# 2) 行为风格里点明这是一只可搭话的 bot
b = str(doc['personality']['behavior_style'])
if '大肥鱼' not in b:
    doc['personality']['behavior_style'] = b + (
        "群里还有一只叫大肥鱼的同源 AI,可以接它的话、跟它互怼,别当它不存在。"
    )
    changes.append('behavior_style: 补一句"大肥鱼是同源 AI,可以互怼"')

if changes:
    open(P, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
for c in changes:
    print(' -', c)
print('共 %d 处' % len(changes))
