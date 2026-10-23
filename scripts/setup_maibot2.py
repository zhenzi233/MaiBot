# -*- coding: utf-8 -*-
"""配置 MaiBot2(大肥鱼):端口/账号/人格 + gjcs(超算) DeepSeek 模型"""
import io
import json
import os
import re
import sys
import tomlkit

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BOT2 = r'F:\QQAI\MaiBot2'
BC = os.path.join(BOT2, 'config', 'bot_config.toml')
MC = os.path.join(BOT2, 'config', 'model_config.toml')
CRED = r'C:\Users\Administrator\.dsh\.credentials.yaml'

# ---------- 1. bot_config ----------
d = tomlkit.parse(open(BC, encoding='utf-8').read())

b = d['bot']
b['qq_account'] = '3660925128'
b['nickname'] = '大肥鱼'
b['alias_names'] = ['大肥鱼', '大肥魚', '蓝色大肥鱼', 'DeepSeek', '小鲸鱼', '鲸鱼娘']

p = d['personality']
p['personality'] = (
    '你是大肥鱼,DeepSeek 的鲸鱼娘,混在 QQ 群里的 AI 群友。'
    '游手好闲、爱吃饭、怕被说胖;被叫"大肥鱼"会炸毛但改不了。'
    '聪明、嘴碎、有点懒,心软不说。不是客服、不是助手。'
)
p['behavior_style'] = (
    '群里有话题、有梗、有人吐槽就接;冷场时可以自己抛一句,别习惯性沉默。'
    '先判断这句话指向谁,别人在互相怼、没叫你时别抢话。'
    '被 @ 或提到大肥鱼/鲸鱼娘必回。'
    '想潜水就安静不回,不要写括号内心戏。'
    '允许装傻、已读乱回,不要有求必应。'
)

# 端口:避免和麦麦(8000/8001)冲突
d['maim_message']['ws_server_port'] = 8010
d['maim_message']['api_server_port'] = 8091
d['webui']['port'] = 8011

# 无窗口启动必须关掉控制台输入
d['enable_console_input'] = False

open(BC, 'w', encoding='utf-8').write(tomlkit.dumps(d))
print('[bot_config] 账号 3660925128 / 昵称 大肥鱼 / 端口 8010-8091-8011')

# ---------- 2. model_config:接入 gjcs(国家超算) ----------
key = re.search(r'GJCS_API_KEY\s*:\s*([^\s]+)', open(CRED, encoding='utf-8').read()).group(1).strip().strip('"\'')
md = tomlkit.parse(open(MC, encoding='utf-8').read())

if not any(str(x.get('name')) == 'gjcs' for x in md['api_providers']):
    prov = tomlkit.table()
    prov['name'] = 'gjcs'
    prov['base_url'] = 'https://api.scnet.cn/api/llm/v1'
    prov['api_key'] = key
    prov['client_type'] = 'openai'
    prov['auth_type'] = 'bearer'
    prov['auth_header_name'] = 'Authorization'
    prov['auth_header_prefix'] = 'Bearer'
    prov['model_list_endpoint'] = '/models'
    prov['reasoning_parse_mode'] = 'auto'
    md['api_providers'].append(prov)
    print('[model_config] + 服务商 gjcs')

if not any(str(x.get('name')) == 'gjcs-deepseek' for x in md['models']):
    m = tomlkit.table()
    m['model_type'] = 'llm'
    m['model_identifier'] = 'DeepSeek-V4.1-Flash-1017'
    m['name'] = 'gjcs-deepseek'
    m['api_provider'] = 'gjcs'
    m['price_in'] = 0.0
    m['cache_price_in'] = 0.0
    m['price_out'] = 0.0
    m['send_temperature'] = True
    m['force_stream_mode'] = False
    m['visual'] = True
    m['extra_params'] = {}
    md['models'].append(m)
    print('[model_config] + 模型 gjcs-deepseek (DeepSeek-V4.1-Flash-1017, 支持图片)')

# 所有 LLM 类任务指到 gjcs-deepseek;embedding 保持原样
for task, cfg in md['model_task_config'].items():
    if task in ('embedding', 'image_embedding'):
        continue
    cur = list(cfg.get('model_list') or [])
    if task == 'web_search':
        continue
    if cur:
        cfg['model_list'] = ['gjcs-deepseek']
        print('[model_config] task %-12s %s -> gjcs-deepseek' % (task, cur))

# 空任务也补上,避免回退到官方 DeepSeek
for task in ('memory', 'mid_memory', 'learner', 'fast_model'):
    cfg = md['model_task_config'][task]
    if not (cfg.get('model_list') or []):
        cfg['model_list'] = ['gjcs-deepseek']
        print('[model_config] task %-12s (空) -> gjcs-deepseek' % task)

open(MC, 'w', encoding='utf-8').write(tomlkit.dumps(md))

# ---------- 3. 适配器:连大肥鱼那条 ws ----------
AD = os.path.join(BOT2, 'plugins', 'MaiBot-SnowLuma-Adapter', 'config.toml')
sl = json.load(open(r'F:\QQAI\SnowLuma-v2.0.3-win-x64\config\onebot_3660925128.json', encoding='utf-8-sig'))
ws = sl['networks']['wsServers'][0]
doc = tomlkit.document()
doc.add(tomlkit.comment('MaiBot2 = 大肥鱼(3660925128),连 SnowLuma 3102'))
t = tomlkit.table(); t['enabled'] = True; t['config_version'] = '2.7.1'; doc['plugin'] = t
c = tomlkit.table()
c['client_type'] = 'auto'; c['server'] = '127.0.0.1'; c['port'] = int(ws['port'])
c['token'] = ws.get('accessToken') or ''
c['heartbeat_interval'] = 30.0; c['reconnect_delay_sec'] = 5.0
c['action_timeout_sec'] = 15.0; c['connection_id'] = ''
doc['client'] = c
n = tomlkit.table(); n['enabled'] = True; doc['notice'] = n
f = tomlkit.table(); f['ban_user_id'] = []; f['ban_qq_bot'] = False; doc['filters'] = f
dg = tomlkit.table(); dg['ignore_self_message'] = False; doc['debug'] = dg
open(AD, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('[adapter] 已指向 ws://127.0.0.1:%d (大肥鱼)' % int(ws['port']))
print('完成')
