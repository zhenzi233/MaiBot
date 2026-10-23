# -*- coding: utf-8 -*-
"""启用图片记忆:接 Qwen3-VL-Embedding-8B(图片→向量)"""
import os
import tomlkit

MP = r'F:\QQAI\MaiBot\config\model_config.toml'
BP = r'F:\QQAI\MaiBot\config\bot_config.toml'
KEY = os.environ.get('SILICONFLOW_KEY', '').strip()
if not KEY:
    raise SystemExit('缺少 SILICONFLOW_KEY')

NAME = 'qwen3-vl-embed'
doc = tomlkit.parse(open(MP, encoding='utf-8').read())

# 服务商(已有就跳过,顺便确保 key 在)
if not any(str(p.get('name')) == 'SiliconFlow' for p in doc['api_providers']):
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
    doc['api_providers'].append(p)
    print('+ 服务商 SiliconFlow')

if not any(str(m.get('name')) == NAME for m in doc['models']):
    m = tomlkit.table()
    m['model_type'] = 'image_embedding'
    m['model_identifier'] = 'Qwen/Qwen3-VL-Embedding-8B'
    m['name'] = NAME
    m['api_provider'] = 'SiliconFlow'
    m['price_in'] = 0.0
    m['cache_price_in'] = 0.0
    m['price_out'] = 0.0
    m['send_temperature'] = False
    m['force_stream_mode'] = False
    m['visual'] = True
    doc['models'].append(m)
    print('+ 模型 %s (image_embedding, 4096 维可截到 1024)' % NAME)

doc['model_task_config']['image_embedding']['model_list'] = [NAME]
print('~ model_task_config.image_embedding -> [%s]' % NAME)
open(MP, 'w', encoding='utf-8').write(tomlkit.dumps(doc))

b = tomlkit.parse(open(BP, encoding='utf-8').read())
im = b['a_memorix']['image_memory']
if not im.get('enabled'):
    im['enabled'] = True
    print('~ a_memorix.image_memory.enabled: false -> true')
im['task_name'] = 'image_embedding'
print('~ image_memory.task_name = image_embedding')
open(BP, 'w', encoding='utf-8').write(tomlkit.dumps(b))
print('完成')
