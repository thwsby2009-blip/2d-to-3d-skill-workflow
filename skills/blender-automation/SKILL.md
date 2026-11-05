---
name: blender-automation
version: 1.0.0
author: Harry Tsai + Hermes
category: creative
description: Use when 用 Blender Python 建模或 2D 圖轉 3D。環境陷阱、參考圖 QC、數值驗收.
---

# Blender 腳本化建模（2D 參考 → 3D）

## When to Use

- 使用者要求「用 Blender 建模型／出渲染圖」或「把 2D 參考圖（單張或四視圖）轉成 3D」時。
- 任何要在本機跑 `blender -b -P` 腳本、做像素量測驗收的工作。
- 不適用：非 Blender 的 3D 交付（如 web 3D、遊戲引擎）。

## 環境（WSL 本機恆定）

- Blender 5.0.1：`/usr/bin/blender`，headless 用 `blender -b -P script.py`。無 GPU：互動視窗/EGL 不可用，渲染只能 Cycles CPU；`-b` 背景算圖完全正常。
- 系統 python3 無 numpy → 像素量測用純 PIL 迴圈。Blender 內建 python 無 PIL → 像素工作交給系統 python3，兩者用小 JSON 傳遞量測值。
- 3~5 視角 × 110 samples 約 3~6 分鐘 → terminal timeout 設 550~600。
- API 與工具陷阱清單：`references/blender5-pitfalls.md`（寫腳本前先讀）。

## 流程

### 1. 參考圖 QC（先於一切建模）

切分視圖 → 量主體 bbox 與 W/H → 一致性檢查 → 特徵量測，產出「量測基準表」（單位＝主體高 H 或寬 W 的比例，標明來源視圖）。起步用 `scripts/measure_4views.py`；配方與判定閾值見 `references/ref-image-qc.md`。

AI 生成四視圖的三類瑕疵與處理：
- **各視圖比例漂移**（都標同一尺寸實測差數 %）→ 選一張為高度基準，其餘按特徵重新正規化，並向使用者聲明決定。
- **姿勢不一致**（如側面走路姿 vs 正面站姿）→ 取合理站姿正規化（腿站直），以身體（不含腿）高度對齊基準。
- **2D 平面 vs 3D 體積矛盾**（正面臉是畫在身上的橢圓、側面卻顯示頭有體積）→ 以有體積資訊的視圖為準做 3D 形狀，正面特徵落在該 3D 形狀上。

顏色閾值一律先探測實際像素值再定，不憑感覺設。

### 2. 腳本建模

每個零件獨立命名（左右配對鏡像、莖葉類可不對稱）。每版另存新版號 .blend；**BASELINE 成功基準永不覆寫**；失敗版保留可回溯。

### 3. 逐版驗收

每版腳本結尾印數值驗證（跳階量、貼合距離、長度/角度），不靠目測。渲染後用 PIL 實測比對（投影像素列、疊圖差異）。
分兩關：**腳本執行成功 ≠ 外觀驗收通過**；後者必須渲染圖給使用者看過確認。未檢視渲染圖前不得宣稱外觀已驗證。
驗收協定細節：`references/acceptance-protocol.md`。

### 4. 凍結與交接

驗收通過即停版（停止自動追加修改），RELEASE 目錄收 .blend + 重建腳本 + 標準視圖 + release 說明。session 變長時寫 `PROJECT_STATE_*.md` 交接文件（版本歷程／量測基準／關鍵參數／教訓），後續 session 讀該檔即可續作，不必載入完整 transcript。

## 此類任務的紀律（使用者必守規則）

- 一次只改一個主要變數；A/B 並排比較。
- 連續猜錯 2 次停下要證據，不 retry。
- 部位名稱有歧義時，先在圖上 A/B 彩色標註給使用者確認，再動手。
- 尺寸疑義給模型量測數值，不用截圖估算。
- 刻意偏離原圖的參數記錄在待決事項，標明「刻意」非缺陷。
