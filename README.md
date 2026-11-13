# 螺絲 CAD 生成器 — Windows 系統可行性測試

目的：確認打包成 exe 後，能在公司電腦上 **免安裝、離線** 執行。

## 取得 exe
GitHub → Actions → 最新一次 "Build Windows exe" → Artifacts → 下載 `ScrewGenTest-windows`（zip）。

## 在公司電腦上測試
1. 解壓縮到任意資料夾（例如桌面）。
2. 雙擊 `ScrewGenTest.exe`。
3. 按「1. 產生模型 + 3D 預覽」→ 應出現 M3x10 盤頭十字螺絲，可用滑鼠旋轉。
4. 按「2. 另存 STEP」→ 存檔後用公司 CAD 開啟確認。

## 回報以下結果
- [ ] exe 能否開啟（SmartScreen / 防毒是否攔截？攔截訊息截圖）
- [ ] 視窗與 3D 預覽是否正常顯示
- [ ] STEP 能否存檔、CAD 能否開啟為實體
- [ ] 產生模型耗時幾秒
