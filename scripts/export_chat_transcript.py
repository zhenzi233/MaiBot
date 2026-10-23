# -*- coding: utf-8 -*-
"""把 AstrBot 卡比狼人杀二号的聊天记录导出成「可导入记忆系统」的对话转录文件"""
import io
import os
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SL = r'F:\甄舜杰\AIWORK\AstrBot\data\plugin_data\astrbot_plugin_self_learning\messages.db'
GROUP = '1046130381'
OUT = r'F:\QQAI\卡比狼人杀二号_聊天转录.txt'

BAD = ('UMO:', '使用说明')

con = sqlite3.connect('file:%s?mode=ro' % SL, uri=True)

rows = []
for ts, name, text in con.execute(
        'SELECT timestamp, sender_name, message FROM raw_messages WHERE group_id=? ORDER BY timestamp', (GROUP,)):
    if not text or any(b in text for b in BAD):
        continue
    rows.append((float(ts), (name or '群友').strip(), text.strip().replace('\n', ' ')[:400]))

bots = []
for ts, text in con.execute(
        'SELECT timestamp, message FROM bot_messages WHERE group_id=? ORDER BY timestamp', (GROUP,)):
    if not text or any(b in text for b in BAD):
        continue
    bots.append((float(ts), '小鲸鱼(机器人)', text.strip().replace('\n', ' ')[:400]))

allrows = sorted(rows + bots, key=lambda x: x[0])
print('群消息 %d 条,机器人发言 %d 条,合计 %d' % (len(rows), len(bots), len(allrows)))

import datetime
lines = ['# 卡比狼人杀二号 群聊记录(2026 年 10 月)', '',
         '> 这是一个 QQ 群的真实聊天记录。小鲸鱼是群里的 AI 角色。', '']
day = None
for ts, name, text in allrows:
    dt = datetime.datetime.fromtimestamp(ts)
    d = dt.strftime('%Y-%m-%d')
    if d != day:
        lines.append('')
        lines.append('## %s' % d)
        day = d
    lines.append('[%s] %s: %s' % (dt.strftime('%H:%M'), name, text))

open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('写出:', OUT, os.path.getsize(OUT), 'bytes')
con.close()
