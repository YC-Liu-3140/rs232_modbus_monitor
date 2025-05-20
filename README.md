# rs232_modbus_monitor
Python RS232/Modbus RTU 即時監控與圖表範例

# RS232 + Modbus RTU 監控系統

本專案是用 Python 實作的 RS232/Modbus RTU 多裝置監控與圖表化程式，支援：
- COM 埠自動偵測與選擇
- 警告值輸入（轉速/電壓/電流）
- Modbus RTU 連線與多裝置讀取
- Matplotlib 即時圖表監控
- 資料同步記錄至 CSV

## 依賴套件

```bash
pip install pyserial pymodbus matplotlib
