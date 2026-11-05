# 臉部量測：tan 色塊（洪水填充）、眼睛（暗點）、鼻嘴記號
from PIL import Image
from collections import deque

im = Image.open("/home/oa312/workspace/sheep_3d/refs/ref_4views.jpg").convert("RGB")
px = im.load()

def flood(seed, tol, x0, y0, x1, y1, label):
    sr, sg, sb = px[seed]
    seen = set([seed]); q = deque([seed]); pts = []
    while q:
        x, y = q.popleft(); pts.append((x, y))
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n = (x+dx, y+dy)
            if n in seen or not (x0 <= n[0] < x1 and y0 <= n[1] < y1):
                continue
            r, g, b = px[n]
            if abs(r-sr) + abs(g-sg) + abs(b-sb) <= tol:
                seen.add(n); q.append(n)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    print(f"{label}: 種子 {seed} 色 {px[seed]}  面積 {len(pts)}")
    print(f"   bbox x[{min(xs)},{max(xs)}] y[{min(ys)},{max(ys)}]  W={max(xs)-min(xs)+1} H={max(ys)-min(ys)+1} 中心 ({(min(xs)+max(xs))/2:.0f},{(min(ys)+max(ys))/2:.0f})")
    # 逐列寬度
    rows = {}
    for (x, y) in pts:
        a, b2 = rows.get(y, (x, x))
        rows[y] = (min(a, x), max(b2, x))
    for y in range(min(ys), max(ys)+1, 8):
        if y in rows:
            print(f"    y={y:4d} x[{rows[y][0]:3d},{rows[y][1]:3d}] w={rows[y][1]-rows[y][0]+1:3d}")
    return pts

print("=== 正面臉部 tan ===")
flood((225, 155), 45, 150, 80, 330, 260, "正面臉")
print("\n=== 側面臉部 tan ===")
flood((350, 730), 45, 250, 640, 430, 850, "側面臉")

print("\n=== 正面眼睛（暗點 sum<430, 在臉部區）===")
for y in range(120, 175, 4):
    seg = [x for x in range(180, 285) if sum(px[x, y]) < 430]
    if seg:
        print(f"  y={y}  暗點 x={seg}")
print("\n=== 正面鼻嘴（暗線 sum<490, y 175-215）===")
for y in range(175, 215, 3):
    seg = [x for x in range(190, 275) if sum(px[x, y]) < 490]
    if seg:
        print(f"  y={y}  x={seg}")
