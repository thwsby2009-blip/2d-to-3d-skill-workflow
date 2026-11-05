# 重現方式

## 環境

原始環境：WSL Ubuntu、Blender 5.0.1、Cycles CPU。量測與比圖工具使用系統 Python 及 Pillow；Blender 腳本使用其內建 Python。請先確認 `blender --version`。

在儲存庫根目錄執行 README 的三個指令。`tools/run_case.py` 支援：

| 參數 | 行為 | 輸出 |
|---|---|---|
| `robot build` | 由收錄的 BASELINE 執行 v29 外殼細節腳本 | `build/robot/droplet_shell_model_v29_detail.blend` |
| `robot render` | 讀取上述模型，執行正式視圖腳本 | `build/robot/*.png` |
| `sheep build` | 執行 v11，從內嵌輪廓表建立模型並算圖 | `build/sheep/sheep_v11.blend` 與圖片 |

`robot render` 前需先執行 `robot build`。渲染可需數分鐘，取決於 CPU 與設定。輸出目錄會重用，重跑會覆寫該目錄內同名產物；封存模型與 BASELINE 不會被此入口改寫。

## 執行入口的作用

入口讀取原始腳本，在記憶體中將原工作區路徑換為目前儲存庫的輸入與 `build/` 輸出路徑，再執行。機器人 BASELINE 的輸入單獨映射到 `cases/robot/`。原始封存腳本保持不變。

其餘封存量測、匯出與比圖腳本仍依賴原工作目錄、檔名及先前產物，未全部適配；它們是方法參考，不屬於上述三個支援入口。若需獨立使用，應先調整其路徑及準備所需產物。

## 換一個角色

現有建模腳本使用角色專屬的輪廓表與部位參數。新角色需先依技能文件執行四視圖 QC、量測、姿態對齊，再設定主體與附屬零件。這個儲存庫沒有提供任意圖片自動轉換 CLI。
