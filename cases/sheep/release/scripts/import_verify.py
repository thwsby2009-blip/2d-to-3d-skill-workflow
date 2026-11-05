# import_verify.py — 把匯出的 GLB 匯入「乾淨場景」重新算圖，驗證匯出檔完整性
import bpy, math, os, mathutils

OUT = "/home/oa312/workspace/sheep_3d"
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.gltf(filepath=os.path.join(OUT, "sheep_RELEASE_v1.glb"))
bpy.context.view_layer.update()

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
print(f"匯入：網格 {len(meshes)}  材質 {len(bpy.data.materials)}")
mn = [1e9]*3; mx = [-1e9]*3
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
print(f"範圍 X[{mn[0]:+.3f},{mx[0]:+.3f}] Y[{mn[1]:+.3f},{mx[1]:+.3f}] Z[{mn[2]:+.3f},{mx[2]:+.3f}]")
print(f"總高 {mx[2]-mn[2]:.3f}")
mat_names = sorted(m.name for m in bpy.data.materials)
print("材質：", mat_names[:8])
# 檢查材質顏色是否跟著來
for m in bpy.data.materials:
    if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
        c = m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value
        print(f"  {m.name:22s} base=({c[0]:.4f},{c[1]:.4f},{c[2]:.4f})")

CZ = (mn[2]+mx[2])/2
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'Khronos PBR Neutral'
scene.render.film_transparent = False
w = bpy.data.worlds.new("W"); scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.86, 0.86, 0.87, 1)
for nm, loc, power, size in [("Key", (2.6, 3.4, 4.6), 330, 3.0), ("Fill", (-3.2, 2.2, 1.4), 150, 4.0), ("Rim", (-0.5, -4.0, 3.2), 90, 3.0)]:
    ld = bpy.data.lights.new(nm, 'AREA'); ld.energy = power; ld.size = size
    lo = bpy.data.objects.new(nm, ld); scene.collection.objects.link(lo); lo.location = loc
    d = mathutils.Vector((0, 0, CZ)) - mathutils.Vector(loc)
    lo.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cam_data = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cam_data)
scene.collection.objects.link(cam); scene.camera = cam

def shoot(name, loc, rot, lens=50, samples=96):
    scene.render.resolution_x, scene.render.resolution_y = 620, 800
    scene.cycles.samples = samples
    cam_data.type = 'PERSP'; cam_data.lens = lens
    cam.location = loc; cam.rotation_euler = rot
    scene.render.filepath = os.path.join(OUT, name)
    bpy.ops.render.render(write_still=True)
    print("rendered", name)

shoot("glb_check_1_front.png", (0.2, 6.8, 2.0), (math.radians(88), 0, math.radians(178)), samples=96)
shoot("glb_check_2_threequarter.png", (3.6, 5.6, 2.6), (math.radians(78), 0, math.radians(147)), samples=96)
shoot("glb_check_3_back.png", (-1.6, -6.6, 2.2), (math.radians(85), 0, math.radians(-13)), samples=96)
print("done")
