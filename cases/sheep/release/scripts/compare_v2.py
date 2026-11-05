# compare_v2.py — 修正：側面原圖框排除底部紅字標籤
from PIL import Image
import sys

OUT = "/home/oa312/workspace/sheep_3d/"
VER = sys.argv[1] if len(sys.argv) > 1 else "v2"

def ref_mask(quad):
    im = Image.open(OUT+"refs/ref_4views.jpg").convert("RGB"); px = im.load()
    boxes = {"front": (0, 60, 448, 590), "back": (450, 60, 896, 590),
             "left": (0, 620, 448, 1105), "right": (450, 620, 896, 1105)}
    x0, y0, x1, y1 = boxes[quad]
    m = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            if (r-b) > 22 or (r-g) > 18:
                m.add((x, y))
    return m

def render_mask(path):
    im = Image.open(path).convert("RGBA"); px = im.load()
    W, H = im.size
    return {(x, y) for y in range(H) for x in range(W) if px[x, y][3] > 128}

def profile(mask):
    ys = {}
    for (x, y) in mask:
        if y in ys:
            a, b = ys[y]; ys[y] = (min(a, x), max(b, x))
        else:
            ys[y] = (x, x)
    return ys

def compare(refq, render, label):
    rp = profile(ref_mask(refq)); gp = profile(render_mask(render))
    ry = sorted(rp); gy = sorted(gp)
    rt, rb = ry[0], ry[-1]; gt, gb = gy[0], gy[-1]
    rh = rb-rt+1; gh = gb-gt+1
    scale = rh/gh
    print(f"--- {label} ---  原圖高 {rh}px 渲染高 {gh}px 縮放 {scale:.4f}")
    devs = []
    for k in range(5, 100, 5):
        ry_ = int(rb - k/100*(rh-1))
        if ry_ not in rp: continue
        rw = rp[ry_][1]-rp[ry_][0]+1
        gy_i = int(round(gb - (rb-ry_)/scale))
        best = None
        for d in (0, 1, -1, 2, -2):
            if gy_i+d in gp: best = gp[gy_i+d]; break
        if best is None: continue
        gw = (best[1]-best[0]+1)*scale
        dev = (gw-rw)/rw*100; devs.append(abs(dev))
        print(f"  底算 {k:3d}%  原圖寬 {rw:4d}  模型寬 {gw:6.1f}  誤差 {dev:+6.1f}%")
    print(f"  平均|誤差| {sum(devs)/len(devs):.1f}%  最大 {max(devs):.1f}%")

compare("front", OUT+f"{VER}_front_ortho.png", "正面")
compare("left",  OUT+f"{VER}_side_ortho.png",  "側面(對左側視圖)")
