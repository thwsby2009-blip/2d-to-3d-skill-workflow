# 本次整理的驗證記錄

原整理日期：2026-11-05。BIM／IFC 延伸驗證更新：2026-11-06。

| 檢查 | 結果 |
|---|---|
| Python 語法 | 18 個 Python 檔案通過 AST 解析 |
| 入口路徑 | robot build、sheep build 改寫後程式可編譯；robot render 的模型前置條件已檢查 |
| 機器人實際重建 | WSL Ubuntu、Blender 5.0.1 執行 `robot build` 成功，模型輸出至 `build/robot/` |
| 板縫數值 | R/L 終點分別為 −0.7291／−0.7290，與凹槽 A 差值分別約 0.0001／0.0000；每側四顆鉚釘 |
| 原正式版機器人雜湊 | `9989719fdadc1ab3fbb88b8cbbadeeca0be4600573371936d7f40e471d0d7cea`，與來源說明一致 |
| 原正式版綿羊雜湊 | `44d451959062bf5b17e4a6805762099af3997a2b39bd7ad5b27c756d2a1867fc`，與來源說明一致 |
| 綿羊 GLB | magic 為 glTF、版本 2、宣告長度與實際 757,576 bytes 一致；僅驗證檔頭，未做完整匯入測試 |
| 桌面匯出交付包 | `sheep_3D_RELEASE_v1` 中的 GLB、OBJ、MTL、PLY、一般 STL 與 100mm STL，六個檔案 SHA-256 皆與儲存庫 export 目錄一致 |
| GLB 回讀圖片 | 已目視檢查桌面交付包的 `glb_check_sheet.png`；圖片檢查不代表本次重新執行匯入驗證 |
| README 與整理文件的本地 Markdown 連結 | 目標檔案均存在 |
| 封存圖片目視檢查 | 機器人正式版透視與綿羊原圖／模型／疊圖對照已查看 |

## BIM／IFC 延伸驗證

| 檢查 | 結果 |
|---|---|
| IFC 解析環境 | `ifcopenshell 0.9.0.post1` pip wheel 可直接開啟 IFC、擷取幾何、匯出 OBJ、計算 bounding box 與視覺化，不依賴 Blender BIM 外掛 |
| IFC 規格與結構 | IFC2X3 CoordinationView；Project → Site → Building → Storey → 元件 |
| 型別關係 | occurrence 為 `IfcFlowTerminal`，type 為 `IfcSanitaryTerminalType`；依 IFC2X3 規則不能只讀 occurrence 判斷精確類別 |
| 幾何 | 單一 faceted Brep，3,108 頂點、6,212 三角面 |
| 尺寸交叉驗證 | 幾何 bbox 約 368 × 580 × 421 mm；屬性為 370 × 580 × 420 mm，差異不超過約 2 mm |
| 屬性完整度 | 60 個欄位中 47 個有值、13 個空白；欄位填寫率約 78.3%，未宣稱為整體 BIM 品質分數 |
| 分類資訊 | 觀察到 10 套分類／代碼表示，需要保存系統、版本、代碼與名稱後再做 mapping |
| 組成完整性 | 陶瓷本體輪廓與官方產品照相符，但目視缺少座圈與上蓋；尚未確認供應商定義的交付範圍 |

完整方法、結果與限制見 [BIM／IFC 延伸驗證報告](BIM_IFC_VALIDATION.md)。第三方產品照與原始下載包未納入本儲存庫。

未重新執行完整綿羊建模與批次渲染，未重新計算歷史輪廓誤差，也未重新驗收所有機器人零件。正文中的歷史驗收數據依原始正式版與交接記錄標示。

`MANIFEST.sha256` 包含 51 個來源資產，涵蓋案例模型、圖像、腳本、技能快照與原技術文件。重建時的 Blender 儲存檔可能包含不同的序列化資訊，因此重建結果未要求與封存 `.blend` 位元組完全相同。
