# -*- coding: utf-8 -*-
"""为 MaiBot 写入 DeepSeek 凭据 + 修正 flash 模型标识符(保留注释与格式)"""
import json
import tomlkit

MP = r'F:\QQAI\MaiBot\config\model_config.toml'
AP = r'F:\甄舜杰\AIWORK\AstrBot\data\cmd_config.json'

cfg = json.load(open(AP, encoding='utf-8-sig'))
src = cfg['provider_sources'][0]
key = src['key']
if isinstance(key, list):
    key = key[0]

doc = tomlkit.parse(open(MP, encoding='utf-8').read())

# 1) API 服务商凭据
for p in doc['api_providers']:
    if p['name'] == 'DeepSeek':
        p['api_key'] = key
        p['base_url'] = 'https://api.deepseek.com'
        print('已写入 api_key(base_url=https://api.deepseek.com)')

# 2) 修正模型标识符:DeepSeek 实际提供 deepseek-flash / deepseek-v4-pro
for m in doc['models']:
    if m['model_identifier'] == 'deepseek-v4-flash':
        m['model_identifier'] = 'deepseek-flash'
        print('修正模型标识符 deepseek-v4-flash -> deepseek-flash (name=%s)' % m['name'])

open(MP, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('model_config.toml 已保存')
