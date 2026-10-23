# -*- coding: utf-8 -*-
"""导出大肥鱼(bridge/DSH)的会话记忆:聊天记录 + 话题 + 待说 + 成员印象"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SRC = r'F:\zsj\qq-bot\state\social-v2.json'
OUT_DIR = r'F:\QQAI\大肥鱼记忆导出'
NAME = {
    'private:1994577746': '私聊_榛子',
    'group:1046130381': '卡比狼人杀二号',
    'group:745674166': '小志的Minecraft交流群',
}

os.makedirs(OUT_DIR, exist_ok=True)
d = json.load(open(SRC, encoding='utf-8'))
convs = d.get('conversations') or {}

summary = []
transcripts = {}

for key, conv in convs.items():
    label = NAME.get(key, key.replace(':', '_'))
    msgs = conv.get('recentMessages') or []
    lines = []
    for m in msgs:
        role = m.get('role') or m.get('sender') or '?'
        text = m.get('text') or m.get('content') or ''
        if isinstance(text, list):
            text = ' '.join(str(x.get('text', x)) if isinstance(x, dict) else str(x) for x in text)
        text = str(text).strip().replace('\n', ' ')
        if not text:
            continue
        who = '大肥鱼' if role in ('assistant', 'bot', 'ai') else '群友'
        lines.append('%s: %s' % (who, text[:400]))

    topics = conv.get('activeTopics') or []
    thoughts = conv.get('pendingThoughts') or []
    impressions = conv.get('memberImpressions') or {}

    md = ['# %s 记忆导出\n' % label, '> 来源:qq-bridge social-v2.json\n']
    md.append('## 统计\n')
    md.append('- 最近消息:%d 条\n- 活跃话题:%d 个\n- 待说想法:%d 条\n- 成员印象:%d 人\n' % (
        len(lines), len(topics), len(thoughts), len(impressions)))
    if topics:
        md.append('\n## 活跃话题\n')
        for t in topics:
            md.append('- %s\n' % (t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)[:200]))
    if thoughts:
        md.append('\n## 想说还没说的\n')
        for t in thoughts:
            md.append('- %s\n' % (t if isinstance(t, str) else json.dumps(t, ensure_ascii=False)[:200]))
    if impressions:
        md.append('\n## 成员印象\n')
        for who, imp in impressions.items():
            md.append('- **%s**:%s\n' % (who, imp if isinstance(imp, str) else json.dumps(imp, ensure_ascii=False)[:200]))
    md.append('\n## 最近对话\n\n```text\n%s\n```\n' % ('\n'.join(lines) if lines else '(无)'))

    path = os.path.join(OUT_DIR, '%s.md' % label)
    open(path, 'w', encoding='utf-8').write(''.join(md))
    transcripts[key] = {'label': label, 'lines': lines}
    summary.append((label, len(lines), len(topics), len(thoughts), len(impressions)))
    print('导出 %-24s 消息 %3d | 话题 %d | 待说 %d | 印象 %d' % (label, len(lines), len(topics), len(thoughts), len(impressions)))

# 供导入用的转录文件(合并三个会话,带会话标题)
for key, info in transcripts.items():
    if not info['lines']:
        continue
    fn = os.path.join(OUT_DIR, '转录_%s.txt' % info['label'])
    open(fn, 'w', encoding='utf-8').write(
        '# %s 聊天记录\n\n%s\n' % (info['label'], '\n'.join(info['lines']))
    )
    print('  转录:', os.path.basename(fn), len(info['lines']), '条')

json.dump(transcripts, open(os.path.join(OUT_DIR, '原始.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n输出目录:', OUT_DIR)
