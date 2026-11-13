螺絲 CAD 生成器（測試版 v3）- Windows

1. 本資料夾 ScrewGen 內的 ScrewGen.exe 與 _internal 資料夾必須放在一起。
   請勿把 ScrewGen.exe 單獨移出來；要放桌面請用「右鍵 > 傳送到 > 桌面(建立捷徑)」。
2. 雙擊 ScrewGen.exe 開啟。第一次開啟需載入 CAD 核心，畫面會顯示秒數，請耐心等候。
3. 免安裝：不寫入系統。不需要時直接刪除整個 ScrewGen 資料夾即可。
4. 記錄檔：screwgen.log（與 exe 同資料夾），回報問題時請一併提供。

自我測試（不開視窗）：
  在本資料夾網址列輸入 cmd 按 Enter，然後執行
    start /wait ScrewGen.exe --selftest
    type selftest.log
