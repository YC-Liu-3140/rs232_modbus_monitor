# RS232 + Modbus RTU 多設備監控系統
# RS232 + Modbus RTU Multi-device Monitoring System

Python 實作的 RS232/Modbus RTU 多裝置監控圖表範例  
A Python project for real-time multi-device monitoring via RS232/Modbus RTU, with graphical visualization and CSV logging.

Python 實作的 RS232/Modbus RTU 多裝置監控圖表範例，支援：
- COM 埠自動偵測與選擇
- 警告值輸入（轉速/電壓/電流）
- Modbus RTU 連線（多設備監控）
- Matplotlib 即時圖表監控
- 數據同步儲存至 CSV

---

### 1. 安裝必要套件

```bash
pip install pyserial pymodbus matplotlib

---
操作流程 | How to Use
啟動程式，會跳出 COM 埠選擇視窗。

輸入監控的警告值（轉速、電壓、電流）。

自動連接 Modbus RTU 並開始讀取數據。

畫面顯示即時三欄曲線圖（含警告紅線）。

所有數據同步儲存到 rs232_monitor_all.csv，方便後續分析。

🛠️ 功能特色 | Features
支援多 COM 埠、多 Slave ID

可自訂警告值，即時紅線顯示

Matplotlib 實時圖形化、數據記錄

程式架構簡單易懂，便於擴充與教學

💡 延伸應用 | Further Applications
可結合 TCP/IP、Web 視覺化、雲端資料同步等進階功能

支援自訂前端（Tkinter、PyQt、Web）或自動化批次監控

🏷️ 授權 License
MIT License

🤝 貢獻 & 聯絡 | Contribution & Contact
歡迎 fork、pull request、或提出 issue 討論改進！
PRs, issues, and suggestions are welcome!

作者 / Author: YC-Liu-3140
GitHub: https://github.com/YC-Liu-3140/rs232_modbus_monitor
