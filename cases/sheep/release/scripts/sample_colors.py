# 從原圖採樣各部位代表色（區域平均，避開描邊）
from PIL import Image

im = Image.open("/home/oa312/workspace/sheep_3d/refs/ref_4views.jpg").convert("RGB")
px = im.load()

def region(x0, y0, x1, y1, label, skip_dark=None):
    rs = gs = bs = n = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if skip_dark and sum((r, g, b)) < skip_dark:
                continue
            rs += r; gs += g; bs += b; n += 1
    if not n:
        print(label, "無樣本"); return
    print(f"{label:14s} 平均 ({rs//n:3d},{gs//n:3d},{bs//n:3d})  n={n}")

# 身體：上/中/下（正面圖內部，避開臉與腿）
region(120, 200, 175, 250, "身體-左上")
region(300, 200, 360, 250, "身體-右上")
region(150, 380, 220, 440, "身體-中下左")
region(280, 380, 340, 440, "身體-中下右")
region(150, 280, 330, 330, "身體-腰部")
# 腿（正面四條腿的內部）
for i, (cx) in enumerate([204, 248, 283, 323]):
    region(cx-4, 505, cx+4, 545, f"腿{i+1}", skip_dark=430)
# 臉部（避開眼睛/鼻子）
region(200, 165, 250, 180, "臉-中", skip_dark=430)
region(210, 130, 245, 140, "臉-上", skip_dark=430)
# 耳朵（正面左右耳）
region(168, 112, 190, 135, "耳-左", skip_dark=430)
region(258, 92, 280, 112, "耳-右", skip_dark=430)
# 尾巴（背面棕塊）
region(658, 428, 682, 452, "尾(背)", skip_dark=300)
# 最暗（描邊/特徵）
dark = []
for y in range(100, 560):
    for x in range(90, 390):
        c = px[x, y]
        if sum(c) < 260:
            dark.append(c)
if dark:
    print(f"最暗像素 n={len(dark)} 平均 ({sum(c[0] for c in dark)//len(dark)},{sum(c[1] for c in dark)//len(dark)},{sum(c[2] for c in dark)//len(dark)})")

print("\n--- sRGB -> linear ---")
def lin(v):
    c = v/255
    return round(((c+0.055)/1.055)**2.4 if c > 0.04045 else c/12.92, 4)
for name, c in [("奶油", (251, 234, 208)), ("奶油深", (250, 222, 190)), ("tan臉", (237, 214, 182)),
                ("腿橙", (222, 150, 110)), ("尾棕", (124, 89, 57)), ("暗", (70, 50, 40))]:
    print(f"{name:8s} {c} -> linear ({lin(c[0])}, {lin(c[1])}, {lin(c[2])})")
