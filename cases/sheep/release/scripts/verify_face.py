# 驗收：渲染圖裡的 tan 臉塊/眼球 相對尺寸，與原圖量測值對比（全部以「身體總高」為單位）
from PIL import Image

OUT = "/home/oa312/workspace/sheep_3d/"

def tan_bbox(im, pred):
    px = im.load(); W, H = im.size
    xs, ys = [], []
    for y in range(H):
        for x in range(W):
            if pred(px[x, y][:3]):
                xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None

def body_bbox_alpha(path):
    im = Image.open(path).convert("RGBA"); px = im.load()
    xs, ys = [], []
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3] > 128:
                xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)

# 原圖（正面）：tan 臉塊與身體
ref = Image.open(OUT+"refs/ref_4views.jpg").convert("RGB")
refc = ref.crop((0, 60, 448, 590))
rt = tan_bbox(refc, lambda c: abs(c[0]-237) < 22 and abs(c[1]-214) < 22 and abs(c[2]-182) < 26)
rbody = (89, 87-60, 389, 559-60)
print("原圖(正面) tan 臉塊 bbox:", rt)
rh = rbody[3]-rbody[1]+1
print(f"  以身高({rh}px)為單位：左 {(rt[0]-rbody[0])/rh:.3f}  右 {(rt[2]-rbody[0])/rh:.3f}  上 {(rt[1]-rbody[1])/rh:.3f}  下 {(rt[3]-rbody[1])/rh:.3f}")
print(f"  臉塊寬/身高 {(rt[2]-rt[0]+1)/rh:.3f}   高/身高 {(rt[3]-rt[1]+1)/rh:.3f}")

# 模型渲染（正面 lit）
m = Image.open(OUT+"v5_front_lit.png").convert("RGB")
mb = body_bbox_alpha(OUT+"v5_front_ortho.png")
print("\n模型(正面) 身體 bbox:", mb)
mh = mb[3]-mb[1]+1
mt = tan_bbox(m, lambda c: c[0] > 150 and c[0]-c[2] > 45 and c[0]-c[1] > 20 and c[1] > 120)
print("模型 tan 臉塊 bbox:", mt)
if mt:
    print(f"  以身高({mh}px)為單位：左 {(mt[0]-mb[0])/mh:.3f}  右 {(mt[2]-mb[0])/mh:.3f}  上 {(mt[1]-mb[1])/mh:.3f}  下 {(mt[3]-mb[1])/mh:.3f}")
    print(f"  臉塊寬/身高 {(mt[2]-mt[0]+1)/mh:.3f}   高/身高 {(mt[3]-mt[1]+1)/mh:.3f}")

# 眼睛（暗點）
def dark_pts(im, box):
    px = im.load(); pts = []
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            r, g, b = px[x, y][:3]
            if r+g+b < 260:
                pts.append((x, y))
    return pts

print("\n--- 眼球比較 ---")
re_ = dark_pts(refc, (rt[0], rt[1], rt[2], rt[3]))
if re_:
    exs = [p[0] for p in re_]; eys = [p[1] for p in re_]
    print(f"原圖眼球像素 {len(re_)}  範圍 x[{min(exs)},{max(exs)}] 中心x {(min(exs)+max(exs))/2:.0f} (臉中心 {(rt[0]+rt[2])/2:.0f})")
    print(f"  眼中心高度/身高 {(sum(eys)/len(eys)-rbody[1])/rh:.3f}（從頂）")
me_ = dark_pts(m, mt) if mt else []
if me_:
    exs = [p[0] for p in me_]; eys = [p[1] for p in me_]
    print(f"模型眼球像素 {len(me_)}  範圍 x[{min(exs)},{max(exs)}] 中心x {(min(exs)+max(exs))/2:.0f} (臉中心 {(mt[0]+mt[2])/2:.0f})")
    print(f"  眼中心高度/身高 {(sum(eys)/len(eys)-mb[1])/mh:.3f}（從頂）")
