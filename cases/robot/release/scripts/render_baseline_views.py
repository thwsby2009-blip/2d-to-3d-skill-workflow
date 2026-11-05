import bpy
from mathutils import Vector

# =====================================================================
#  BASELINE 標準視圖：正面正交 / 背面正交 / 側面正交 / 前方透視
#  - 正交三視圖用「同一 ortho_scale」，且比例一致
#  - 每張皆完整包含 葉尖(z=+2.718) / 雙手(x=±1.19) / 腳底(z=-2.360)
#  - 材質、燈光沿用目前設定
# =====================================================================
BLEND = '/home/oa312/workspace/droplet_shell_model_BASELINE.blend'
RES, SAMPLES, ORTHO = 900, 250, 5.40
LIGHTS = [((-4.5,-5.8,4.6), 950,12.0,'Key'), (( 6.8,-3.2,0.9), 750,16.0,'Fill'),
          (( 4.2,-4.6,-2.0),500,16.0,'FillLow'), ((-1.0, 6.6,4.6), 500, 8.0,'Rim'),
          (( 0.6, 0.6,8.2), 350,12.0,'Top')]
WORLD = ((0.030,0.030,0.032), (0.140,0.140,0.146))

bpy.ops.wm.open_mainfile(filepath=BLEND)
sc=bpy.context.scene
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
nt=w.node_tree; nt.nodes.clear()
o=nt.nodes.new('ShaderNodeOutputWorld'); bg=nt.nodes.new('ShaderNodeBackground')
ramp=nt.nodes.new('ShaderNodeValToRGB'); sep=nt.nodes.new('ShaderNodeSeparateXYZ')
tex=nt.nodes.new('ShaderNodeTexCoord')
nt.links.new(tex.outputs['Generated'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
nt.links.new(bg.outputs['Background'], o.inputs['Surface'])
cr=ramp.color_ramp
cr.elements[0].position=0.0; cr.elements[0].color=(*WORLD[0],1)
cr.elements[1].position=1.0; cr.elements[1].color=(*WORLD[1],1)
cd=bpy.data.cameras.new("Cam"); cam=bpy.data.objects.new("Cam",cd)
sc.collection.objects.link(cam); sc.camera=cam
for loc,e,sz,nm in LIGHTS:
    ld=bpy.data.lights.new(nm,type='AREA'); ld.energy=e; ld.size=sz; ld.shape='SQUARE'
    lo=bpy.data.objects.new(nm,ld); sc.collection.objects.link(lo); lo.location=loc
    lo.rotation_euler=(Vector((0,0,0))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=SAMPLES
sc.render.image_settings.file_format='PNG'
sc.render.resolution_x=RES; sc.render.resolution_y=RES
for cand in ('Khronos PBR Neutral','AgX'):
    try: sc.view_settings.view_transform=cand; break
    except Exception: pass
# 模型範圍檢查
allc=[]
for ob in bpy.data.objects:
    if ob.type=='MESH':
        allc += [ob.matrix_world@v.co for v in ob.data.vertices]
Z0,Z1=min(c.z for c in allc),max(c.z for c in allc)
X0,X1=min(c.x for c in allc),max(c.x for c in allc)
CZ=(Z0+Z1)/2
print(f"model extent: z[{Z0:+.3f},{Z1:+.3f}] (span {Z1-Z0:.3f})  x[{X0:+.3f},{X1:+.3f}]  centre z={CZ:+.3f}  ortho_scale={ORTHO}")

def shot(nm, loc, tgt, ortho=None, lens=50):
    if ortho: cd.type='ORTHO'; cd.ortho_scale=ortho
    else:     cd.type='PERSP'; cd.lens=lens
    loc=Vector(loc); tgt=Vector(tgt)
    cam.location=loc; cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath='/home/oa312/workspace/'+nm
    bpy.ops.render.render(write_still=True); print("OK",nm,flush=True)

shot('baseline_ortho_front', (0.0,-8.0,CZ), (0.0,0.0,CZ), ortho=ORTHO)   # 正面正交
shot('baseline_ortho_back',  (0.0, 8.0,CZ), (0.0,0.0,CZ), ortho=ORTHO)   # 背面正交
shot('baseline_ortho_side',  (8.0, 0.0,CZ), (0.0,0.0,CZ), ortho=ORTHO)   # 側面正交
shot('baseline_front_persp', (-5.6,-5.6,CZ+1.75), (0.0,0.0,CZ-0.03), lens=50)  # 前方透視
print("DONE",flush=True)
