# BIM／IFC 延伸驗證：DURAVIT 衛浴產品物件

日期：2026-11-06。

## 驗證目的

這次實驗不是再建立一個角色模型，而是檢查既有的「輸入檢查 → 幾何處理 → 數值驗證 → 格式交付」技能流，能否延伸到市售 BIM 產品物件。

測試對象為 BIMobject 上的 [DURAVIT White Tulip 落地式馬桶 200109](https://www.bimobject.com/zh/duravit/product/white-tulip-floor-mounted-toilet-200109) 產品下載包。官方產品照只用於目視比對，第三方圖片、原始 IFC 與其他產品檔案未納入本儲存庫。

### 素材來源與授權界線

產品頁將素材標示為可免費下載，但「免費下載」不等同採用開源授權。BIMobject 現行使用條款將 BIM 物件、CAD／3D 檔、產品資訊及圖片納入 `Content`，允許個人使用、建築專業專案使用及純教育／研究等指定用途；條款同時說明權利仍由 BIMobject 與其授權人／製造商保留，沒有因下載而移轉所有權，並限制向第三方散布或提供存取。

因此本儲存庫只公開自行撰寫的測試方法、量測結果與分析，不重新散布原始產品包或官方照片。若產品頁另行提供明確的開源或再散布授權，才應依該授權文字與標示方式處理。

參考：[BIMobject User Terms of Service（2025-06-24 生效）](https://business.bimobject.com/terms-of-service-eula/)

## 下載包中的容器

| 檔案 | 大小 | 本次觀察 |
|---|---:|---|
| `.ifc` | 1.07 MB | 交換格式，包含幾何、屬性與分類資訊 |
| `.rfa` | 1.28 MB | Revit 原生族群 |
| `.gsm` | 1.55 MB | Archicad 原生物件 |
| `.dwg` × 2 | 1.78 MB + 40 KB | 3D 模型與 2D 圖塊 |
| `.skp`／`.fbx`／`.3ds`／`.stl` | 917／190／142／311 KB | 不同軟體與用途的幾何容器 |
| `.txt` | 1.7 KB | UTF-16 產品變體表，包含 `00 White Alpin`、`20 HygieneGlaze` |

同一項產品以多種容器交付，但檔案副檔名不同不代表內容、語意或可編輯程度相同。本次深入檢查以 IFC 為主，未逐一驗證其他原生格式。

## IFC 解析結果

| 項目 | 實測內容 |
|---|---|
| 規格 | IFC2X3、CoordinationView，檔案記錄日期為 2021-04-26 |
| 產生器 | `IFC Engine DLL 2017-09-06`；供應來源標示 BIMobject |
| 空間樹 | Project「BIMobject Library」→ Site → Building → Storey → 元件；中間三層 `Name=None` |
| 元件語意 | occurrence 為 `IfcFlowTerminal`，type 為 `IfcSanitaryTerminalType` |
| 幾何 | 單一 faceted Brep，3,108 頂點、6,212 三角面；不是參數化實體 |
| 屬性 | 60 個欄位，其中 13 個空白，47 個有值 |
| 分類 | 觀察到 10 套分類／代碼表示 |
| 外觀 | 1 個純白材質，顏色 `(1, 1, 1)`，透射 0 |
| 實體分布 | face、polyloop、point 等幾何相關實體約占總實體數 95% |

### IFC2X3 型別關係的技術修正

`IfcFlowTerminal` 並不代表這次匯出必然遺失「衛生設備」語意。IFC2X3 的設計可以由 occurrence `IfcFlowTerminal` 經 `IfcRelDefinesByType` 連到 `IfcSanitaryTerminalType`；IFC4 才加入更精確的 occurrence 類別 `IfcSanitaryTerminal`。

因此真正的自動分類風險是：**程式若只讀 occurrence 的實體類別，沒有繼續解析型別關係，就會把馬桶、洗手台等產品停留在同一個上層類別。**

參考：

- [buildingSMART IFC2X3：IfcSanitaryTerminalType](https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ifcplumbingfireprotectiondomain/lexical/ifcsanitaryterminaltype.htm)
- [buildingSMART IFC2X3：IfcFlowTerminal](https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ifcsharedbldgserviceelements/lexical/ifcflowterminal.htm)
- [buildingSMART IFC4：IfcSanitaryTerminal](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD1/HTML/schema/ifcplumbingfireprotectiondomain/lexical/ifcsanitaryterminal.htm)

## 實戰驗證結果

### 1. 單位與尺寸可以交叉驗收

IFC 專案宣告單位為 `METRE`，幾何尺寸也以公尺表示，例如寬度約 `0.3685`。產品屬性則記錄 `Width 370`、`Depth 580`、`Height 420`，其數值尺度對應毫米。

| 比對項目 | 幾何 bbox | 產品屬性 | 差異 |
|---|---:|---:|---:|
| 寬 | 約 368 mm | 370 mm | 約 2 mm |
| 深 | 約 580 mm | 580 mm | 約 0 mm |
| 高 | 約 421 mm | 420 mm | 約 1 mm |

這證明幾何與產品資料可以互相驗收，也證明自動化管線不能把所有數值直接套用同一尺度。正式規則仍應檢查專案單位、屬性單位與供應商欄位定義，不能只靠數值大小猜測。

### 2. 欄位填寫率不等於整體 BIM 品質

60 個屬性中有 47 個有值、13 個空白，欄位填寫率約為 **78.3%**。空白項目包括製造國、設計國、發佈日、安裝說明、產品認證、技術文件、影片、次要材料與 COBie 類別等。

這個比例可作為資料完整度的第一層指標，但尚不能直接稱為整體 BIM 品質分數。後續規則需要把欄位分成必填、建議與選填，依交付目的給予不同權重。

### 3. 多套分類碼需要正規化對照

同一物件同時出現 UNSPSC `301815`、Uniclass 1.4 `L7216`、Uniclass 2.0 `SS-35-65-90`、Uniclass 2015 `Pr_40_20_93`、NBS `35-65-90`、OmniClass `23-31 19 00`、MasterFormat `01 52 19`、Uniformat II `D2030`、BIMobject `sanitary-toilets` 與 IFC `Sanitary Terminal`。

自動化時不能只保存「分類碼」一個欄位，至少要同時保存分類系統、版本、代碼與名稱，才能建立內部標準與外部分類之間的 mapping。

### 4. 尺寸正確不代表產品組成完整

從 IFC 取出的陶瓷本體輪廓，與官方產品照的上寬下收、圓弧前緣和平直背板相符；但模型缺少座圈與上蓋。

因此模型完整性不能只看 bounding box 或輪廓誤差，還要建立「預期部件清單」並檢查組成。幾何尺寸通過，不代表產品模型已完整交付。

## 與綿羊案例的對照

| | 綿羊：技能流產出 | 馬桶：市售 BIM 物件 |
|---|---:|---:|
| 幾何 | 16,615 頂點、78 個命名物件 | 3,108 頂點、1 個 Brep |
| 材質 | 5 個實測色材質 | 1 個純白材質 |
| 語意 | 尚未加入產業分類 | 1 個 occurrence 上層類別與 1 個產品型別 |
| 屬性 | 尚未加入產品屬性 | 60 個欄位 |
| 分類碼 | 無 | 10 套分類／代碼表示 |

這個比較顯示：對製造商產品物件而言，BIM 的交付價值不只在幾何面數，而在幾何、型別關係、產品屬性與分類能否被可靠解析、交換及驗證。

## 工具鏈驗證

本次使用 `ifcopenshell 0.9.0.post1` 的 pip wheel，直接完成 IFC 開啟、幾何擷取、OBJ 匯出、bounding box 計算與視覺化，不需要 Blender BIM 外掛。這表示既有技能流可以加入獨立的 IFC 解析與驗收階段，而不必把所有工作綁在 Blender 介面內。

參考：[IfcOpenShell 幾何處理文件](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html)

## 對技能流的意義

安裝 Blender 或 IfcOpenShell 只提供工具，不能自動形成可交付產品。這次驗證補上了 BIM 領域需要的執行規則：

1. 辨識輸入格式與語意層級。
2. 正規化專案單位與屬性單位。
3. 追蹤 occurrence、type 與分類關係。
4. 以幾何 bbox 對照標稱尺寸。
5. 檢查欄位填寫率與必填規則。
6. 檢查預期部件與模型組成。
7. 將結果輸出為可追蹤的驗收報告。

因此，原本的角色建模技能流已證明可以延伸為「3D 幾何生成、格式解析與自動品質驗證」流程。不同領域仍需要各自的資料規則、分類規則和驗收標準，而不是只替換模型檔案。

## 驗證界線

- 本次只有一個品牌、一個產品樣本，不能代表所有 BIMobject 或 IFC 檔案。
- 尚未驗證 RFA、GSM、DWG、SKP、FBX、3DS 與 STL 之間的幾何一致性。
- 尚未驗證 IFC 在不同 BIM 軟體中重新匯入、修改與匯出的結果。
- 欄位填寫率只描述非空比例，沒有判定每個欄位是否正確或符合特定業主 EIR。
- 幾何是 faceted Brep，不代表已具備可製造的 CAD 實體、公差或 GD&T。
- 座圈與上蓋缺失是相對官方產品照的目視結果；尚未取得供應商對該下載變體交付範圍的說明。
