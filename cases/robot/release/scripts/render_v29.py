import bpy
from mathutils import Vector
LIGHTS = [((-4.5,-5.8,4.6), 950,12.0,'Key'), (( 6.8,-3.2,0.9), 750,16.0,'Fill'),
          (( 4.2,-4.6,-2.0),500,16.0,'FillLow'), ((-1.0, 6.6,4.6), 500, 8.0,'Rim'),
          (( 0.6, 0.6,8.2), 350,12.0,'Top')]
WORLD = ((0.030,0.030,0.032), (0.140,0.140,0.146))
bpy.ops.wm.open_mainfile(filepath='/home/oa312/workspace/droplet_shell_model_v29_detail.blend')
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
sc.render.engine='CYCLES'; sc.cycles.device='CPU'
sc.render.image_settings.file_format='PNG'
for cand in ('Khronos PBR Neutral','AgX'):
    try: sc.view_settings.view_transform=cand; break
    except Exception: pass
def shot(nm,loc,tgt,res=900,samples=250,ortho=None,lens=50):
    sc.render.resolution_x=res; sc.render.resolution_y=res; sc.cycles.samples=samples
    if ortho: cd.type='ORTHO'; cd.ortho_scale=ortho
    else:     cd.type='PERSP'; cd.lens=lens
    loc=Vector(loc); tgt=Vector(tgt)
    cam.location=loc; cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath='/home/oa312/workspace/'+nm
    bpy.ops.render.render(write_still=True); print("OK",nm,flush=True)

CZ=0.179
# 左右側面（同比例）
shot('v29_side_R',(8.0,0.0,CZ),(0,0,CZ),ortho=5.40)
shot('v29_side_L',(-8.0,0.0,CZ),(0,0,CZ),ortho=5.40)
# 兩側近照（同 v28 相機，左右鏡像）
shot('v29_bottom_R',(2.97,-1.05,-0.75),(1.02,0.0,-0.825),res=600,samples=180,lens=85)
shot('v29_bottom_L',(-2.97,-1.05,-0.75),(-1.02,0.0,-0.825),res=600,samples=180,lens=85)
# 無板縫對照（渲染實測用）
for nm in ('PanelSeam_R','PanelSeam_L'): bpy.data.objects[nm].hide_render=True
shot('v29_noseam_R',(2.97,-1.05,-0.75),(1.02,0.0,-0.825),res=600,samples=180,lens=85)
shot('v29_noseam_L',(-2.97,-1.05,-0.75),(-1.02,0.0,-0.825),res=600,samples=180,lens=85)
for nm in ('PanelSeam_R','PanelSeam_L'): bpy.data.objects[nm].hide_render=False
# 最終四視圖
shot('v29_ortho_front',(0.0,-8.0,CZ),(0,0,CZ),ortho=5.40)
shot('v29_ortho_back', (0.0, 8.0,CZ),(0,0,CZ),ortho=5.40)
shot('v29_front_persp',(-5.6,-5.6,CZ+1.75),(0,0,CZ-0.03),lens=50)
print("DONE",flush=True)
