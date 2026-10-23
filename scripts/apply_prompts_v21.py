# -*- coding: utf-8 -*-
"""从 v2.1 文档解析三个预设的正/反向模板,写回插件配置"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MD = r'D:\Downloads\大肥鱼绘图提示词_v2.1.md'
S = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'

text = open(MD, encoding='utf-8').read()

# 按 "## 预设:名字" 切段
parts = re.split(r'^## 预设[:：](.+?)\s*$', text, flags=re.M)
print('切出的段数:', (len(parts) - 1) // 2)

parsed = {}
for i in range(1, len(parts), 2):
    name = parts[i].strip()
    body = parts[i + 1]
    pos = re.search(r'### 正向模板\s*```text\s*(.+?)\s*```', body, re.S)
    neg = re.search(r'### 反向模板\s*```text\s*(.+?)\s*```', body, re.S)
    if not (pos and neg):
        print('  跳过(缺模板):', name)
        continue
    parsed[name] = {'positive': pos.group(1).strip(), 'negative': neg.group(1).strip()}
    print('  %-10s 正向 %d 字 / 反向 %d 字' % (name, len(parsed[name]['positive']), len(parsed[name]['negative'])))

s = json.load(open(S, encoding='utf-8'))
presets = s['settings']['style']['presets']
for p in presets:
    n = p['name']
    if n in parsed:
        p['positive_prompt_template'] = parsed[n]['positive']
        p['negative_prompt_template'] = parsed[n]['negative']
        print('~ 已更新:', n)
    else:
        print('! 文档里没有:', n)

s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(S, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('revision ->', s['revision'])
