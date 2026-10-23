# -*- coding: utf-8 -*-
"""翻页抓取卡比群历史,提取大肥鱼(3660925128)的全部发言"""
import io
import json
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOK = json.load(open(r'F:\QQAI\SnowLuma-v2.0.3-win-x64\config\onebot_3660925128.json',
                     encoding='utf-8-sig'))['networks']['httpServers'][0]['accessToken']
GROUP = 1046130381
BOT = 3660925128
PAGES = 12


def fetch(seq=None):
    body = {'group_id': GROUP, 'count': 200}
    if seq:
        body['message_seq'] = seq
    req = urllib.request.Request(
        'http://127.0.0.1:3101/get_group_msg_history',
        data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + TOK, 'Content-Type': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def text_of(m):
    out = []
    for c in m.get('message', []):
        t = c.get('type')
        if t == 'text':
            out.append(str(c.get('data', {}).get('text', '')))
        elif t == 'image':
            out.append('[图]')
        elif t == 'face':
            out.append('[表情]')
        elif t == 'mface':
            out.append('[表情包]')
    return ''.join(out).strip()


all_msgs = {}
seq = None
for i in range(PAGES):
    try:
        d = fetch(seq)
    except Exception as e:
        print('第 %d 页失败: %s' % (i + 1, str(e)[:60]))
        break
    msgs = (d.get('data') or {}).get('messages') or []
    if not msgs:
        print('第 %d 页为空,停止' % (i + 1))
        break
    for m in msgs:
        all_msgs[m.get('message_seq')] = m
    oldest = min(m.get('message_seq') for m in msgs)
    print('第 %d 页 %d 条,seq %s~%s' % (i + 1, len(msgs),
          min(m.get('message_seq') for m in msgs), max(m.get('message_seq') for m in msgs)))
    if oldest == seq:
        break
    seq = oldest

msgs = sorted(all_msgs.values(), key=lambda m: m.get('message_seq') or 0)
bot = [m for m in msgs if m.get('user_id') == BOT]
print('\n总消息 %d 条 | 大肥鱼 %d 条' % (len(msgs), len(bot)))

rows = []
for m in bot:
    t = text_of(m)
    if t:
        rows.append({'time': m.get('time'), 'text': t})

json.dump(rows, open(r'F:\QQAI\大肥鱼记忆导出\大肥鱼发言.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
json.dump(msgs, open(r'F:\QQAI\大肥鱼记忆导出\群历史_卡比_全量.json', 'w', encoding='utf-8'),
          ensure_ascii=False)
print('已保存 %d 条大肥鱼发言' % len(rows))
for r in rows[:6]:
    print('  ', r['text'][:60])
