# sheep_v4.py — v3 + 臉部：tan 橢圓色塊（貼合頭部曲面）＋兩眼＋鼻線＋嘴弧
import bpy, math, os, mathutils

S = 0.005556; K = 1.1057; CY = 233.0
Z_BELLY = 0.417; BODY_H = 2.150; Z_TOP = Z_BELLY + BODY_H
OUT = "/home/oa312/workspace/sheep_3d"

FRONT = [(97,20),(107,30),(117,40),(127,47),(137,53),(147,59),(157,66),(167,79),
 (177,85),(187,91),(197,98),(207,106),(217,109),(227,115),(237,120),(247,125),
 (257,129),(267,132),(277,135.5),(287,138.5),(297,141.5),(307,143.5),(317,145),
 (327,146.5),(337,147.5),(347,148),(357,148),(367,147.5),(377,146.5),(387,145),
 (397,143),(407,140.5),(417,137),(427,132.5),(437,127.5),(447,120.5),(457,111.5),
 (467,100.5),(477,85),(484,76)]
SIDE = [(654,315,291),(664,338,264),(674,348,251),(684,358,241),(694,370,233),
 (704,380,227),(714,389,221),(724,395,215),(734,398,208),(744,397,200),
 (754,392,193),(764,352,184),(774,354,175),(784,354,165),(794,355,154),
 (804,357,144),(814,359,135),(824,361,127),(834,363,120),(844,365,113),
 (854,366,107),(864,367,103),(874,368,99),(884,369,96),(894,369,96),
 (904,368,96),(914,368,96),(924,366,96),(934,365,96),(944,363,96),
 (954,359,96),(964,356,97),(974,350,104),(984,344,110),(994,336,117),(1004,328,127)]

def smooth_col(tbl, idx, passes=1):
    out = [list(r) for r in tbl]
    for _ in range(passes):
        vals = [r[idx] for r in out]; new = vals[:]
        for i in range(1, len(vals)-1):
            new[i] = (vals[i-1] + 2*vals[i] + vals[i+1])/4
        for i, r in enumerate(out):
            r[idx] = new[i]
    return [tuple(r) for r in out]

FRONT = smooth_col(FRONT, 1, 1)
SIDE = smooth_col(SIDE, 1, 2); SIDE = smooth_col(SIDE, 2, 2)

def catmull(tbl, key, idx):
    if key <= tbl[0][0]: return tbl[0][idx]
    if key >= tbl[-1][0]: return tbl[-1][idx]
    for i in range(len(tbl)-1):
        if tbl[i][0] <= key <= tbl[i+1][0]:
            p0 = tbl[max(i-1, 0)][idx]; p1 = tbl[i][idx]
            p2 = tbl[i+1][idx]; p3 = tbl[min(i+2, len(tbl)-1)][idx]
            t = (key - tbl[i][0])/(tbl[i+1][0]-tbl[i][0])
            return 0.5*((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t*t*t)

def cross_section(u):
    u = max(0.0, min(1.0, u))
    z = Z_BELLY + u*BODY_H
    hw = catmull(FRONT, 484 - u*387.0, 1)*S
    ys = 1004 - u*350.0
    yf = (catmull(SIDE, ys, 1)-CY)*K*S; yb = (catmull(SIDE, ys, 2)-CY)*K*S
    return hw, (yf+yb)/2, (yf-yb)/2, z

def surf_front(x, z):
    """頭部前表面在 (x, z) 的 Y 座標"""
    hw, yc, rd, _ = cross_section((z - Z_BELLY)/BODY_H)
    t = min(abs(x)/hw, 0.9995)
    return yc + rd*math.sqrt(1 - t*t)

# ---------- 場景 ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene; objs = []
groups = {}   # 物件 -> 材質名

NSEG, NRING = 80, 96
verts, faces = [], []
CAP_B = [(-0.10, 1.00), (-0.28, 0.92), (-0.55, 0.72), (-0.80, 0.40)]
hw0, yc0, rd0, z0 = cross_section(0.0)
base_idx = len(verts); verts.append((0.0, yc0, z0 - 0.104))
for u, sc in CAP_B:
    zz = z0 + u*0.16
    for j in range(NSEG):
        t = 2*math.pi*j/NSEG
        verts.append((hw0*sc*math.cos(t), yc0 + rd0*sc*math.sin(t), zz))
b0 = 1
for i in range(NRING+1):
    u = i/NRING
    hw, yc, rd, z = cross_section(u)
    for j in range(NSEG):
        t = 2*math.pi*j/NSEG
        verts.append((hw*math.cos(t), yc + rd*math.sin(t), z))
# 頂部圓弧收尾（4 環 + 頂點）：消掉平頂折角
hw_t, yc_t, rd_t, z_t = cross_section(1.0)
NCAP = 5
for k in range(1, NCAP+1):
    ang = (k/NCAP)*(math.pi/2)
    sc = math.cos(ang)
    for j in range(NSEG):
        t = 2*math.pi*j/NSEG
        verts.append((hw_t*sc*math.cos(t), yc_t + rd_t*sc*math.sin(t), z_t + 0.055*math.sin(ang)))
top_c = len(verts)
verts.append((0.0, yc_t, z_t + 0.055))
for j in range(NSEG):
    faces.append((base_idx, b0+(j+1) % NSEG, b0+j))
all_rows = [b0 + k*NSEG for k in range(len(CAP_B))] + [b0 + len(CAP_B)*NSEG + k*NSEG for k in range(NRING+1+NCAP)]
for r in range(len(all_rows)-1):
    a, b = all_rows[r], all_rows[r+1]
    for j in range(NSEG):
        j2 = (j+1) % NSEG
        faces.append((a+j, a+j2, b+j2, b+j))
t0 = all_rows[-1]
for j in range(NSEG):
    faces.append((top_c, t0+j, t0+(j+1) % NSEG))
me = bpy.data.meshes.new("Body"); me.from_pydata(verts, [], faces); me.validate(); me.update()
body = bpy.data.objects.new("Body", me); scene.collection.objects.link(body)
objs.append(body); groups[body.name] = "Wool"

def add_ellipsoid(name, loc, scale, rot=(0,0,0), seg=24, ring=12, mat="Clay"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=1.0, location=loc)
    o = bpy.context.active_object; o.name = name; o.scale = scale; o.rotation_euler = rot
    objs.append(o); groups[name] = mat; return o

LEG_R = 0.045; LEG_TOP = 0.62
for sx, sy, tag in [(0.098, 0.35, "F"), (-0.098, 0.35, "F"), (0.336, -0.45, "B"), (-0.336, -0.45, "B")]:
    side = "L" if sx > 0 else "R"
    h = LEG_TOP - LEG_R
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=LEG_R, depth=h, location=(sx, sy, LEG_R + h/2))
    cyl = bpy.context.active_object; cyl.name = f"Leg_{tag}{side}"
    objs.append(cyl); groups[cyl.name] = "Leg"
    add_ellipsoid(f"Foot_{tag}{side}", (sx, sy, LEG_R), (LEG_R,)*3, seg=20, ring=10, mat="Leg")

for sx in (1, -1):
    add_ellipsoid("Ear_L" if sx > 0 else "Ear_R", (sx*0.275, 0.28, 2.400),
                  (0.070, 0.030, 0.184), rot=(math.radians(12), math.radians(37*sx), 0), mat="Tan")
# 尾巴：捲曲小尾（沿圓弧路徑串珠，由粗到細；基部貼臀）
CURL_C, CURL_R = (-0.888, 0.862), 0.058
for i in range(22):
    t = i/21
    th = math.radians(-105 + t*230)
    r = 0.028*(1 - 0.46*t)
    add_ellipsoid(f"Tail_{i:02d}", (0.0, CURL_C[0] + CURL_R*math.cos(th), CURL_C[1] + CURL_R*math.sin(th)),
                  (r,)*3, seg=14, ring=8, mat="Tail")

# ---------- 臉部 ----------
FACE_CZ, FACE_A, FACE_B = 2.220, 0.183, 0.230
OFF = 0.008
NSK, NRING2 = 48, 6
verts, faces = [], []
verts.append((0.0, surf_front(0.0, FACE_CZ) + OFF, FACE_CZ))
ring_starts = []
for k in range(1, NRING2+1):
    r = k/NRING2
    ring_starts.append(len(verts))
    for j in range(NSK):
        t = 2*math.pi*j/NSK
        x = FACE_A*r*math.cos(t); z = FACE_CZ + FACE_B*r*math.sin(t)
        verts.append((x, surf_front(x, z) + OFF, z))
# 裙邊（往殼內縮）
skirt = []
for j in range(NSK):
    x = FACE_A*math.cos(2*math.pi*j/NSK); z = FACE_CZ + FACE_B*math.sin(2*math.pi*j/NSK)
    skirt.append(len(verts)); verts.append((x, surf_front(x, z) - 0.030, z))
for j in range(NSK):
    j2 = (j+1) % NSK
    faces.append((0, ring_starts[0]+j, ring_starts[0]+j2))
for k in range(len(ring_starts)-1):
    a, b = ring_starts[k], ring_starts[k+1]
    for j in range(NSK):
        j2 = (j+1) % NSK
        faces.append((a+j, b+j, b+j2, a+j2))
a = ring_starts[-1]
for j in range(NSK):
    j2 = (j+1) % NSK
    faces.append((a+j, skirt[j], skirt[j2], a+j2))
me = bpy.data.meshes.new("Face"); me.from_pydata(verts, [], faces); me.validate(); me.update()
face = bpy.data.objects.new("Face", me); scene.collection.objects.link(face)
for p in face.data.polygons: p.use_smooth = True
objs.append(face); groups["Face"] = "Tan"

EYE_X, EYE_Z, EYE_R = 0.075, 2.290, 0.015
for sx in (1, -1):
    y = surf_front(sx*EYE_X, EYE_Z) - 0.006
    add_ellipsoid("Eye_L" if sx > 0 else "Eye_R", (sx*EYE_X, y, EYE_Z), (EYE_R,)*3, mat="Dark")

def bead_line(name, pts, r, mat="Dark"):
    for i, (x, z) in enumerate(pts):
        y = surf_front(x, z) - r*0.45
        add_ellipsoid(f"{name}_{i}", (x, y, z), (r,)*3, seg=12, ring=8, mat=mat)

def densify(pts, k):
    out = []
    for i in range(len(pts)-1):
        (x0, z0), (x1, z1) = pts[i], pts[i+1]
        for j in range(k):
            f = j/k
            out.append((x0+(x1-x0)*f, z0+(z1-z0)*f))
    out.append(pts[-1]); return out

bead_line("Nose", densify([(0.0, 2.025 - i*(2.025-1.985)/4) for i in range(5)], 4), 0.0070)
bead_line("Mouth", densify([(x, 1.968 + 0.008*(x/0.045)**2) for x in (-0.045, -0.028, -0.014, 0.0, 0.014, 0.028, 0.045)], 4), 0.0060)

# ---------- 材質 ----------
def mkmat(name, color, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    return m

MATS = {"Wool": mkmat("Wool", (0.9647, 0.8228, 0.6308), 0.62),   # 身體 251,234,208
        "Tan":  mkmat("Tan",  (0.8469, 0.6724, 0.4678), 0.60),   # 臉/耳 237,214,182
        "Leg":  mkmat("Leg",  (0.8390, 0.3050, 0.1360), 0.45),   # 腿 236,150,103
        "Tail": mkmat("Tail", (0.4020, 0.1410, 0.0530), 0.50),   # 尾棕
        "Dark": mkmat("Dark", (0.0612, 0.0319, 0.0212), 0.40)}   # 眼/鼻/嘴 70,50,40
for o in objs:
    o.data.materials.append(MATS[groups[o.name]])
    if o.name != "Face":
        for p in o.data.polygons: p.use_smooth = True

bpy.context.view_layer.update()
mn = [1e9]*3; mx = [-1e9]*3
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
CZ = (mn[2]+mx[2])/2
print("== v4 模型範圍 ==")
print(f"X[{mn[0]:+.3f},{mx[0]:+.3f}] Y[{mn[1]:+.3f},{mx[1]:+.3f}] Z[{mn[2]:+.3f},{mx[2]:+.3f}]")
print(f"總高 {mx[2]-mn[2]:.3f}  寬 {mx[0]-mn[0]:.3f}  深 {mx[1]-mn[1]:.3f}")
print(f"臉部：中心 z={FACE_CZ} 半寬 {FACE_A} 半高 {FACE_B}  表面Y={surf_front(0,FACE_CZ):.4f}")
print(f"眼睛：x=±{EYE_X} z={EYE_Z} r={EYE_R}  物件數 {len(objs)}")

# ---------- 算圖 ----------
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Khronos PBR Neutral'
cam_data = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam); scene.camera = cam

def shoot(name, res, ortho, loc, rot, samples=32, lens=50):
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.cycles.samples = samples
    cam_data.type = 'ORTHO' if ortho else 'PERSP'
    if ortho: cam_data.ortho_scale = ortho
    else: cam_data.lens = lens
    cam.location = loc; cam.rotation_euler = rot
    scene.render.filepath = os.path.join(OUT, name)
    bpy.ops.render.render(write_still=True)
    print("rendered", name)

OS = 2.90
scene.render.film_transparent = True
shoot("v11_front_ortho.png", (800, 1200), OS, (0, 8, CZ), (math.radians(90), 0, math.radians(180)), samples=24)
shoot("v11_side_ortho.png", (800, 1200), OS, (8, 0, CZ), (math.radians(90), 0, math.radians(90)), samples=24)
scene.render.film_transparent = False
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.84, 0.84, 0.85, 1)
for nm, loc, power, size in [("Key", (2.6, 3.4, 4.6), 330, 3.0), ("Fill", (-3.2, 2.2, 1.4), 150, 4.0), ("Rim", (-0.5, -4.0, 3.2), 90, 3.0)]:
    ld = bpy.data.lights.new(nm, 'AREA'); ld.energy = power; ld.size = size
    lo = bpy.data.objects.new(nm, ld); scene.collection.objects.link(lo); lo.location = loc
    d = mathutils.Vector((0, 0, CZ)) - mathutils.Vector(loc)
    lo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
shoot("v11_front_lit.png", (800, 1200), OS, (0, 8, CZ), (math.radians(90), 0, math.radians(180)), samples=64)
shoot("v11_back_lit.png", (800, 1200), OS, (0, -8, CZ), (math.radians(90), 0, 0), samples=48)
shoot("v11_side_lit.png", (800, 1200), OS, (8, 0, CZ), (math.radians(90), 0, math.radians(90)), samples=48)
shoot("v11_persp_front.png", (900, 1200), 0, (0.9, 6.6, 2.4), (math.radians(80), 0, math.radians(172)), samples=110)
shoot("v11_face.png", (900, 900), 0, (0.55, 3.3, 2.75), (math.radians(78), 0, math.radians(168)), samples=110, lens=85)
scene.render.use_freestyle = True
scene.render.line_thickness_mode = 'ABSOLUTE'
scene.render.line_thickness = 1.3
fs = scene.view_layers[0].freestyle_settings
ls = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("LS")
ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True
_lsty = bpy.data.linestyles.new("OutlineStyle"); _lsty.color = (0.46, 0.29, 0.20); _lsty.thickness = 1.3
ls.linestyle = _lsty
shoot("v11_outline.png", (900, 1200), 0, (0.9, 6.6, 2.4), (math.radians(80), 0, math.radians(172)), samples=64)
scene.render.use_freestyle = False
shoot("v11_outline_front.png", (800, 1200), OS, (0, 8, CZ), (math.radians(90), 0, math.radians(180)), samples=48)
for lo in bpy.data.objects:
    if lo.type == 'LIGHT':
        lo.hide_render = True
world.node_tree.nodes["Background"].inputs[0].default_value = (1.0, 1.0, 1.0, 1)
scene.view_settings.view_transform = 'Standard'; scene.view_settings.exposure = 0.0
shoot("v11_flat_front.png", (800, 1200), OS, (0, 8, CZ), (math.radians(90), 0, math.radians(180)), samples=48)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "sheep_v11.blend"))
print("done")
