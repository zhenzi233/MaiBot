# -*- coding: utf-8 -*-
"""补丁:放行代理的 fake-ip 网段(198.18.0.0/15),否则图片下载被 SSRF 校验拦下

背景:本机 FlClash(mihomo) 用 fake-ip 模式,DNS 全部返回 198.18.x.x。
插件下载结果图前会校验 IP 是否为公网,198.18/15 不是公网 → 直接报
「图片结果地址指向非公网网络」。这个网段在本机只会由代理 TUN 接管,
放行它是安全的。
注意:插件更新会覆盖此文件,更新后重新运行本脚本即可。
"""
import io
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

F = r'F:\QQAI\MaiBot\plugins\maimai-drawpic-plugin\src\maimai_drawpic\infrastructure\media\downloads.py'
src = open(F, encoding='utf-8').read()

if '_FAKE_IP_NET' in src:
    print('补丁已存在,跳过')
    raise SystemExit(0)

# 1) 导入 ip_network
src = src.replace('from ipaddress import ip_address', 'from ipaddress import ip_address, ip_network', 1)

# 2) 加入网段常量与判定函数
anchor = 'def _url(value: str) -> URL:'
helper = '''_FAKE_IP_NET = ip_network("198.18.0.0/15")


def _is_proxy_fake_ip(values: List[str]) -> bool:
    """本机代理(mihomo fake-ip)返回的地址:全部落在 198.18.0.0/15 才放行。"""

    try:
        return bool(values) and all(ip_address(value) in _FAKE_IP_NET for value in values)
    except ValueError:
        return False


'''
src = src.replace(anchor, helper + anchor, 1)

# 3) 放宽校验条件
old = 'if not addresses or (not local_origin and not all(_public_address(value) for value in addresses)):'
new = (
    'if not addresses or (\n'
    '                        not local_origin\n'
    '                        and not all(_public_address(value) for value in addresses)\n'
    '                        and not _is_proxy_fake_ip(addresses)\n'
    '                    ):'
)
if old not in src:
    print('未找到校验条件,补丁失败')
    raise SystemExit(1)
src = src.replace(old, new, 1)

open(F, 'w', encoding='utf-8').write(src)
print('补丁已写入:', F)
print('  + from ipaddress import ip_network')
print('  + _FAKE_IP_NET = 198.18.0.0/15 + _is_proxy_fake_ip()')
print('  ~ 下载校验放行 fake-ip 网段')
