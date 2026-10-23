# -*- coding: utf-8 -*-
"""按 sha256 把迁移包里的描述 + 标签回填到 MaiBot 表情库"""
import csv
import hashlib
import json
import os
import httpx

EXPORT = r'F:\甄舜杰\AIWORK\表情包导出'
FLAT = os.path.join(EXPORT, '02_已入库_扁平')
MANIFEST = os.path.join(EXPORT, '清单_已入库.csv')
WEBUI = r'F:\QQAI\MaiBot\data\webui.json'
BASE = 'http://127.0.0.1:8001'

tok = json.load(open(WEBUI, encoding='utf-8'))['access_token']
headers = {'Cookie': 'maibot_session=%s' % tok}

# 1) 文件 -> 描述
hash2desc = {}
rows = list(csv.DictReader(open(MANIFEST, encoding='utf-8-sig')))
for r in rows:
    p = os.path.join(FLAT, r['文件名'])
    if not os.path.isfile(p):
        continue
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    desc = (r.get('描述') or '').strip()
    tags = (r.get('标签') or '').strip()
    if desc and tags:
        text = '%s（%s）' % (desc, tags)
    else:
        text = desc or tags
    if text:
        hash2desc[h] = text[:300]
print('清单里可用于回填的:', len(hash2desc))

# 2) 拉全量表情
items = []
page = 1
with httpx.Client(timeout=60.0, headers=headers) as c:
    while True:
        r = c.get(BASE + '/api/webui/emoji/list', params={'page': page, 'page_size': 100})
        r.raise_for_status()
        j = r.json()
        items.extend(j.get('data') or [])
        if len(items) >= int(j.get('total') or 0) or not j.get('data'):
            break
        page += 1
print('表情库总数:', len(items))

# 3) 逐个 PATCH
ok = miss = fail = 0
fail_samples = []
with httpx.Client(timeout=60.0, headers=headers) as c:
    for it in items:
        h = str(it.get('emoji_hash') or os.path.basename(str(it.get('full_path') or '')).split('.')[0])
        desc = hash2desc.get(h)
        if not desc:
            miss += 1
            continue
        try:
            rr = c.patch(BASE + '/api/webui/emoji/%s' % it['id'], json={'description': desc})
            if rr.status_code == 200:
                ok += 1
            else:
                fail += 1
                if len(fail_samples) < 5:
                    fail_samples.append((it['id'], rr.status_code, rr.text[:100]))
        except Exception as e:
            fail += 1
            if len(fail_samples) < 5:
                fail_samples.append((it['id'], 'exc', str(e)[:100]))

print('回填成功 %d | 无匹配 %d | 失败 %d' % (ok, miss, fail))
for s in fail_samples:
    print('  失败样例:', s)
