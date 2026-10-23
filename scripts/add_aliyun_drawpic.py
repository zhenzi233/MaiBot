# -*- coding: utf-8 -*-
"""把阿里百炼(通义万相/qwen-image)加成第二个绘图平台,并设为默认"""
import io
import json
import os
import sys
import uuid

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin'
KEY = os.environ.get('QWEN_KEY', '').strip()
if not KEY:
    raise SystemExit('缺少 QWEN_KEY')

MODELS = ['qwen-image-3.0-pro', 'qwen-image-3.0', 'qwen-image-2.1-pro', 'z-image-turbo']

# 1) 平台
p = os.path.join(DATA, 'platforms.json')
payload = json.load(open(p, encoding='utf-8'))
rec = {
    'id': uuid.uuid4().hex,
    'kind': 'aliyun',
    'name': '阿里百炼',
    'config': {
        'enabled': True,
        'base_url': 'https://dashscope.aliyuncs.com/api/v1',
        'api_key': KEY,
        'models': MODELS,
        'size': '1024*1024',
    },
}
cur = [x for x in payload.get('providers', []) if x.get('kind') == 'aliyun']
if cur:
    cur[0]['config'].update(rec['config'])
    print('阿里百炼平台已存在,更新配置')
else:
    payload.setdefault('providers', []).append(rec)
    print('新增阿里百炼平台 id=', rec['id'])
payload['revision'] = int(payload.get('revision', 1)) + 1
json.dump(payload, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('平台总数', len(payload['providers']), '| revision', payload['revision'])

# 2) 默认模型切到阿里百炼的图像模型
sp = os.path.join(DATA, 'workspace_settings.json')
s = json.load(open(sp, encoding='utf-8'))
g = s.setdefault('settings', {}).setdefault('general', {})
old = g.get('default_model', '')
g['default_model'] = '阿里百炼/qwen-image-3.0-pro'
s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('default_model: %r -> %r' % (old, g['default_model']))
