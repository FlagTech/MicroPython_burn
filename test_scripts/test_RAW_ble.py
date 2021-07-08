# Implements a BLE HID Consumer Controll

from micropython import const
import struct
import bluetooth

conph = False

def ble_irq(event, data):
    global conn_handle,conph
    if event == 1:
        print("已連線！")
        print("請將磁鐵靠近 ESP32 銀色鐵殼中央區域")
        conn_handle = data[0]
        conph = True
    if event == 2:
        print("已斷線！")
        conph = False
    else:
        pass
        #print("event:", event, data)


ble = bluetooth.BLE()
ble.active(1)
ble.irq(ble_irq)

UUID = bluetooth.UUID

F_READ = bluetooth.FLAG_READ
F_WRITE = bluetooth.FLAG_WRITE
F_READ_WRITE = bluetooth.FLAG_READ | bluetooth.FLAG_WRITE
F_READ_NOTIFY = bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY

ATT_F_READ = 0x01
ATT_F_WRITE = 0x02

# 建立伺服器
hid_service = (
    UUID(0x1812),  # Human Interface Device            人機介面設備
    (
        (UUID(0x2A4A), F_READ),  # HID information     HID信息
        (UUID(0x2A4B), F_READ),  # HID report map      HID報告圖
        (UUID(0x2A4C), F_WRITE),  # HID control point  HID控制點
        (UUID(0x2A4D), F_READ_NOTIFY, ((UUID(0x2908), ATT_F_READ),)),  # HID report / reference
        #(UUID(0x2A4D), F_READ_WRITE, ((UUID(0x2908), ATT_F_READ),)),  # HID report / reference
        (UUID(0x2A4E), F_READ_WRITE),  # HID protocol mode
    ),
)

# fmt: off
HID_REPORT_MAP = bytes([
    0x05, 0x01,     # Usage Page (Generic Desktop) 通用桌面控制類型
    0x09, 0x06,     # Usage (Keyboard)             鍵盤
    0xA1, 0x01,     # Collection (Application)     集合(應用)
    0x85, 0x01,     #     Report ID (1)            報告編號 (1)
    0x75, 0x01,     #     Report Size (1)          單位數據大小 (1)
    0x95, 0x08,     #     Report Count (8)         數據量:8
    0x05, 0x07,     #     Usage Page (Key Codes)   用途類型:鍵盤 (修飾鍵)
    0x19, 0xE0,     #     Usage Minimum (224)      內容最小值:0xE0
    0x29, 0xE7,     #     Usage Maximum (231)      內容最小值:0xE7
    0x15, 0x00,     #     Logical Minimum (0)      狀態最小值:0 (放開)
    0x25, 0x01,     #     Logical Maximum (1)      狀態最大值:1 (按下)
    0x81, 0x02,     #     Input (Data, Variable, Absolute); Modifier byte
    0x95, 0x01,     #     Report Count (1)         數據量:1
    0x75, 0x08,     #     Report Size (8)          單位數據大小 (8)
    0x81, 0x01,     #     Input (Constant); Reserved byte
    0x95, 0x05,     #     Report Count (5)         數據量:5
    0x75, 0x01,     #     Report Size (1)          單位數據大小 (1)
    0x05, 0x08,     #     Usage Page (LEDs)        用途類型:LED指示燈
    0x19, 0x01,     #     Usage Minimum (1)        內容最小值:0x01,代表數字鎖定
    0x29, 0x05,     #     Usage Maximum (5)        內容最大值:0x05,代表日文假名切換
    0x91, 0x02,     #     Output (Data, Variable, Absolute); LED report  輸出，絕對值
    0x95, 0x01,     #     Report Count (1)         數據量:1
    0x75, 0x03,     #     Report Size (3)          單位數據大小 (3)
    0x91, 0x01,     #     Output (Constant); LED report padding
    0x95, 0x06,     #     Report Count (6)
    0x75, 0x08,     #     Report Size (8)
    0x15, 0x00,     #     Logical Minimum (0)
    0x25, 0x65,     #     Logical Maximum (101)
    0x05, 0x07,     #     Usage Page (Key Codes)   用途類型:鍵盤
    0x19, 0x00,     #     Usage Minimum (0)
    0x29, 0x65,     #     Usage Maximum (101)
    0x81, 0x00,     #     Input (Data, Array); Key array (6 bytes)
    0xC0,           # End Collection
])
# fmt: on

# register services  註冊服務
name = "Akeyboard"
ble.config(gap_name=name)
handles = ble.gatts_register_services((hid_service,))
#print(handles)
h_info, h_hid, _, h_rep, h_d1, h_proto = handles[0]

# set initial data
ble.gatts_write(h_info, b"\x01\x01\x00\x02")  # HID info: ver=1.1, country=0, flags=normal
ble.gatts_write(h_hid, HID_REPORT_MAP)  # HID report map
ble.gatts_write(h_d1, struct.pack("<BB", 1, 1))  # report: id=1, type=input
# ble.gatts_write(h_d2, struct.pack("<BB", 1, 2))  # report: id=1, type=output
ble.gatts_write(h_proto, b"\x01")  # protocol mode: report

# advertise 廣告
adv = (
    b"\x02\x01\x06"
    b"\x03\x03\x12\x18"  # complete list of 16-bit service UUIDs: 0x1812
    b"\x03\x19\xc1\x03"  # appearance: keyboard
    +bytes((len(name)+1,9,))+ str.encode(name)
)
conn_handle = None
ble.gap_advertise(100_000, adv)
print("請用手機藍牙連線 " + name)
# once connected use the following to send reports

def send_char(char):
    if char == " ":
        mod = 0
        code = 0x2C
    elif ord("a") <= ord(char) <= ord("z"):
        mod = 0
        code = 0x04 + ord(char) - ord("a")
    elif ord("A") <= ord(char) <= ord("Z"):
        mod = 2
        code = 0x04 + ord(char) - ord("A")
    else:
        assert 0

    ble.gatts_notify(conn_handle, h_rep, struct.pack("8B", mod, 0, code, 0, 0, 0, 0, 0))
    ble.gatts_notify(conn_handle, h_rep, b"\x00\x00\x00\x00\x00\x00\x00\x00")


def send_str(st):
    for c in st:
        send_char(c)

# 可以查看以下對照表
# https://circuitpython.readthedocs.io/projects/hid/en/latest/_modules/adafruit_hid/keycode.html
# https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf
def screen_shot():   # 0x28:ENTER    0x46:Print Scrn
    global conph
    if(conph == True):
        mod = 0
        code = 0x46
        ble.gatts_notify(conn_handle, h_rep, struct.pack("8B", mod, 0, code, 0, 0, 0, 0, 0))
        ble.gatts_notify(conn_handle, h_rep, b"\x00\x00\x00\x00\x00\x00\x00\x00")
        return True
    else:
        print("尚未連線！")
        return False
    
from machine import Pin
import time
#from ble_hid import BLE_HID
import esp32

led = Pin(5,Pin.OUT)
last_staUp = 1     # 是否按下按鈕

# 上面按鈕
button_up=Pin(13,Pin.IN,Pin.PULL_UP)   

while True:
    hall = esp32.hall_sensor()
    print("\r{:5d}".format(hall), end="")
    if(hall<150 and hall>-150):
        staUp = 1
        led.value(1)
    else:
        staUp = 0
        led.value(0)

    # 前一次沒按 且 這次有按
    if(last_staUp == 1 and staUp == 0):
        blst = screen_shot()
        print("已截圖")
        if(blst == True):
            break
    # 紀錄前一次狀態
    last_staUp = staUp
    time.sleep(0.05)
