# 顏色驗收：把原圖的取樣區映射到渲染圖座標，比對平均色
from PIL import Image

OUT = "/home/oa312/workspace/sheep_3d/"
ref = Image.open(OUT+"refs/ref_4views.jpg").convert("RGB"); rp = ref.load()

def bbox_alpha(path):
    im = Image.open(path).convert("RGBA"); px = im.load()
    xs = []; ys = []
    for y in range(0, im.height, 2):
        for x in range(0, im.width, 2):
            if px[x, y][3] > 128:
                xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)

rb = (89, 87, 389, 559)                 # 原圖正面身體 bbox
mb = bbox_alpha(OUT+"v7_front_ortho.png")
print("原圖身體 bbox", rb, " 渲染身體 bbox", mb)
sx = (mb[2]-mb[0])/(rb[2]-rb[0]); sy = (mb[3]-mb[1])/(rb[3]-rb[1])
print(f"映射比例 sx={sx:.4f} sy={sy:.4f}")

def avg(px, box, skip_dark=True, maxsum=430):
    rs=gs=bs=n=0
    for y in range(int(box[1]), int(box[3])):
        for x in range(int(box[0]), int(box[2])):
            c = px[x, y][:3]
            if skip_dark and sum(c) < maxsum:
                continue
            rs+=c[0]; gs+=c[1]; bs+=c[2]; n+=1
    return (rs//n, gs//n, bs//n) if n else None

m = Image.open(OUT+"v7_front_lit.png").convert("RGB"); mp = m.load()
REG = {"身體腰": (150,280,330,330), "身體下左": (150,380,220,440),
       "腿2": (244,505,253,545), "臉中": (200,165,250,180)}
print(f"\n{'部位':10s} {'原圖':18s} {'渲染':18s} 差異")
for k, b in REG.items():
    rc = avg(rp, b)
    mbox = (mb[0]+(b[0]-rb[0])*sx, mb[1]+(b[1]-rb[1])*sy, mb[0]+(b[2]-rb[0])*sx, mb[1]+(b[3]-rb[1])*sy)
    mc = avg(mp, mbox)
    if rc and mc:
        d = tuple(mc[i]-rc[i] for i in range(3))
        print(f"{k:10s} {str(rc):18s} {str(mc):18s} {d}")

# 背面：尾巴
rbk = (516, 87, 813, 559)
mbk = bbox_alpha(OUT+"v7_back_ortho.png") if __import__("os").path.exists(OUT+"v7_back_ortho.png") else None
bk = Image.open(OUT+"v7_back_lit.png").convert("RGB"); bp = bk.load()
tb = (655, 425, 685, 455)
print("\n尾巴 原圖", avg(rp, tb, skip_dark=False), " (背面渲染無 mask 對照，僅目視)")
