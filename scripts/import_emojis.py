# -*- coding: utf-8 -*-
"""把 AstrBot 导出的表情包批量导入 MaiBot(按分类打 emotion 标签)"""
import csv
import json
import os
import sys
import httpx
import tomlkit

BOTCFG = r'F:\QQAI\MaiBot\config\bot_config.toml'
WEBUI = r'F:\QQAI\MaiBot\data\webui.json'
EXPORT = r'F:\甄舜杰\AIWORK\表情包导出'
FLAT = os.path.join(EXPORT, '02_已入库_扁平')
MANIFEST = os.path.join(EXPORT, '清单_已入库.csv')
BASE = 'http://127.0.0.1:8001'

# ---------- 1. 提高上限 ----------
doc = tomlkit.parse(open(BOTCFG, encoding='utf-8').read())
old = doc['emoji']['max_reg_num']
if int(old) < 400:
    doc['emoji']['max_reg_num'] = 400
    open(BOTCFG, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
    print('max_reg_num: %s -> 400' % old)
else:
    print('max_reg_num 已是 %s,无需调整' % old)

# ---------- 2. 读取清单 ----------
rows = list(csv.DictReader(open(MANIFEST, encoding='utf-8-sig')))
by_cat = {}
for r in rows:
    fn = r['文件名']
    p = os.path.join(FLAT, fn)
    if not os.path.isfile(p):
        continue
    by_cat.setdefault(r['中文分类'], []).append(p)
print('待导入 %d 张,分 %d 类' % (sum(len(v) for v in by_cat.values()), len(by_cat)))

tok = json.load(open(WEBUI, encoding='utf-8'))['access_token']
headers = {'Cookie': 'maibot_session=%s' % tok}

# ---------- 3. 分批上传 ----------
total_ok = total_fail = 0
fail_detail = []
with httpx.Client(timeout=120.0, headers=headers) as client:
    for cat, files in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        ok = fail = 0
        for i in range(0, len(files), 20):
            chunk = files[i:i + 20]
            multipart = []
            handles = []
            try:
                for p in chunk:
                    fh = open(p, 'rb')
                    handles.append(fh)
                    ext = os.path.splitext(p)[1].lower()
                    mime = {'.gif': 'image/gif', '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg', '.png': 'image/png',
                            '.webp': 'image/webp'}.get(ext, 'image/png')
                    multipart.append(('files', (os.path.basename(p), fh, mime)))
                resp = client.post(BASE + '/api/webui/emoji/batch/upload',
                                   files=multipart,
                                   data={'emotion': cat, 'is_registered': 'true'})
                if resp.status_code != 200:
                    fail += len(chunk)
                    fail_detail.append((cat, 'HTTP %s' % resp.status_code, resp.text[:120]))
                else:
                    j = resp.json()
                    ok += int(j.get('uploaded', 0))
                    fail += int(j.get('failed', 0))
                    for d in (j.get('details') or []):
                        if not d.get('success'):
                            fail_detail.append((cat, d.get('filename'), d.get('error')))
            finally:
                for fh in handles:
                    fh.close()
        total_ok += ok
        total_fail += fail
        print('  %-6s %3d 张 -> 成功 %3d 失败 %3d' % (cat, len(files), ok, fail))

print('\n合计: 成功 %d,失败 %d' % (total_ok, total_fail))
if fail_detail:
    print('失败样例:')
    for item in fail_detail[:8]:
        print('  ', item)
