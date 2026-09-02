# assets

主頁 `index.html` 引用的本地資源。

## icons/

PWA 圖示集，主體是一張「發光鍋貼」真實照片 — 取材自 `hero-poster.jpg`
裡手持鍋貼、爆汁冒煙的特寫鏡頭（真實拍攝，非插畫/AI 生圖），裁切成圓形
徽章、做了亮部 bloom 與暖色調校，襯在琥珀色放射光暈背景上，呼應品牌的
wood / ember 配色。所有 PNG 皆由 `generate-icon.py`（Pillow 程式合成）
產生，並由 `export-sizes.py` 依 `manifest.json` 所需尺寸輸出：

| 檔案 | 尺寸 | 用途 |
| --- | --- | --- |
| `icon-16.png` / `icon-32.png` | 16×16 / 32×32 | favicon（另有根目錄 `favicon.ico` 多尺寸版本） |
| `icon-180.png` | 180×180 | `apple-touch-icon` |
| `icon-192.png` / `icon-512.png` | 192×192 / 512×512 | manifest 一般圖示（`purpose: any`） |
| `icon-maskable-192.png` / `icon-maskable-512.png` | 192×192 / 512×512 | manifest 可遮罩圖示（`purpose: maskable`，內容縮至安全區內） |

依賴 `hero-poster.jpg`：`generate-icon.py` 用寫死的座標框
（`box = (566, 250, 976, 660)`）從該圖裁出鍋貼特寫。**若更換
`hero-poster.jpg`，這組座標很可能需要重新調整**，否則會裁到錯誤區域。

若要重新設計圖示：修改 `generate-icon.py` 內的裁切座標 / 合成邏輯 →
執行 `python3 generate-icon.py`（需要 `pip install Pillow`，會在本資料夾
產出 `icon-master.png`，此檔不進版控）→ 執行 `python3 export-sizes.py`
重新輸出上表所有尺寸與根目錄 `favicon.ico`。修改後請確認 `manifest.json`
與 `index.html` 的 `<link rel="icon"...>` / `apple-touch-icon` 路徑仍對應。

## hero-poster.jpg

Hero 區塊右下角「TODAY'S FAVORITE」卡片內的海報縮圖（`index.html` 中
`alt="鍋貼品牌社群行銷菜單海報"` 的 `<img>`）。

- **檔名必須是 `hero-poster.jpg`**，放在 `assets/` 底下。若改用 `.png` / `.webp`，記得同步修改 `index.html` 的 `src`。
- 顯示區塊為 70 × 92 px（直式），套用 `object-cover`，建議來源圖比例接近 **3:4 直式**，過寬或過扁會被裁切。
- 建議寬度 800–1200 px，兼顧清晰度與載入速度。
