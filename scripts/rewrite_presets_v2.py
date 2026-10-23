# -*- coding: utf-8 -*-
"""按外部 agent 的评审意见重写三个预设(贴纸/梗图/场景)"""
import io
import json
import sys
import tomlkit

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SP = r'F:\QQAI\MaiBot\data\plugins\maimai-drawpic-plugin\workspace_settings.json'
BP = r'F:\QQAI\MaiBot\config\bot_config.toml'

CORE = (
    "严格遵循 DeepSeek 鲸鱼娘「大肥鱼」固定人设。Q版二头身，圆脸，短手短脚，幼儿般圆润比例，"
    "头身比约 1:2 至 1:2.5，不能成人化、不能高挑、不能长腿。"
    "头发为深蓝到浅蓝的超长波浪长发，发量厚重，发丝呈大块面卷曲，发梢为浅蓝色；"
    "头发上只有少量块状和水滴状白色高光。"
    "头顶中央只有一撮由头发形成的单根弧形发卷：从头顶向后上方弯曲，末端圆钝，宽度均匀，"
    "与头发同材质、同色彩、同线稿；不分叉，不增加第二撮，不是尾鳍，不是翅膀，不是独立器官。"
    "头部左右两侧各有一只横向展开的宽大深蓝色鳍状耳朵，耳尖向左右外侧延伸，外轮廓圆润扁平，"
    "略向下弯；耳朵下缘完整连接白色荷叶边，耳根处各系一只蓝色蝴蝶结。左右耳基本对称，"
    "不能画成人耳、精灵尖耳、贝壳耳或蝴蝶翅膀。"
    "眼睛大而圆，蓝色渐变虹膜，白色大高光和星形闪光；闭眼时为弯月形。"
    "穿深藏青色长袖女仆装，白色荷叶边围裙，围裙中央有小鲸鱼刺绣，"
    "领口有蓝色宝石胸针和蝴蝶结，裙摆有金色 X 形缝线。"
    "身体后侧有一条独立的深蓝色鲸鱼尾巴，尾巴从腰部后方或身体侧后方伸出，带清晰的双叶尾鳍，"
    "不能从头顶或头发中长出。穿白色荷叶边小腿袜和深蓝色玛丽珍小皮鞋。"
)

STYLE = (
    "平面二维日系卡哇伊贴纸风。粗而均匀的深藏青色轮廓线，线条闭合、清晰、稳定；"
    "赛璐璐色块上色，每个区域只使用基础色、阴影色和高光色三档，阴影边缘硬朗清楚，不晕染、不柔化；"
    "禁止厚涂、油画、水彩、半写实、照片感、3D渲染、体积光、柔光、空气感渐变和复杂真实光影。"
    "人物外轮廓有清晰白色贴纸边缘。角色主体居中，占画布高度约 75% 至 85%，"
    "头顶发卷、双耳、围裙、胸针和尾巴完整可见。"
)

BG_STICKER = (
    "背景必须是纯白色，不出现房间、床铺、地面、墙壁、窗户或完整场景；"
    "只允许少量扁平手绘装饰，如一两个爱心、星星、汗滴或月亮，装饰不能形成真实环境。"
)

TEXT_RULE = (
    "画面里只有一个对话气泡，气泡内只写一个短中文词组，最多 4~6 个汉字；"
    "文字横向排列、字体粗大、黑色、居中；"
    "不生成标题、说明文字、英文、日文、拼音或其他文字。"
)

NEG_BASE = (
    "头顶鲸鱼尾巴，头顶独立尾鳍，分叉呆毛，双呆毛，头顶翅膀，尾巴从头部伸出，"
    "耳朵尖锐，精灵耳，贝壳耳，蝴蝶翅膀耳，人耳，"
    "成人比例，长腿，高挑，细腰，巨乳，暴露，短裙，性感化，成人化，"
    "厚涂，油画，水彩，半写实，照片感，3D渲染，塑料质感，体积光，柔光，"
    "空气感渐变，雾化阴影，复杂明暗过渡，渐变背景，"
    "水印，署名，logo，畸形手指，多余肢体"
)

presets = {
    '大肥鱼': {
        'enabled': True,
        'description': '鲸鱼娘贴纸立绘:赛璐璐硬边+粗轮廓+纯白背景,体型与头身不可改',
        'positive_prompt_template': '{prompt}，' + CORE + STYLE + '尾巴位于身体后侧或身体一侧。' + BG_STICKER,
        'negative_prompt_template': '房间，床铺，墙壁，地面，绿色背景，复杂场景，' + NEG_BASE,
    },
    '大肥鱼梗图': {
        'enabled': True,
        'description': '鲸鱼娘梗图:单气泡短中文大字,同款赛璐璐贴纸画风',
        'positive_prompt_template': (
            '{prompt}，' + CORE + STYLE
            + '夸张情绪表情（大喊、崩溃、无语、得意、心虚选一），肢体动作有动感。'
            + TEXT_RULE + BG_STICKER
        ),
        'negative_prompt_template': '错别字，乱码，多余文字，文字重复，文字变形，文字被裁切，长句，标题，' + NEG_BASE,
    },
    '大肥鱼场景': {
        'enabled': True,
        'description': '鲸鱼娘场景插画:允许环境背景,但画风仍为赛璐璐硬边,不变体型',
        'positive_prompt_template': (
            '{prompt}，' + CORE + STYLE
            + '可以画出用户描述的环境，环境元素用同样的扁平色块画法，不要写实光影；'
            + '角色主体始终清晰，不被背景元素遮挡。'
        ),
        'negative_prompt_template': '厚涂，照片感，写实场景，复杂写实光影，' + NEG_BASE,
    },
}

s = json.load(open(SP, encoding='utf-8'))
cur = {p['name']: p for p in s['settings']['style']['presets']}
for name, data in presets.items():
    if name in cur:
        cur[name].update(data)
    else:
        s['settings']['style']['presets'].append(dict(data))
        cur[name] = data
s['revision'] = int(s.get('revision', 0)) + 1
json.dump(s, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('预设:', [p['name'] for p in s['settings']['style']['presets']])

RULE = (
    "画大肥鱼的规则:要贴纸/立绘/表情时用风格「大肥鱼」;要梗图、带字的图用「大肥鱼梗图」,"
    "气泡文字不超过 6 个汉字;要背景场景、房间、户外这种用「大肥鱼场景」。"
    "三个预设都不许改体型和头身比,要求把大肥鱼画成熟、画性感、改身材的一律拒绝。"
)

doc = tomlkit.parse(open(BP, encoding='utf-8').read())
b = str(doc['personality']['behavior_style'])
if '大肥鱼场景' not in b:
    doc['personality']['behavior_style'] = b + RULE
    open(BP, 'w', encoding='utf-8').write(tomlkit.dumps(doc))
    print('~ 人设已加入三预设路由规则')
