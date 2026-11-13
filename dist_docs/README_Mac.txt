螺絲 CAD 生成器（測試版 v3）- macOS（Apple 晶片 M1/M2/M3/M4）

1. 解壓縮 ScrewGen-mac-arm64.zip，得到 ScrewGen.app（可拖到「應用程式」資料夾）。
2. 第一次開啟前，打開「終端機」執行以下指令解除下載隔離（路徑依實際位置調整）：
     xattr -cr ~/Downloads/ScrewGen.app
3. 雙擊開啟。第一次開啟需載入 CAD 核心，畫面會顯示秒數，請耐心等候。
4. 記錄檔：~/Library/Logs/ScrewGen/screwgen.log

自我測試（不開視窗），在終端機執行：
  ~/Downloads/ScrewGen.app/Contents/MacOS/ScrewGen --selftest --out ~/Desktop/screwgen_test
  cat ~/Desktop/screwgen_test/selftest.log
