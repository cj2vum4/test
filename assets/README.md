# assets

主頁 `index.html` 引用的本地資源。

## hero-poster.jpg

Hero 區塊右下角「TODAY'S FAVORITE」卡片內的海報縮圖（`index.html` 中
`alt="鍋貼品牌社群行銷菜單海報"` 的 `<img>`）。

- **檔名必須是 `hero-poster.jpg`**，放在 `assets/` 底下。若改用 `.png` / `.webp`，記得同步修改 `index.html` 的 `src`。
- 顯示區塊為 70 × 92 px（直式），套用 `object-cover`，建議來源圖比例接近 **3:4 直式**，過寬或過扁會被裁切。
- 建議寬度 800–1200 px，兼顧清晰度與載入速度。
