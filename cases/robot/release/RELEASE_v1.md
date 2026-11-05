# RELEASE v1 — 植物系機器人（水滴主殼）第一版完成品

> 狀態：**外觀驗收通過（使用者確認），凍結不再自動追加修改。**
> 日期：2026-09-26　｜　Blender **5.0.1**（`/usr/bin/blender`，headless `-b`）　｜　渲染 **Cycles CPU**

---

## 1. 最終檔案、重建腳本與依賴

### 成品
| 檔案 | sha256 | 說明 |
|---|---|---|
| `release_v1/droplet_shell_model_RELEASE_v1.blend` | `9989719fdadc1ab3fbb88b8cbbadeeca0be4600573371936d7f40e471d0d7cea` | **第一版完成品**（＝`droplet_shell_model_v29_detail.blend`）|

### 重建腳本
| 檔案 | 作用 |
|---|---|
| `release_v1/scripts/droplet_shell_v29.py` | **重建成品**：由 BASELINE 加入兩側板縫＋鉚釘，結尾印出驗收數值 |
| `release_v1/scripts/render_v29.py` | 產生左右側面、兩側近照、最終四視圖 |
| `release_v1/scripts/render_baseline_views.py` | 產生 BASELINE 標準視圖（不含外殼細節）|

### 必要依賴
1. **`droplet_shell_model_BASELINE.blend`**（sha256 `d4a7f41391703b54f8f09e3ebf42f2dafc8b8c542ded1592f477411740435717`）— v29 腳本的唯一輸入。
2. **Blender 5.0.1**；建置腳本只用內建的 `bmesh` / `mathutils`，**不需額外 Python 套件**。
3. 渲染：Cycles CPU（本機無 GPU）。**注意：此 build 沒有可用的 Cycles 降噪器**（8spp 開/關逐像素相同）。
4. 分析腳本（像素量測）用**系統 `python3` + PIL**；**Blender 內建 Python 沒有 PIL**。

### 重建指令
```bash
cd /home/oa312/workspace
blender -b -P release_v1/scripts/droplet_shell_v29.py      # -> droplet_shell_model_v29_detail.blend
blender -b -P release_v1/scripts/render_v29.py             # -> v29_side_R/L 等視圖
```

### BASELINE 的組成（若要從零重建）
BASELINE（=v24）＝ 主殼・五官・莖葉・腿腳（v1–v12）＋ 雙手臂夾爪（v16）＋ 背筒（v17）＋ 材質燈光（v18–v20）＋ 主殼頂部修正（v21）＋ 鼻子（v24）。
各版建置腳本 `droplet_shell_v6.py` … `droplet_shell_v24.py` 全部保留於 `/home/oa312/workspace/`，可逐版回溯。

---

## 2. 視圖（`release_v1/views/`）

| 檔案 | 內容 |
|---|---|
| `01_front_ortho.png` | 正面正交 |
| `02_back_ortho.png` | 背面正交 |
| `03_side_left_ortho.png` | 左側面正交 |
| `04_side_right_ortho.png` | 右側面正交 |
| `05_front_persp.png` | 前方透視 |
| `06_bottom_detail_R.png`／`07_bottom_detail_L.png` | 兩側下端近照（鉚釘＋水平凹槽＋肩部接頭）|

**構圖**：四張正交圖使用**同一 ortho_scale = 5.40**，900px；皆完整包含葉尖（z=+2.718）、雙手（x=±1.26）、腳底（z=−2.360），物件邊界未觸圖邊（PIL 實測）。

---

## 3. 專案狀態：已完成外觀驗收

| 類別 | 內容 | 驗收版本 |
|---|---|---|
| **主要結構** | 水滴主殼、五官（眼框／鏡片／四平面菱形鼻）、莖葉、底部連接件、雙腿腳掌、**雙手臂＋紅色兩指夾爪**、**背後雙圓筒裝置**（紅筒＋銀端蓋＋黑彎管＋支架） | v1–v17 |
| **材質／燈光** | 深紅金屬烤漆（`RedPaint` rough 0.375）／銀／淡青鏡片／橡膠黑／葉綠；大柔主光＋補光＋輪廓光；Khronos PBR Neutral | v18–v20 |
| **外殼細節** | 左右兩側縱向板縫（止於主殼水平凹槽，T 字交會）＋ 每側 4 顆銀色鉚釘 | v29 |
| 其他已驗收 | 主殼頂部（去頸／肩凸／凹折＋頂緣倒圓）、鼻子（直邊菱形＋四平面＋淺凸） | v21／v24 |

---

## 4. 與原圖仍有的差異（保留為後續選修，本次不處理）

1. **整體比例**：主殼 W/H=0.852（原圖約 0.90）；眼距 48%W（原圖 53%W）；鼻子比原圖大 35%。此三項為使用者**刻意指定偏離原圖量測值**。
2. **夾爪造型**：目前為兩指分節機械夾爪（直邊齒狀），與原圖的夾爪細節仍有差距。
3. **葉片姿態**：葉片由中央葉脈結構生成，與原圖的葉形／傾角仍有差異。
4. **背筒標誌**：原圖背筒上的標誌／圖案**尚未製作**（本次刻意不加標記）。

---

## 5. 備註

- **BASELINE 與所有歷史版本（v1–v29）皆保留未覆寫**，可隨時回溯比對。
- 本檔內的具體數值（板縫寬 0.012、楔形高 0.0018、凹槽 z=−0.729、材質 rough 0.375…）都是**本專案的實測值，不是通用標準**；可重用的是**方法**（見 Skill `blender-automation`），不是這些數字。
