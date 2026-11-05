# 四視圖品管：切四格、找分隔線、量主體 bbox 與 W/H，並存四張單圖
from PIL import Image
import os

SRC = "/home/oa312/workspace/sheep_3d/refs/ref_4views.jpg"
OUT = "/home/oa312/workspace/sheep_3d/refs"
im = Image.open(SRC).convert("RGB")
W, H = im.size
px = im.load()
print("image size:", W, H)

def is_warm(x, y):
    r, g, b = px[x, y]
    return (r - b) > 22 or (r - g) > 18

# ---- 分隔線（已實測）----
dx, dy = 448, 600

def runs_of(mask, min_count, gap_tol):
    runs, start, gap = [], None, 0
    for i, c in enumerate(mask):
        if c >= min_count:
            if start is None:
                start = i
            gap = 0
        else:
            if start is not None:
                gap += 1
                if gap > gap_tol:
                    runs.append((start, i - gap)); start = None; gap = 0
    if start is not None:
        runs.append((start, len(mask) - 1))
    return runs

def measure(qx0, qy0, qx1, qy1, name):
    # 列投影 → 取含主體的最長連續段（避開紅色文字等離散暖色塊）
    rowc = [sum(1 for x in range(qx0, qx1) if is_warm(x, y)) for y in range(qy0, qy1)]
    rr = sorted(runs_of(rowc, 3, 5), key=lambda r: r[1]-r[0], reverse=True)
    r0, r1 = rr[0]
    top, bot = qy0 + r0, qy0 + r1
    colc = [sum(1 for y in range(top, bot+1) if is_warm(x, y)) for x in range(qx0, qx1)]
    cr = sorted(runs_of(colc, 2, 5), key=lambda r: r[1]-r[0], reverse=True)
    c0, c1 = cr[0]
    left, right = qx0 + c0, qx0 + c1
    w, h = right-left+1, bot-top+1
    print(f"{name:6s}: x[{left:4d},{right:4d}] y[{top:4d},{bot:4d}]  W={w:4d} H={h:4d}  W/H={w/h:.3f}")
    # 存單圖（留 8px 邊）
    m = 8
    crop = im.crop((max(0,left-m), max(0,top-m), min(W,right+m), min(H,bot+m)))
    crop.save(os.path.join(OUT, f"{name}.png"))
    return dict(name=name, w=w, h=h, wh=w/h)

q = [
    measure(0, 0, dx, dy, "front"),
    measure(dx+2, 0, W, dy, "back"),
    measure(0, dy+2, dx, H, "left"),
    measure(dx+2, dy+2, W, H, "right"),
]

hs = [d["h"] for d in q]
print("\n高度檢查（四張都標 100）: min=%d max=%d spread=%.1f%%" % (min(hs), max(hs), (max(hs)-min(hs))/min(hs)*100))
fw, bw = q[0]["wh"], q[1]["wh"]
lw, rw = q[2]["wh"], q[3]["wh"]
print("前/背 W/H 差: %.3f vs %.3f (%.1f%%)" % (fw, bw, abs(fw-bw)/fw*100))
print("左/右 W/H 差: %.3f vs %.3f (%.1f%%)" % (lw, rw, abs(lw-rw)/lw*100))
print("正面(寬) vs 側面(深): W/H %.3f vs %.3f" % (fw, lw))
