# 特徵量測：正面(臉/腿)、側面(頭/腿姿)
from PIL import Image

im = Image.open("/home/oa312/workspace/sheep_3d/refs/ref_4views.jpg").convert("RGB")
px = im.load()

def bbox(x0, y0, x1, y1, pred, label):
    xs, ys = [], []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if pred(px[x, y]):
                xs.append(x); ys.append(y)
    if not xs:
        print(label, ": 無像素")
        return
    print(f"{label}: x[{min(xs)},{max(xs)}] y[{min(ys)},{max(ys)}]  W={max(xs)-min(xs)+1} H={max(ys)-min(ys)+1}")
    return min(xs), min(ys), max(xs), max(ys)

# 探測：正面 y=530 一列的顏色（找腿）
row = 530
segs = []
prev = False
for x in range(60, 420):
    r, g, b = px[x, row]
    warm = (r - b) > 15 and r > 200
    if warm and not prev:
        start = x
    if not warm and prev:
        segs.append((start, x - 1))
    prev = warm
print("正面 y=530 暖色段落:", segs)
print("  樣本色:", [px[x, 530] for x in range(segs[0][0], segs[0][0]+3)] if segs else "-")

# 正面臉（暗色塊：sum < 660 在頭部區域）
bbox(120, 95, 360, 260, lambda c: sum(c) < 665, "正面臉(暗塊)")

# 正面腿區（y 500~560）
bbox(60, 495, 420, 565, lambda c: (c[0]-c[2]) > 15 and c[0] > 200, "正面腿區")

# 左側視圖頭（tan 色塊 r-b>55，在 x 260~420, y 650~820）
bbox(260, 650, 430, 830, lambda c: (c[0]-c[2]) > 55, "左側頭(tan)")

# 左側腿：掃 y=1050 一列
row = 1050
segs = []
prev = False
for x in range(50, 430):
    r, g, b = px[x, row]
    warm = (r - b) > 15 and r > 200
    if warm and not prev:
        start = x
    if not warm and prev:
        segs.append((start, x - 1))
    prev = warm
print("左側 y=1050 暖色段落(腿):", segs)

# 尾巴（背面棕塊 r+g+b < 500）
bbox(560, 380, 780, 500, lambda c: sum(c) < 500, "背面尾(棕)")
