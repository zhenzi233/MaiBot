# -*- coding: utf-8 -*-
"""写入 SnowLuma 适配器配置(token 直接取自 SnowLuma 自身配置,不落明文到脚本里)"""
import json
import tomlkit

SL_CFG = r'F:\QQAI\SnowLuma-v2.0.3-win-x64\config\onebot_3660925128.json'
ADAPTER_CFG = r'F:\QQAI\MaiBot\plugins\MaiBot-SnowLuma-Adapter\config.toml'

sl = json.load(open(SL_CFG, encoding='utf-8-sig'))
networks = sl.get('networks') or {}
ws = (networks.get('wsServers') or [])
if not ws:
    raise SystemExit('SnowLuma 配置里没有 wsServers,请先在其 WebUI 开启正向 WebSocket')
item = ws[0]
host = item.get('host') or '127.0.0.1'
if host in ('0.0.0.0', '::'):
    host = '127.0.0.1'
port = int(item.get('port') or 3001)
token = item.get('accessToken') or ''

doc = tomlkit.document()
doc.add(tomlkit.comment('MaiBot SnowLuma 适配器 —— 由部署脚本生成'))
doc.add(tomlkit.comment('连接 SnowLuma 的正向 WebSocket 服务'))

plugin = tomlkit.table()
plugin['enabled'] = True
doc['plugin'] = plugin

client = tomlkit.table()
client['client_type'] = 'auto'
client['server'] = host
client['port'] = port
client['token'] = token
client['heartbeat_interval'] = 30.0
client['reconnect_delay_sec'] = 5.0
client['action_timeout_sec'] = 15.0
client['connection_id'] = ''
doc['client'] = client

notice = tomlkit.table()
notice['enabled'] = True
doc['notice'] = notice

filters = tomlkit.table()
filters['ban_user_id'] = []
filters['ban_qq_bot'] = False
doc['filters'] = filters

debug = tomlkit.table()
debug['ignore_self_message'] = False
doc['debug'] = debug

open(ADAPTER_CFG, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('适配器配置已写入:', ADAPTER_CFG)
print('  连接目标: ws://%s:%d   token: %s...' % (host, port, token[:6] if token else '(空)'))
