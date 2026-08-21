# assets

主頁 `index.html` 引用的本地資源。

## hero-poster.jpg

Hero 區塊右下角「TODAY'S FAVORITE」卡片內的海報縮圖（`index.html` 中
`alt="鍋貼品牌社群行銷菜單海報"` 的 `<img>`）。

- **檔名必須是 `hero-poster.jpg`**，放在 `assets/` 底下。若改用 `.png` / `.webp`，記得同步修改 `index.html` 的 `src`。
- 顯示區塊為 70 × 92 px（直式），套用 `object-cover`，建議來源圖比例接近 **3:4 直式**，過寬或過扁會被裁切。
- 建議寬度 800–1200 px，兼顧清晰度與載入速度。

## hero-gyoza.glb

Hero 3D 場景的預設模型（鍋貼本體 + 冰花脆邊），由 `index.html` 內
`CONFIG.modelUrl` 指定。

- 約 210 KB，8,372 個三角形，使用 vertex color + `KHR_materials_clearcoat`，
  不含貼圖，因此不需要額外的 texture 請求。
- 這顆模型是把 `index.html` 裡的 `buildProceduralSubject()`（程序化幾何）
  匯出成 GLB 的結果。兩者外觀一致：**GLB 載入失敗時（例如以 `file://`
  直接開啟造成 CORS 失敗），程式會自動改用同一份程序化幾何**，畫面不會壞掉。
- 想換成自己的模型：只要改 `CONFIG.modelUrl`（相對路徑或完整 URL 皆可，
  支援 `.glb` / `.gltf`）。載入後會自動置中、依 `CONFIG.model.targetSize`
  正規化尺寸，並重新計算相機距離，不需要事先調整模型的 scale 或 origin。
- 若模型含有 animation clips，會自動以 `THREE.AnimationMixer` 播放；
  可用 `CONFIG.model.clip` 指定 `'auto'` / `'all'` / clip 名稱 / index / `null`。
