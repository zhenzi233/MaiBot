# -*- coding: utf-8 -*-
"""补丁:GIF 图片写入长期记忆前先转成首帧 PNG

问题:A-Memorix 的 asset_store 只支持 BMP/JPEG/PNG/WEBP,GIF 会抛
「不支持的图片格式: GIF」,导致群里发动图时记忆写入报错、那张图记不下来。
处理:在 memory_flow_service 传入 image_bytes 之前,把 GIF 转成首帧 PNG。
插件/程序升级会覆盖此文件,升级后重新运行本脚本即可。
"""
import io
import os
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HELPER = '''

def _to_static_image_bytes(payload: bytes) -> bytes:
    """把动图(GIF/APNG)降级成首帧 PNG,避免长期记忆层拒绝该格式。"""
    try:
        from PIL import Image as _PILImage

        with _PILImage.open(io.BytesIO(payload)) as image:
            fmt = str(image.format or "").upper()
            if fmt not in {"GIF", "APNG"}:
                return payload
            image.seek(0)
            frame = image.convert("RGBA")
    except Exception:
        return payload
    out = io.BytesIO()
    frame.save(out, format="PNG")
    return out.getvalue()
'''

TARGETS = [
    r'F:\QQAI\MaiBot\src\services\memory_flow_service.py',
    r'F:\QQAI\MaiBot2\src\services\memory_flow_service.py',
]

OLD_CALL = '                    image_bytes=bytes(component.binary_data),'
NEW_CALL = '                    image_bytes=_to_static_image_bytes(bytes(component.binary_data)),'

for path in TARGETS:
    if not os.path.isfile(path):
        print('跳过(不存在):', path)
        continue
    src = open(path, encoding='utf-8').read()
    if '_to_static_image_bytes' in src:
        print('已有补丁:', path)
        continue

    bak = path + '.bak_gif'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)

    if OLD_CALL not in src:
        print('! 未找到调用点,跳过:', path)
        continue

    # 1) 插入辅助函数(放在 logger 定义之后)
    anchor = 'logger = get_logger("memory_flow_service")'
    if anchor not in src:
        print('! 未找到 logger 锚点,跳过:', path)
        continue
    src = src.replace(anchor, anchor + HELPER, 1)

    # 2) 替换调用点
    src = src.replace(OLD_CALL, NEW_CALL, 1)

    open(path, 'w', encoding='utf-8').write(src)
    print('已打补丁:', path)
