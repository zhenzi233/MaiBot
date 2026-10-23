# -*- coding: utf-8 -*-
"""按插件自己的 JSON 结构配置硅基流动平台(config.toml 里不能放平台节)"""
import io
import json
import os
import shutil
import sys
import uuid

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PLUG = r'F:\QQAI\MaiBot\plugins\maimai-drawpic-plugin'
DATA = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin'
KEY = os.environ.get('SILICONFLOW_KEY', '').strip()
if not KEY:
    raise SystemExit('缺少 SILICONFLOW_KEY')

# 1) 把 config.toml 还原(去掉我加的 [siliconflow] 节)
bak = os.path.join(PLUG, 'config.toml.bak')
cfg = os.path.join(PLUG, 'config.toml')
if os.path.isfile(bak):
    shutil.copy2(bak, cfg)
    print('config.toml 已还原')

# 2) 写 platforms.json
path = os.path.join(DATA, 'platforms.json')
payload = json.load(open(path, encoding='utf-8'))

rec = {
    'id': uuid.uuid4().hex,
    'kind': 'siliconflow',
    'name': '硅基流动',
    'config': {
        'enabled': True,
        'api_key': KEY,
        'models': ['Qwen/Qwen-Image', 'Kwai-Kolors/Kolors', 'Tongyi-MAI/Z-Image-Turbo'],
        'image_size': '1024x1024',
        'cfg': 4.0,
        'num_inference_steps': 20,
    },
}
existing = [p for p in payload.get('providers', []) if p.get('kind') == 'siliconflow']
if existing:
    existing[0]['config'].update(rec['config'])
    print('已有硅基流动平台,已更新配置')
else:
    payload.setdefault('providers', []).append(rec)
    print('新增硅基流动平台,id=', rec['id'])

payload['revision'] = int(payload.get('revision', 1)) + 1
json.dump(payload, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('platforms.json 已写入,revision=', payload['revision'], '| 平台数=', len(payload['providers']))
