# 逐列輪廓剖面：正面(寬) / 側面(深)，並量臉部與腿
from PIL import Image

im = Image.open("/home/oa312/workspace/sheep_3d/refs/ref_4views.jpg").convert("RGB")
px = im.load()

def warm(c):
    r, g, b = c
    return (r - b) > 15 and r > 195

def scan_row(y, x0, x1):
    xs = [x for x in range(x0, x1) if warm(px[x, y])]
    return (min(xs), max(xs)) if xs else None

print("=== 正面 (象限 x0=0) 每 10 列：左緣 右緣 寬 ===")
FR_TOP, FR_BOT = 87, 559
for y in range(FR_TOP, FR_BOT + 1, 10):
    s = scan_row(y, 60, 420)
    if s:
        print(f"y={y:4d} t={(y-FR_TOP)/(FR_BOT-FR_TOP):.2f}  x[{s[0]:3d},{s[1]:3d}] w={s[1]-s[0]+1:3d}")

print("\n=== 側面 (左側視圖, 象限 y0=600) 每 10 列 ===")
SD_TOP, SD_BOT = 654, 1096
for y in range(SD_TOP, SD_BOT + 1, 10):
    s = scan_row(y, 40, 430)
    if s:
        print(f"y={y:4d} t={(y-SD_TOP)/(SD_BOT-SD_TOP):.2f}  x[{s[0]:3d},{s[1]:3d}] d={s[1]-s[0]+1:3d}")

print("\n=== 正面：tan 臉部色塊逐列 (r-b>50) ===")
for y in range(95, 230, 8):
    xs = [x for x in range(150, 330) if (px[x, y][0] - px[x, y][2]) > 50 and px[x, y][0] < 250]
    if xs:
        print(f"y={y:4d}  x[{min(xs):3d},{max(xs):3d}] w={max(xs)-min(xs)+1:3d}")

print("\n=== 背面：棕尾巴 (sum<500) 逐列 ===")
for y in range(400, 510, 8):
    xs = [x for x in range(600, 760) if sum(px[x, y]) < 500]
    if xs:
        print(f"y={y:4d}  x[{min(xs):3d},{max(xs):3d}] w={max(xs)-min(xs)+1:3d}")
