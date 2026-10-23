# -*- coding: utf-8 -*-
"""只保留小鲸鱼时代的聊天记录(剔除 baka/琪露诺时代的内容)"""
import datetime
import io
import os
import sqlite3
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SL = r'F:\甄舜杰\AIWORK\AstrBot\data\plugin_data\astrbot_plugin_self_learning\messages.db'
GROUP = '1046130381'
OUT = r'F:\QQAI\卡比狼人杀二号_聊天转录_小鲸鱼时代.txt'

# baka/琪露诺 时代标记
BAKA = ('本小姐', '⑨', '琪露诺', '冰之妖精', '雾之湖', '幻想乡', '冻青蛙', '大妖精', '妖精')
SKIP = ('UMO:', '使用说明')


def is_baka(text: str) -> bool:
    return any(k in text for k in BAKA)


con = sqlite3.connect('file:%s?mode=ro' % SL, uri=True)

rows, dropped_h = [], 0
for ts, name, text in con.execute(
        'SELECT timestamp, sender_name, message FROM raw_messages WHERE group_id=? ORDER BY timestamp', (GROUP,)):
    if not text or any(s in text for s in SKIP):
        continue
    if is_baka(text):
        dropped_h += 1
        continue
    rows.append((float(ts), (name or '群友').strip(), text.strip().replace('\n', ' ')[:400]))

bots, dropped_b = [], 0
for ts, text in con.execute(
        'SELECT timestamp, message FROM bot_messages WHERE group_id=? ORDER BY timestamp', (GROUP,)):
    if not text or any(s in text for s in SKIP):
        continue
    if is_baka(text):
        dropped_b += 1
        continue
    bots.append((float(ts), '小鲸鱼(机器人)', text.strip().replace('\n', ' ')[:400]))

allrows = sorted(rows + bots, key=lambda x: x[0])
print('保留 群消息 %d / 机器人 %d = %d 条' % (len(rows), len(bots), len(allrows)))
print('剔除 baka 内容:群友 %d 条,机器人 %d 条' % (dropped_h, dropped_b))

lines = ['# 卡比狼人杀二号 群聊记录(小鲸鱼时代)', '',
         '> QQ 群真实聊天。小鲸鱼是群里的 AI 群友(不是客服)。', '']
day = None
for ts, name, text in allrows:
    dt = datetime.datetime.fromtimestamp(ts)
    d = dt.strftime('%Y-%m-%d')
    if d != day:
        lines += ['', '## %s' % d]
        day = d
    lines.append('[%s] %s: %s' % (dt.strftime('%H:%M'), name, text))

open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('写出:', OUT, os.path.getsize(OUT), 'bytes')
con.close()
