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
