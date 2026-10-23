# -*- coding: utf-8 -*-
"""把 MaiBot 切到小号 3911764418(爸爸巴巴)"""
import json
import tomlkit

SL_CFG = r'F:\QQAI\SnowLuma-v2.0.3-win-x64\config\onebot_3911764418.json'
ADAPTER = r'F:\QQAI\MaiBot\plugins\MaiBot-SnowLuma-Adapter\config.toml'
BOTCFG = r'F:\QQAI\MaiBot\config\bot_config.toml'
UIN = '3911764418'

sl = json.load(open(SL_CFG, encoding='utf-8-sig'))
ws = (sl.get('networks') or {}).get('wsServers') or []
if not ws:
    raise SystemExit('小号没有开启正向 WebSocket,请先在 SnowLuma 里开')
it = ws[0]
host = it.get('host') or '127.0.0.1'
if host in ('0.0.0.0', '::'):
    host = '127.0.0.1'
port = int(it.get('port'))
token = it.get('accessToken') or ''

# 1) 适配器
doc = tomlkit.parse(open(ADAPTER, encoding='utf-8').read())
doc['client']['server'] = host
doc['client']['port'] = port
doc['client']['token'] = token
open(ADAPTER, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
print('适配器 -> ws://%s:%d' % (host, port))

# 2) 机器人身份
b = tomlkit.parse(open(BOTCFG, encoding='utf-8').read())
b['bot']['qq_account'] = UIN
al = list(b['bot']['alias_names'])
if '爸爸巴巴' not in al:
    al.append('爸爸巴巴')
b['bot']['alias_names'] = al
open(BOTCFG, 'w', encoding='utf-8').write(tomlkit.dumps(b))
print('bot_config: qq_account=%s, alias 追加 爸爸巴巴' % UIN)
