# -*- coding: utf-8 -*-
"""接入 SiliconFlow bge-m3 作为嵌入模型,解锁 A-Memorix 语义召回"""
import os
import tomlkit

MP = r'F:\QQAI\MaiBot\config\model_config.toml'
BP = r'F:\QQAI\MaiBot\config\bot_config.toml'
KEY = os.environ.get('SILICONFLOW_KEY', '').strip()
if not KEY:
    raise SystemExit('缺少环境变量 SILICONFLOW_KEY')

doc = tomlkit.parse(open(MP, encoding='utf-8').read())

providers = doc['api_providers']
if not any(str(p.get('name')) == 'SiliconFlow' for p in providers):
    p = tomlkit.table()
    p['name'] = 'SiliconFlow'
    p['base_url'] = 'https://api.siliconflow.cn/v1'
    p['api_key'] = KEY
    p['client_type'] = 'openai'
    p['auth_type'] = 'bearer'
    p['auth_header_name'] = 'Authorization'
    p['auth_header_prefix'] = 'Bearer'
    p['model_list_endpoint'] = '/models'
    p['reasoning_parse_mode'] = 'auto'
    providers.append(p)
    print('+ 服务商 SiliconFlow')
else:
    print('= 服务商已存在')

models = doc['models']
if not any(str(m.get('name')) == 'bge-m3' for m in models):
    m = tomlkit.table()
    m['model_type'] = 'embedding'
    m['model_identifier'] = 'BAAI/bge-m3'
    m['name'] = 'bge-m3'
    m['api_provider'] = 'SiliconFlow'
    m['price_in'] = 0.0
    m['cache_price_in'] = 0.0
    m['price_out'] = 0.0
    m['send_temperature'] = False
    m['force_stream_mode'] = False
    m['visual'] = False
    models.append(m)
    print('+ 模型 bge-m3 (embedding, 1024 维)')
else:
    print('= 模型已存在')

open(MP, 'w', encoding='utf-8').write(tomlkit.dumps(doc))

# A-Memorix 指向它
b = tomlkit.parse(open(BP, encoding='utf-8').read())
emb = b['a_memorix']['embedding']
old = str(emb['model_name'])
emb['model_name'] = 'bge-m3'
if int(emb['dimension']) != 1024:
    print('~ dimension: %s -> 1024' % emb['dimension'])
    emb['dimension'] = 1024
print('~ a_memorix.embedding.model_name: %s -> bge-m3' % old)

# 图片记忆没有对应模型,先关掉避免空转
im = b['a_memorix']['image_memory']
if im.get('enabled'):
    im['enabled'] = False
    print('~ a_memorix.image_memory.enabled: true -> false(没有 image_embedding 模型)')

open(BP, 'w', encoding='utf-8').write(tomlkit.dumps(b))
print('完成')
