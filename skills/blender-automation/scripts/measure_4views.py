#!/usr/bin/env python3
"""四視圖參考圖 QC：切四格、量主體 bbox/W-H、一致性檢查、存單張切圖。

用法：
  python3 measure_4views.py IMAGE [--outdir OUTDIR] [--div-x N] [--div-y N] [--thresh N]

- 純 PIL（無 numpy）。
- 分隔線自動偵測：中央 40~60% 範圍內，整行/列暗像素（sum RGB<450）最多的位置，
  計數須 > 60% 長度；偵測不到時先探測像素亮度，再以 --div-x/--div-y 手動指定。
- 物件遮罩：與背景色（四角取樣）色差 > --thresh。
- 輸出：四格 bbox、W/H、一致性檢查；切圖存 <name>.png。
"""
import argparse
import os

from PIL import Image


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
                    runs.append((start, i - gap))
                    start, gap = None, 0
    if start is not None:
        runs.append((start, len(mask) - 1))
    return runs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--div-x", type=int, default=None, help="垂直分隔線 x（跳過自動偵測）")
    ap.add_argument("--div-y", type=int, default=None, help="水平分隔線 y")
    ap.add_argument("--thresh", type=int, default=60, help="與背景的色差閾值")
    a = ap.parse_args()

    im = Image.open(a.image).convert("RGB")
    W, H = im.size
    px = im.load()

    # 背景色＝四角 20x20 平均
    br = bg = bb = n = 0
    for cx, cy in ((0, 0), (W - 20, 0), (0, H - 20), (W - 20, H - 20)):
        for y in range(cy, cy + 20):
            for x in range(cx, cx + 20):
                r, g, b = px[x, y]
                br += r
                bg += g
                bb += b
                n += 1
    br, bg, bb = br // n, bg // n, bb // n
    print(f"image {W}x{H}  背景 RGB=({br},{bg},{bb})")

    def is_obj(x, y):
        r, g, b = px[x, y]
        return abs(r - br) + abs(g - bg) + abs(b - bb) > a.thresh

    def find_div(axis):
        if axis == "col":
            rng = range(int(W * 0.40), int(W * 0.60))
            scan = lambda v: sum(1 for y in range(0, H, 2) if sum(px[v, y]) < 450)
            length = H
        else:
            rng = range(int(H * 0.40), int(H * 0.60))
            scan = lambda v: sum(1 for x in range(0, W, 2) if sum(px[x, v]) < 450)
            length = W
        best, bestv = None, 0
        for v in rng:
            c = scan(v)
            if c > bestv:
                bestv, best = c, v
        full = bestv * 2  # scan step=2
        return (best if full > length * 0.6 else None), full

    dx, dy = a.div_x, a.div_y
    if dx is None:
        dx, cnt = find_div("col")
        if dx is None:
            raise SystemExit(f"找不到垂直分隔線（最高計數 {cnt}）— 先探測像素亮度，再以 --div-x 指定")
    if dy is None:
        dy, cnt = find_div("row")
        if dy is None:
            raise SystemExit(f"找不到水平分隔線（最高計數 {cnt}）— 以 --div-y 指定")
    print(f"分隔線 col={dx} row={dy}")
    os.makedirs(a.outdir, exist_ok=True)

    def measure(qx0, qy0, qx1, qy1, name):
        rowc = [sum(1 for x in range(qx0, qx1) if is_obj(x, y)) for y in range(qy0, qy1)]
        rr = sorted(runs_of(rowc, 3, 5), key=lambda r: r[1] - r[0], reverse=True)
        r0, r1 = rr[0]
        top, bot = qy0 + r0, qy0 + r1
        colc = [sum(1 for y in range(top, bot + 1) if is_obj(x, y)) for x in range(qx0, qx1)]
        cr = sorted(runs_of(colc, 2, 5), key=lambda r: r[1] - r[0], reverse=True)
        c0, c1 = cr[0]
        left, right = qx0 + c0, qx0 + c1
        w, h = right - left + 1, bot - top + 1
        m = 8
        im.crop(
            (max(0, left - m), max(0, top - m), min(W, right + m), min(H, bot + m))
        ).save(os.path.join(a.outdir, f"{name}.png"))
        print(
            f"{name:6s}: x[{left:4d},{right:4d}] y[{top:4d},{bot:4d}]"
            f"  W={w:4d} H={h:4d}  W/H={w / h:.3f}"
        )
        return w, h

    fw, fh = measure(0, 0, dx, dy, "front")
    bw, bh = measure(dx + 2, 0, W, dy, "back")
    lw, lh = measure(0, dy + 2, dx, H, "left")
    rw, rh = measure(dx + 2, dy + 2, W, H, "right")

    hs = (fh, bh, lh, rh)
    print(f"\n高度差 spread = {(max(hs) - min(hs)) / min(hs) * 100:.1f}%（四張標同一比例時應 <3%）")
    print(f"前/背 W/H 差 = {abs(fw / fh - bw / bh) / (fw / fh) * 100:.1f}%（鏡像對應 <2%）")
    print(f"左/右 W/H 差 = {abs(lw / lh - rw / rh) / (lw / lh) * 100:.1f}%（鏡像對應 <2%）")


if __name__ == "__main__":
    main()
