# export_3d.py — 把 RELEASE v1 匯出成通用 3D 格式
import bpy, os, math, mathutils

OUT = "/home/oa312/workspace/sheep_3d"
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT, "release_v1", "sheep_RELEASE_v1.blend"))
scene = bpy.context.scene
bpy.context.view_layer.update()

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
tri = 0
for o in meshes:
    tri += sum(len(p.vertices) - 2 for p in o.data.polygons)
print(f"網格物件 {len(meshes)}  三角面 {tri}  材質 {len(bpy.data.materials)}")

mn = [1e9]*3; mx = [-1e9]*3
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
H = mx[2] - mn[2]
print(f"尺寸 X {mx[0]-mn[0]:.4f}  Y {mx[1]-mn[1]:.4f}  Z {H:.4f}（模型單位）")

for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]

# ---- 1. GLB（材質完整，最通用）----
try:
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "sheep_RELEASE_v1.glb"),
                              export_format='GLB', use_selection=True,
                              export_cameras=False, export_lights=False,
                              export_apply=True)
    print("GLB ok")
except Exception as e:
    print("GLB FAIL:", e)

# ---- 2. OBJ + MTL ----
try:
    bpy.ops.wm.obj_export(filepath=os.path.join(OUT, "sheep_RELEASE_v1.obj"),
                          export_selected_objects=True, export_materials=True,
                          export_uv=False, export_normals=True, apply_modifiers=True)
    print("OBJ ok")
except Exception as e:
    print("OBJ FAIL:", e)

# ---- 3. STL（單一網格；原始尺寸）----
bpy.ops.object.select_all(action='DESELECT')
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
joined = bpy.context.active_object
joined.name = "Sheep"
try:
    bpy.ops.wm.stl_export(filepath=os.path.join(OUT, "sheep_RELEASE_v1.stl"),
                          export_selected_objects=True, global_scale=1.0, ascii_format=False)
    print("STL ok")
except Exception as e:
    print("STL FAIL:", e)

# ---- 4. STL（列印用：總高 100 mm）----
k = 100.0 / H
joined.scale = (k, k, k)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
try:
    bpy.ops.wm.stl_export(filepath=os.path.join(OUT, "sheep_RELEASE_v1_print_100mm.stl"),
                          export_selected_objects=True, global_scale=1.0, ascii_format=False)
    print(f"STL(100mm) ok  scale={k:.4f}")
except Exception as e:
    print("STL100 FAIL:", e)

# ---- 5. PLY（純幾何，方便寫程式讀）----
try:
    bpy.ops.wm.ply_export(filepath=os.path.join(OUT, "sheep_RELEASE_v1.ply"),
                          export_selected_objects=True)
    print("PLY ok")
except Exception as e:
    print("PLY FAIL:", e)

print("最終 joined 頂點", len(joined.data.vertices), "面", len(joined.data.polygons))
