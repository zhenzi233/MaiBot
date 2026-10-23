# -*- coding: utf-8 -*-
"""接一个能识图的模型(国家超算 gjcs),解锁:表情包发送 + 图片理解"""
import re
import tomlkit

MP = r'F:\QQAI\MaiBot\config\model_config.toml'
CRED = r'C:\Users\Administrator\.dsh\.credentials.yaml'
KEY_RE = re.compile(r'GJCS_API_KEY\s*:\s*([^\s]+)')
MODEL_NAME = 'gjcs-vision'
MODEL_ID = 'DeepSeek-V4.1-Flash-1017'

key = KEY_RE.search(open(CRED, encoding='utf-8').read()).group(1).strip().strip('"\'')
doc = tomlkit.parse(open(MP, encoding='utf-8').read())

# 1) 服务商
providers = doc['api_providers']
if not any(str(p.get('name')) == 'gjcs' for p in providers):
    p = tomlkit.table()
    p['name'] = 'gjcs'
    p['base_url'] = 'https://api.scnet.cn/api/llm/v1'
    p['api_key'] = key
    p['client_type'] = 'openai'
    p['auth_type'] = 'bearer'
    p['auth_header_name'] = 'Authorization'
    p['auth_header_prefix'] = 'Bearer'
    p['model_list_endpoint'] = '/models'
    p['reasoning_parse_mode'] = 'auto'
    providers.append(p)
    print('+ 服务商 gjcs')
else:
    print('= 服务商 gjcs 已存在')

# 2) 视觉模型
models = doc['models']
if not any(str(m.get('name')) == MODEL_NAME for m in models):
    m = tomlkit.table()
    m['model_type'] = 'llm'
    m['model_identifier'] = MODEL_ID
    m['name'] = MODEL_NAME
    m['api_provider'] = 'gjcs'
    m['price_in'] = 0.0
    m['cache_price_in'] = 0.0
    m['price_out'] = 0.0
    m['send_temperature'] = True
    m['force_stream_mode'] = False
    m['visual'] = True
    models.append(m)
    print('+ 模型 %s (%s, visual=true)' % (MODEL_NAME, MODEL_ID))
else:
    print('= 模型 %s 已存在' % MODEL_NAME)

# 3) 任务分配
tasks = doc['model_task_config']
for name in ('vlm', 'emoji'):
    if name in tasks:
        old = list(tasks[name].get('model_list') or [])
        tasks[name]['model_list'] = [MODEL_NAME]
        print('~ %s.model_list: %s -> [%s]' % (name, old, MODEL_NAME))
    else:
        print('! 没有 [model_task_config.%s]' % name)

open(MP, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('已保存')
