# -*- coding: utf-8 -*-
"""按第三轮评审收紧耳朵尺寸(三个预设同步)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

S = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'

OLD = (
    '头部左右两侧各有一只横向展开的宽大深蓝色鳍状耳朵，耳朵横向展开但长度适中，'
    '耳尖向左右外侧延伸；耳朵宽度约为脸宽的 0.8 至 1.1 倍，外轮廓圆润扁平，略向下弯；'
    '耳朵下缘完整连接白色荷叶边，耳根处各系一只蓝色蝴蝶结。'
)

NEW = (
    '头部左右两侧各有一只短小的深蓝色鳍状耳朵，贴在脸侧、向左右外侧伸出；'
    '单只耳朵的横向长度约为脸宽的 0.25 至 0.3 倍，双耳总跨度不超过脸宽的 1.4 倍；'
    '耳尖必须落在长发外轮廓以内，不外扩成宽翼、不形成大翅膀；'
    '外轮廓圆润扁平、略向下弯；耳朵下缘完整连接白色荷叶边，耳根处各系一只蓝色蝴蝶结。'
)

ADD_NEG = '巨型耳鳍，宽翼，三角形大耳，耳朵外扩超出头发，'

s = json.load(open(S, encoding='utf-8'))
hit = 0
for p in s['settings']['style']['presets']:
    pos = p['positive_prompt_template']
    if OLD in pos:
        pos = pos.replace(OLD, NEW)
        hit += 1
    p['positive_prompt_template'] = pos
    neg = p['negative_prompt_template']
    if '巨型耳鳍' not in neg:
        p['negative_prompt_template'] = ADD_NEG + neg
        print('  %-8s 反向已补限制词' % p['name'])

s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(S, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('正向替换 %d/3 个预设 | revision -> %d' % (hit, s['revision']))
for p in s['settings']['style']['presets']:
    print('  %-8s 含新耳描述: %s' % (p['name'], '单只耳朵的横向长度' in p['positive_prompt_template']))
