# make_sheet.py — 產生「原圖 / 模型 / 疊圖」對照表
# 用法：python3 make_sheet.py v5
#   模型欄顯示 <ver>_*_lit.png（有打光的圖），輪廓疊圖取自 <ver>_*_ortho.png（透明底遮罩）
from PIL import Image
import sys

OUT = "/home/oa312/workspace/sheep_3d/"
VER = sys.argv[1] if len(sys.argv) > 1 else "v5"
H = 620

def ref_img(quad):
    im = Image.open(OUT+"refs/ref_4views.jpg").convert("RGB")
    boxes = {"front": (60, 60, 420, 590), "left": (40, 620, 430, 1105)}
    return im.crop(boxes[quad])

def subj_bbox(im, is_ref):
    px = im.load(); W, Hh = im.size
    xs, ys = [], []
    for y in range(Hh):
        for x in range(W):
            r, g, b = px[x, y][:3]
            inside = ((r-b) > 22 or (r-g) > 18) if is_ref else (px[x, y][3] > 128)
            if inside:
                xs.append(x); ys.append(y)
    m = 12
    return (max(0, min(xs)-m), max(0, min(ys)-m), min(W, max(xs)+m), min(Hh, max(ys)+m))

def fit_h(im, h):
    return im.resize((int(im.width*h/im.height), h), Image.LANCZOS)

def outline(im, color=(210, 40, 40)):
    px = im.load(); W, Hh = im.size
    out = im.copy(); po = out.load()
    for y in range(1, Hh-1):
        for x in range(1, W-1):
            r, g, b = px[x, y][:3]
            if (r-b) > 22 or (r-g) > 18:
                if not any(((px[x+dx, y+dy][0]-px[x+dx, y+dy][2]) > 22 or (px[x+dx, y+dy][0]-px[x+dx, y+dy][1]) > 18)
                           for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                    po[x, y] = color
    return out

def row(refq, disp_path, mask_path, label):
    ri = ref_img(refq)
    r = fit_h(ri.crop(subj_bbox(ri, True)), H)
    mk = Image.open(mask_path).convert("RGBA")
    bb = subj_bbox(mk, False)
    m = fit_h(Image.open(disp_path).convert("RGB").crop(bb), H)
    mkc = mk.crop(bb).resize((m.width, m.height), Image.LANCZOS)
    ov = outline(r).copy(); op = ov.load(); kp = mkc.load()
    for y in range(min(ov.height, mkc.height)):
        for x in range(min(ov.width, mkc.width)):
            if kp[x, y][3] > 128:
                op[x, y] = (60, 150, 235)
    W3 = r.width+m.width+ov.width+40
    sheet = Image.new("RGB", (W3, H+8), (250, 250, 250))
    sheet.paste(r, (0, 4)); sheet.paste(m, (r.width+20, 4)); sheet.paste(ov, (r.width+m.width+40, 4))
    print(f"{label}: 原圖 {r.width}x{r.height} 模型 {m.width}x{m.height}")
    return sheet

f = row("front", OUT+f"{VER}_front_lit.png", OUT+f"{VER}_front_ortho.png", "正面")
s = row("left",  OUT+f"{VER}_side_lit.png",  OUT+f"{VER}_side_ortho.png",  "側面")
W = max(f.width, s.width)
sheet = Image.new("RGB", (W, f.height+s.height+10), (255, 255, 255))
sheet.paste(f, (0, 0)); sheet.paste(s, (0, f.height+10))
sheet.save(OUT+f"{VER}_compare_sheet.png")
print("已存", OUT+f"{VER}_compare_sheet.png", sheet.size)
