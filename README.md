# 螺絲 CAD 生成器 — 系統可行性測試 v2

目的：確認打包後能在 Windows（公司電腦）與 macOS（Apple 晶片）上 **免安裝、離線** 執行。

## 打包（手動）
GitHub → Actions → **Build ScrewGen (manual)** → **Run workflow** → 選 `windows` 或 `mac` → Run。
完成後在該次執行頁面最下方 **Artifacts** 下載。

## 測試回報
- [ ] 能否開啟（是否被安全機制攔截）
- [ ] 「載入 CAD 幾何核心」花幾秒
- [ ] 產生模型後畫面顯示的：建模 / 網格 / 傳輸 / 總計 秒數
- [ ] 3D 預覽可旋轉
- [ ] STEP 能否用 CAD 開啟為實體
- [ ] 有問題時附上 screwgen.log（位置見各平台使用說明）
