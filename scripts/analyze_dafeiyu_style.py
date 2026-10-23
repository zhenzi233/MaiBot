# -*- coding: utf-8 -*-
"""从 SnowLuma 消息库提取大肥鱼在卡比群的全部发言并统计风格"""
import collections
import io
import json
import os
import re
import sqlite3
import statistics
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB = r'F:\QQAI\SnowLuma-v2.0.3-win-x64\data\3660925128\messages.db'
GROUP = 1046130381
BOT = 3660925128
OUT_JSON = r'F:\QQAI\大肥鱼记忆导出\大肥鱼发言_卡比群.json'

con = sqlite3.connect('file:%s?mode=ro' % DB, uri=True)
rows = con.execute('SELECT timestamp, data FROM messages WHERE session_id=? ORDER BY timestamp', (GROUP,)).fetchall()
print('该群消息总数:', len(rows))

texts = []
for ts, raw in rows:
    try:
        d = json.loads(raw)
    except Exception:
        continue
    if int(d.get('user_id') or 0) != BOT:
        continue
    parts = []
    for c in d.get('message') or []:
        t = c.get('type')
        if t == 'text':
            parts.append(str(c.get('data', {}).get('text', '')))
        elif t in ('image', 'mface'):
            parts.append('[图]')
        elif t == 'face':
            parts.append('[表情]')
        elif t == 'at':
            parts.append('@')
    s = ''.join(parts).strip()
    if s:
        texts.append(s)

print('大肥鱼发言:', len(texts))
if texts:
    lens = [len(t) for t in texts]
    print('字数 中位 %d / 平均 %.1f / 最长 %d' % (statistics.median(lens), sum(lens) / len(lens), max(lens)))
    for th in (5, 10, 15, 20, 30):
        print('  <=%2d 字: %5.1f%%' % (th, sum(1 for l in lens if l <= th) * 100 / len(lens)))
    def pct(pred):
        return sum(1 for t in texts if pred(t)) * 100 / len(texts)
    print('问号 %.1f%% | 感叹号 %.1f%% | 逗号 %.1f%% | 句号 %.1f%% | [图] %.1f%% | [表情] %.1f%%' % (
        pct(lambda t: '?' in t or '？' in t), pct(lambda t: '!' in t or '！' in t),
        pct(lambda t: '，' in t), pct(lambda t: '。' in t),
        pct(lambda t: '[图]' in t), pct(lambda t: '[表情]' in t)))
    print('\n高频开头:')
    for k, v in collections.Counter(t[:2] for t in texts if len(t) > 1).most_common(8):
        print('   %-4s %d' % (k, v))
    print('高频结尾:')
    for k, v in collections.Counter(t[-2:] for t in texts if len(t) > 1).most_common(8):
        print('   %-4s %d' % (k, v))
    print('\n高频词片段:')
    txt = ''.join(texts)
    for k, v in collections.Counter(re.findall(r'[\u4e00-\u9fa5]{2}', txt)).most_common(20):
        print('   %-4s %d' % (k, v), end='')
    print()
    print('\n样例(每 15 条取 1):')
    for t in texts[::max(1, len(texts) // 25)][:25]:
        print('   ', t[:70])

os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
json.dump(texts, open(OUT_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n已保存:', OUT_JSON)
