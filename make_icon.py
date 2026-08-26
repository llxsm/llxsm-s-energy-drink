import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ---------- 参数 ----------
SIZE = 512          # 高分辨率渲染尺寸
R = 90              # 圆角矩形圆角半径
ICO_SIZES = [16, 20, 24, 32, 40, 48, 64, 128, 256]

# 配色（与页面"青蓝"主题一致）
BG_TOP = (2, 48, 71)        # #023047
BG_BOT = (0, 180, 216)      # #00b4d8
HEART_TOP = (144, 224, 239) # #90e0ef
HEART_BOT = (0, 119, 182)   # #0077b6


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def vgradient(size, top, bottom):
    """纵向渐变图，形状 (size, size, 3) uint8"""
    t = np.linspace(0, 1, size)[:, None]
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    for i in range(3):
        arr[:, :, i] = (top[i] + (bottom[i] - top[i]) * t).astype(np.uint8)
    return arr


def heart_points(cx, cy, scale, n=240):
    """经典心形参数曲线，返回像素坐标点列表（y 向下）。"""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        px = cx + x * scale
        py = cy - y * scale
        pts.append((px, py))
    return pts


# ---------- 背景（圆角矩形 + 纵向渐变）----------
bg_arr = vgradient(SIZE, BG_TOP, BG_BOT)
img = Image.fromarray(bg_arr).convert("RGB")
mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=R, fill=255)

# 心形蒙版
heart_cx, heart_cy, heart_scale = SIZE / 2, SIZE / 2 + 8, SIZE / 48
hp = heart_points(heart_cx, heart_cy, heart_scale)
heart_mask = Image.new("L", (SIZE, SIZE), 0)
ImageDraw.Draw(heart_mask).polygon(hp, fill=255)

# 心形渐变填充（叠加到背景上）
heart_arr = vgradient(SIZE, HEART_TOP, HEART_BOT)
heart_img = Image.fromarray(heart_arr).convert("RGB")
img = Image.composite(heart_img, img, heart_mask)

# 高光（左上柔光）
gloss = Image.new("L", (SIZE, SIZE), 0)
gd = ImageDraw.Draw(gloss)
gx, gy, gw, gh = int(SIZE * 0.32), int(SIZE * 0.24), int(SIZE * 0.26), int(SIZE * 0.20)
gd.ellipse([gx, gy, gx + gw, gy + gh], fill=140)
gloss = gloss.filter(ImageFilter.GaussianBlur(14))
white = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
img = Image.composite(white, img, gloss)

# 装饰小爱心（右上 + 左下）
draw = ImageDraw.Draw(img)
for (dcx, dcy, ds, col) in [
    (int(SIZE * 0.80), int(SIZE * 0.22), SIZE / 150, (201, 242, 250)),
    (int(SIZE * 0.20), int(SIZE * 0.80), SIZE / 210, (144, 224, 239)),
    (int(SIZE * 0.86), int(SIZE * 0.70), SIZE / 260, (255, 255, 255)),
]:
    sp = heart_points(dcx, dcy, ds)
    draw.polygon(sp, fill=col)

# 应用圆角背景蒙版（裁掉圆角外的装饰）
img.putalpha(mask)

# ---------- 导出多尺寸 .ico ----------
img.save("app_icon.ico", sizes=[(s, s) for s in ICO_SIZES])
print("已生成 app_icon.ico，尺寸:", ICO_SIZES)

# 同时导出一个 256 预览 PNG 方便查看
img.convert("RGBA").resize((256, 256), Image.LANCZOS).save("app_icon_preview.png")
print("已生成 app_icon_preview.png")
