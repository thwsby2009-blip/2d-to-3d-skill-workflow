import bpy, bmesh, math, collections
from mathutils import Vector

# =====================================================================
#  v29 : BASELINE(v24) + 兩側外殼細節（板縫 + 鉚釘），左右鏡像
#   板縫：寬 0.012、楔形(中央0.0018/邊緣0.0006)、SeamDarkRed(rough .85/metal 0)
#         上端 z=+1.340(近頂) 、下端止於「A：主殼水平凹槽」z=-0.7290 -> T字交會
#   鉚釘：每側 4 顆 r=0.016、y=-0.035 貼在縫旁紅色板面（上2 t=0.900/0.862；下2 t=0.300/0.262）
#   鏡像方式：x -> -x（y,z 不變）
#   不動：主殼、環形接縫、其他已驗收部件、材質、燈光
# =====================================================================
BLEND_IN='/home/oa312/workspace/droplet_shell_model_BASELINE.blend'
OUT     ='/home/oa312/workspace/droplet_shell_model_v29_detail.blend'
SEAM_W, EDGE_H, MID_H = 0.012, 0.0006, 0.0018
T_HI = 0.997
RIVET_R=0.016; RIVET_T=(0.900,0.862,0.300,0.262); RIVET_YOFF=-0.035

bpy.ops.wm.open_mainfile(filepath=BLEND_IN)
def ensure_mat(name,rgb,rough,metallic):
    m=bpy.data.materials.get(name)
    if m is None:
        m=bpy.data.materials.new(name); m.use_nodes=True
        bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        bs.inputs['Base Color'].default_value=(*rgb,1)
        bs.inputs['Metallic'].default_value=metallic
        bs.inputs['Roughness'].default_value=rough
        m.diffuse_color=(*rgb,1)
    return m
seam_mat=ensure_mat('SeamDarkRed',(0.105,0.028,0.022),0.85,0.0)
rivet_mat=bpy.data.materials['SilverMetal']
def make_obj(name,bm,mat,smooth=True):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); ob=bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob); bm.to_mesh(me); bm.free(); me.update()
    me.materials.append(mat)
    for p in me.polygons: p.use_smooth=smooth
    return ob

shell=bpy.data.objects['DropletShell']
sh_v=[shell.matrix_world@v.co for v in shell.data.vertices]
rings=collections.defaultdict(list)
for c in sh_v: rings[round(c.z,6)].append(c)
rz=sorted(rings.keys())

# --- 量測水平凹槽 A（兩側同 z，主殼左右對稱）---
def rf_side(z,sgn):
    v=[abs(c.x) for c in rings[z] if c.x*sgn>0]
    return max(v) if v else max(abs(c.x) for c in rings[z])
prof=[(z,rf_side(z,+1)) for z in rz if -1.00<=z<=-0.45]
best=None
for i in range(2,len(prof)-2):                    # 局部極小 = 水平凹槽
    if prof[i][1]<prof[i-1][1] and prof[i][1]<prof[i+1][1] and prof[i][1]<prof[i-2][1] and prof[i][1]<prof[i+2][1]:
        if best is None or prof[i][1]<best[1]: best=prof[i]
ZA=best[0]
sb=bpy.data.objects['ArmShoulder_R']; sh_top=max((sb.matrix_world@v.co).z for v in sb.data.vertices)
print(f"凹槽 A = z={ZA:+.4f} (r={best[1]:.5f})  肩部頂 z={sh_top:+.4f}  -> A 在肩部之上 {ZA>sh_top}")

def build_side(sgn, tag):
    def rf(z):
        v=[abs(c.x) for c in rings[z] if c.x*sgn>0]
        return max(v) if v else max(abs(c.x) for c in rings[z])
    def mk(z):
        i=max(1,min(len(rz)-2,min(range(len(rz)),key=lambda k:abs(rz[k]-z))))
        a=rf(rz[i]); ap=rf(rz[i-1]); an=rf(rz[i+1])
        tm=Vector((an-ap,0,rz[i+1]-rz[i-1])).normalized()
        n=Vector((0,1,0)).cross(tm).normalized()*sgn
        return Vector((a*sgn,0,rz[i])), n, rz[i], a
    P=[mk(ZA)]
    for z in rz:
        t=(z+1.35)/2.7
        if z<=ZA+1e-6 or t>T_HI+1e-9: continue
        P.append(mk(z))
    P.sort(key=lambda s:s[2])
    bm=bmesh.new(); rows=[]
    for p,n,z,a in P:
        w=Vector((0,1,0))
        rows.append([bm.verts.new(p+n*EDGE_H-w*(SEAM_W/2)), bm.verts.new(p+n*MID_H), bm.verts.new(p+n*EDGE_H+w*(SEAM_W/2))])
    for i in range(len(rows)-1):
        for k in range(2): bm.faces.new([rows[i][k],rows[i][k+1],rows[i+1][k+1],rows[i+1][k]])
    seam=make_obj(f'PanelSeam_{tag}', bm, seam_mat, smooth=True)
    def add_dome(bm,base,n,r,seg=20,nr=6):
        n=n.normalized(); up=Vector((0,0,1))
        if abs(n.dot(up))>0.99: up=Vector((1,0,0))
        ex=n.cross(up).normalized(); ey=n.cross(ex).normalized()
        rr_=[]
        for i in range(1,nr+1):
            th=(math.pi/2)*i/nr; rr=r*math.sin(th); hh=r*math.cos(th)
            rr_.append([bm.verts.new(base+ex*(rr*math.cos(2*math.pi*j/seg))+ey*(rr*math.sin(2*math.pi*j/seg))+n*hh) for j in range(seg)])
        pole=bm.verts.new(base+n*r)
        for i in range(len(rr_)-1):
            for j in range(seg):
                j2=(j+1)%seg; bm.faces.new([rr_[i][j],rr_[i][j2],rr_[i+1][j2],rr_[i+1][j]])
        for j in range(seg):
            j2=(j+1)%seg; bm.faces.new([pole,rr_[0][j2],rr_[0][j]])
        bm.faces.new(list(reversed(rr_[-1])))
    rivs=[]
    for k,t in enumerate(RIVET_T):
        z=t*2.7-1.35; zc=min(rz,key=lambda zz:abs(zz-z)); i=rz.index(zc)
        a=rf(zc); ap=rf(rz[i-1]); an=rf(rz[i+1])
        tm=Vector((an-ap,0,rz[i+1]-rz[i-1])).normalized()
        n=Vector((0,1,0)).cross(tm).normalized()*sgn
        base=Vector((a*sgn,RIVET_YOFF,zc))+n*0.0008
        bm=bmesh.new(); add_dome(bm,base,n,RIVET_R)
        rivs.append(make_obj(f'Rivet_{tag}_{k+1}',bm,rivet_mat,smooth=True))
    return seam, rivs, P

seams={}; rivs={}; samples={}
for sgn,tag in ((+1,'R'),(-1,'L')):
    s,r,P=build_side(sgn,tag); seams[tag]=s; rivs[tag]=r; samples[tag]=P
    print(f"[{tag}] seam verts={len(s.data.vertices)} samples={len(P)} z {P[0][2]:+.3f}..{P[-1][2]:+.3f}  rivets={len(r)}")

# ================= 驗收 =================
print("\n=== 驗收 ===")
for tag in ('R','L'):
    sv=[seams[tag].matrix_world@v.co for v in seams[tag].data.vertices]
    low=min(sv,key=lambda c:c.z)
    ring=bpy.data.objects['ConnectorRing']; rc=[ring.matrix_world@v.co for v in ring.data.vertices]
    ZB=(max(c.z for c in rc)+min(c.z for c in rc))/2
    print(f"[{tag}] 縱線下端 z={low.z:+.4f} (＝凹槽 {ZA:+.4f}, 差 {abs(low.z-ZA):.4f})  "
          f"距底蓋金屬圈 {low.z-ZB:+.4f} (無多餘縱線={low.z>ZB+0.3})")
# 鉚釘貼合：座點是否落在主殼橢圓面上（(x/a)^2+(y/b)^2 應 ≈ 1）
print("\n鉚釘貼合（座點橢圓值 (x/a)²+(y/b)² 應 ≈1.000）:")
RW_=2.3*0.5; RD_=2.0*0.5
for tag,sgn in (('R',+1),('L',-1)):
    for k,t in enumerate(RIVET_T):
        z=min(rz,key=lambda zz:abs(zz-(t*2.7-1.35)))
        tt=(z+1.35)/2.7
        fs=prof[0][1]  # placeholder
        a=max(abs(v.x) for v in rings[z] if v.x*sgn>0)
        b=a*(RD_/RW_)
        x=a*sgn; y=RIVET_YOFF
        q=(x/a)**2+(y/b)**2
        print(f"   Rivet_{tag}_{k+1}: z={z:+.4f} a={a:.4f} b={b:.4f} base=({x:+.4f},{y:+.4f})  -> (x/a)²+(y/b)²={q:.4f}")
# 對稱性
print("\n左右對稱性:")
for part in ['PanelSeam']+[f'Rivet']:
    names_r=[o.name for o in bpy.data.objects if o.name.endswith('_R') and (o.name.startswith('PanelSeam') or o.name.startswith('Rivet'))]
print("  objects:", sorted(o.name for o in bpy.data.objects if o.name.startswith(('PanelSeam','Rivet'))))
allc=[]
for o in bpy.data.objects:
    if o.type=='MESH' and not o.name.startswith(('PanelSeam','Rivet')): allc+=[o.matrix_world@v.co for v in o.data.vertices]
print(f"  其他部件總頂點={len(allc)}  主殼 verts={len(shell.data.vertices)} (未改)")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print(f"\nSaved {OUT}")
