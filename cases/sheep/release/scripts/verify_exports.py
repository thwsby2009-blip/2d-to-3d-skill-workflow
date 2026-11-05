# verify_exports.py — 讀回匯出檔，驗證內容（GLB/OBJ/MTL/STL）
import json, struct, os

OUT = "/home/oa312/workspace/sheep_3d"

def fsize(p):
    return os.path.getsize(os.path.join(OUT, p))

print("=== 檔案 ===")
for f in ["sheep_RELEASE_v1.glb", "sheep_RELEASE_v1.obj", "sheep_RELEASE_v1.mtl",
          "sheep_RELEASE_v1.stl", "sheep_RELEASE_v1_print_100mm.stl", "sheep_RELEASE_v1.ply"]:
    p = os.path.join(OUT, f)
    print(f"  {f:36s} {'存在' if os.path.exists(p) else '不存在':6s} {fsize(f)/1024:8.1f} KB")

# ---- GLB ----
print("\n=== GLB ===")
with open(os.path.join(OUT, "sheep_RELEASE_v1.glb"), "rb") as fh:
    data = fh.read()
magic, ver, length = struct.unpack("<4sII", data[:12])
print(f"  magic={magic.decode()} version={ver} 宣告長度={length} 實際={len(data)} {'✅' if length == len(data) else '❌'}")
off = 12
clen, ctype = struct.unpack("<I4s", data[off:off+8])
j = json.loads(data[off+8:off+8+clen].decode("utf-8"))
print(f"  nodes={len(j.get('nodes', []))} meshes={len(j.get('meshes', []))} materials={len(j.get('materials', []))}")
print(f"  材質名：{[m.get('name') for m in j.get('materials', [])]}")
print(f"  物件名前 8 個：{[n.get('name') for n in j.get('nodes', [])][:8]}")
acc = j.get('accessors', [])
tot_v = sum(a['count'] for a in acc if a.get('type') == 'VEC3' and 'min' in a and len(a.get('min', [])) == 3)
print(f"  accessor 數={len(acc)}")

# ---- OBJ / MTL ----
print("\n=== OBJ / MTL ===")
nv = nf = 0
mtllib = None
usemtl = set()
for line in open(os.path.join(OUT, "sheep_RELEASE_v1.obj"), encoding="utf-8", errors="ignore"):
    if line.startswith("v "): nv += 1
    elif line.startswith("f "): nf += 1
    elif line.startswith("mtllib"): mtllib = line.strip().split(None, 1)[1]
    elif line.startswith("usemtl"): usemtl.add(line.strip().split(None, 1)[1])
print(f"  頂點 {nv}  面 {nf}  mtllib={mtllib}  用到的材質={sorted(usemtl)}")
mtlp = os.path.join(OUT, "sheep_RELEASE_v1.mtl")
if os.path.exists(mtlp):
    names = [l.split(None, 1)[1].strip() for l in open(mtlp, encoding="utf-8", errors="ignore") if l.startswith("newmtl")]
    print(f"  MTL 材質 {len(names)} 個：{names}")
    for l in open(mtlp, encoding="utf-8", errors="ignore"):
        if l.startswith("Kd"): print("    ", l.strip()); break

# ---- STL ----
print("\n=== STL ===")
for fn in ["sheep_RELEASE_v1.stl", "sheep_RELEASE_v1_print_100mm.stl"]:
    with open(os.path.join(OUT, fn), "rb") as fh:
        head = fh.read(84)
        ntri = struct.unpack("<I", head[80:84])[0]
        body = fh.read(ntri*50)
    xs = []; ys = []; zs = []
    for i in range(ntri):
        rec = body[i*50:(i+1)*50]
        vals = struct.unpack("<12f", rec[:48])
        for k in range(3):
            xs.append(vals[3+k*3]); ys.append(vals[4+k*3]); zs.append(vals[5+k*3])
    print(f"  {fn}: 三角面 {ntri}")
    print(f"    範圍 X[{min(xs):.3f},{max(xs):.3f}] Y[{min(ys):.3f},{max(ys):.3f}] Z[{min(zs):.3f},{max(zs):.3f}]")
    print(f"    高度 {max(zs)-min(zs):.3f}  寬 {max(xs)-min(xs):.3f}  深 {max(ys)-min(ys):.3f}")

# ---- PLY ----
print("\n=== PLY ===")
with open(os.path.join(OUT, "sheep_RELEASE_v1.ply"), "rb") as fh:
    for _ in range(12):
        line = fh.readline().decode("ascii", "ignore").strip()
        print("  ", line)
