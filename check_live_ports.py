import time
import csv
from datetime import datetime
import serial.tools.list_ports
from pymodbus.client import ModbusSerialClient
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk

# ────── COM 埠選擇 ──────
def select_com_port():
    ports = serial.tools.list_ports.comports()
    available = [port.device for port in ports]
    if not available:
        print("❌ 沒有可用的 COM 埠，請確認設備已插入")
        exit()

    def on_select():
        selected_port.set(combo.get())
        window.destroy()

    window = tk.Tk()
    window.title("選擇 COM 埠")
    tk.Label(window, text="請選擇 COM 埠：").pack(padx=10, pady=10)
    combo = ttk.Combobox(window, values=available, state="readonly")
    combo.current(0)
    combo.pack(padx=10, pady=5)
    tk.Button(window, text="開始", command=on_select).pack(padx=10, pady=10)
    selected_port = tk.StringVar()
    window.mainloop()
    return selected_port.get()

# ────── 警告值輸入 ──────
def get_warning_thresholds():
    def on_submit():
        try:
            thresholds['rpm'] = float(entry_rpm.get())
            thresholds['voltage'] = float(entry_v.get())
            thresholds['current'] = float(entry_a.get())
            input_window.destroy()
        except ValueError:
            tk.Label(input_window, text="⚠️ 請輸入數值").pack()

    thresholds = {}
    input_window = tk.Tk()
    input_window.geometry("250x300")
    input_window.title("輸入警告值")

    tk.Label(input_window, text="轉速警告值 (RPM)").pack()
    entry_rpm = tk.Entry(input_window)
    entry_rpm.pack()

    tk.Label(input_window, text="電壓警告值 (V)").pack()
    entry_v = tk.Entry(input_window)
    entry_v.pack()

    tk.Label(input_window, text="電流警告值 (A)").pack()
    entry_a = tk.Entry(input_window)
    entry_a.pack()

    tk.Button(input_window, text="確認", command=on_submit).pack(pady=10)
    input_window.mainloop()
    return thresholds

# 執行設定
com_port = select_com_port()
thresholds = get_warning_thresholds()

# ────── 初始化 Modbus RTU ──────
client = ModbusSerialClient(
    port=com_port,
    baudrate=19200,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1
)

# ────── 資料初始化 ──────
times, rpm_51, rpm_53, rpm_55 = [], [], [], []
v_52, v_54, v_56 = [], [], []
a_52, a_54, a_56 = [], [], []

# ────── 繪圖設定 ──────
plt.style.use('ggplot')
fig, (ax_rpm, ax_v, ax_a) = plt.subplots(3, 1, figsize=(12, 9), sharex=True)

# 折線資料物件
line_rpm_51, = ax_rpm.plot([], [], label='RPM_51', color='tab:blue')
line_rpm_53, = ax_rpm.plot([], [], label='RPM_53', color='tab:orange')
line_rpm_55, = ax_rpm.plot([], [], label='RPM_55', color='tab:green')
line_v_52, = ax_v.plot([], [], label='V_52', color='tab:blue')
line_v_54, = ax_v.plot([], [], label='V_54', color='tab:orange')
line_v_56, = ax_v.plot([], [], label='V_56', color='tab:green')
line_a_52, = ax_a.plot([], [], label='A_52', color='tab:blue')
line_a_54, = ax_a.plot([], [], label='A_54', color='tab:orange')
line_a_56, = ax_a.plot([], [], label='A_56', color='tab:green')

# 警告虛線標示
ax_rpm.axhline(
    y=thresholds['rpm'], color='red', linestyle='--',
    label=f'RPM Warning ({thresholds["rpm"]})'
)
ax_v.axhline(
    y=thresholds['voltage'], color='red', linestyle='--',
    label=f'Voltage Warning ({thresholds["voltage"]})'
)
ax_a.axhline(
    y=thresholds['current'], color='red', linestyle='--',
    label=f'Current Warning ({thresholds["current"]})'
)

# 標籤設定
ax_rpm.set_ylabel('RPM')
ax_rpm.set_title('Real-time RPM')
ax_rpm.legend()

ax_v.set_ylabel('Voltage (V)')
ax_v.set_title('Real-time Voltage')
ax_v.legend()

ax_a.set_xlabel('Time')
ax_a.set_ylabel('Current (A)')
ax_a.set_title('Real-time Current')
ax_a.legend()

# ────── CSV 建立 ──────
csvfile = open('rs232_monitor_all.csv', mode='w', newline='')
csvwriter = csv.writer(csvfile)
csvwriter.writerow(['Timestamp', 'RPM_51', 'V_52', 'A_52',
                    'RPM_53', 'V_54', 'A_54',
                    'RPM_55', 'V_56', 'A_56','set-rpm', 'set-voltage','set-current'])

# ────── 資料讀取 ──────
def read_rpm(slave_id):
    disp = client.read_holding_registers(address=0x0040, count=2, slave=slave_id)
    scale = client.read_holding_registers(address=0x002C, count=2, slave=slave_id)
    if disp.isError() or scale.isError():
        return None
    raw_disp = (disp.registers[0] << 16) + disp.registers[1]
    raw_scale = (scale.registers[0] << 16) + scale.registers[1]
    if raw_disp & 0x80000000:
        raw_disp -= 0x100000000
    if raw_scale & 0x80000000:
        raw_scale -= 0x100000000
    return raw_disp * (raw_scale / 10000)

def read_signed_16(slave, address):
    res = client.read_holding_registers(address=address, count=1, slave=slave)
    if res.isError():
        return None
    val = res.registers[0]
    return val - 0x10000 if val & 0x8000 else val

# ────── 更新圖表 ──────
def update(frame):
    now = datetime.now().strftime("%H:%M:%S")
    times.append(now)

    r51 = read_rpm(51)
    r53 = read_rpm(53)
    r55 = read_rpm(55)
    v52 = read_signed_16(52, 0x0046)
    a52 = read_signed_16(52, 0x0048)
    v54 = read_signed_16(54, 0x0046)
    a54 = read_signed_16(54, 0x0048)
    v56 = read_signed_16(56, 0x0046)
    a56 = read_signed_16(56, 0x0048)

    if None in [r51, r53, r55, v52, a52, v54, a54, v56, a56]:
        print("❌ 通訊錯誤")
        return

    v52, v54, v56 = v52 / 100, v54 / 100, v56 / 100
    a52, a54, a56 = a52 / 1000, a54 / 1000, a56 / 1000

    rpm_51.append(r51)
    rpm_53.append(r53)
    rpm_55.append(r55)
    v_52.append(v52)
    v_54.append(v54)
    v_56.append(v56)
    a_52.append(a52)
    a_54.append(a54)
    a_56.append(a56)

    for lst in [times, rpm_51, rpm_53, rpm_55, v_52, v_54, v_56, a_52, a_54, a_56]:
        lst[:] = lst[-60:]

    line_rpm_51.set_data(times, rpm_51)
    line_rpm_53.set_data(times, rpm_53)
    line_rpm_55.set_data(times, rpm_55)
    ax_rpm.set_xlim(times[0], times[-1])
    ax_rpm.set_ylim(
        min(rpm_51 + rpm_53 + rpm_55 + [thresholds['rpm']]) * 0.9,
        max(rpm_51 + rpm_53 + rpm_55 + [thresholds['rpm']]) * 1.1
    )

    line_v_52.set_data(times, v_52)
    line_v_54.set_data(times, v_54)
    line_v_56.set_data(times, v_56)
    ax_v.set_xlim(times[0], times[-1])
    ax_v.set_ylim(
        min(v_52 + v_54 + v_56 + [thresholds['voltage']]) * 0.9,
        max(v_52 + v_54 + v_56 + [thresholds['voltage']]) * 1.1
    )

    line_a_52.set_data(times, a_52)
    line_a_54.set_data(times, a_54)
    line_a_56.set_data(times, a_56)
    ax_a.set_xlim(times[0], times[-1])
    ax_a.set_ylim(
        min(a_52 + a_54 + a_56 + [thresholds['current']]) * 0.9,
        max(a_52 + a_54 + a_56 + [thresholds['current']]) * 1.1
    )

    csvwriter.writerow([now, r51, v52, a52, r53, v54, a54, r55, v56, a56,thresholds["rpm"],thresholds["voltage"],thresholds["current"]])
    print(f"{now} ➤ RPM: {r51:.1f}, {r53:.1f}, {r55:.1f} | V: {v52:.2f}, {v54:.2f}, {v56:.2f} | A: {a52:.3f}, {a54:.3f}, {a56:.3f}")

# ────── 主流程執行 ──────
try:
    if not client.connect():
        print(f"❌ 無法連接 {com_port}")
    else:
        print(f"✅ 成功連線 {com_port}，開始資料更新...")
        ani = FuncAnimation(fig, update, interval=1000)
        plt.tight_layout()
        plt.show()
except KeyboardInterrupt:
    print("🛑 手動中止")
finally:
    client.close()
    csvfile.close()
