# Blender 5 API 與工具陷阱（寫腳本前先讀）

## API

- `scene.render.file_format` 不存在 → 用 `scene.render.image_settings.file_format`。
- `obj.select` 不存在 → 用 `bpy.context.view_layer.objects.active` + 選取 API。
- `Material.use_nodes` 已棄用（僅 warning）；`'Sheen'` 輸入不存在。
- **在 `bpy.ops.wm.open_mainfile()` 之前建立的 datablock 會失效** → 材質必須在開檔之後才建立。
- `bmesh.ops.bevel(..., affect='EDGES')` 可用；`bm.free()` 之後不能再讀 `len(bm.verts)`（先存變數）。

## 工具

- shell heredoc（`<<'PY'`）會被 Hermes 擋 → 一律 `write_file` 寫腳本 + `patch` 改，再 `blender -b -P` 執行。
- 系統 python3（有 PIL、無 numpy）與 Blender python（有 mathutils、無 PIL）分工：像素量測在外、幾何在內，以小 JSON 檔傳值。
- 渲染只能 Cycles CPU；銀色金屬在近黑環境會渲染成黑色 → 場景必須有漸層環境光。
- 先估渲染時間：3~5 視角 × 110 samples 約 3~6 分鐘，terminal timeout 設 550~600。
