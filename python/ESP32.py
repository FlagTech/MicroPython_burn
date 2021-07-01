import serial
import os
import sys
import time
import subprocess
import pyboard

bin_dir = os.path.join(os.pardir, "bin")
upload_dir = os.path.join(os.pardir, "upload")
print(bin_dir)
print(upload_dir)
ser = serial.Serial()
ser.baudrate = 115200

try:

    # -------- 尋找 .bin 檔以及需要上傳的檔案 ---------
    bin_files = []
    bin_file_names = []
    with os.scandir(bin_dir) as my_dir:
        for entry in my_dir:
            if entry.name.endswith('.bin') and entry.is_file():
                bin_files.append(os.path.join(bin_dir, entry.name))
                bin_file_names.append(entry.name)

    upload_files = []
    upload_files_name = []
    with os.scandir(upload_dir) as my_dir:
        for entry in my_dir:
            if entry.is_file():
                upload_files.append(os.path.join(upload_dir, entry.name))
                upload_files_name.append(entry.name)

    if len(bin_files) == 0:
        raise FileNotFoundError("找不到可燒錄的 .bin 檔")
    elif len(bin_files) > 1:
        raise ValueError(".bin 檔數量超過 1 個, 請刪除多餘 .bin 檔")

    print("準備使用 " + bin_file_names[0] + " 進行燒錄")

    if upload_files:
        print("燒錄後上傳檔案: " + str(upload_files_name))


    # -------- 開始燒錄與上傳檔案 ---------

    com_port = input("\n請輸入 ESP32/D1 mini 連接的序列埠: ")
    print("\n\n測試序列埠...\n")
    ser.port = com_port
    ser.open()
    ser.close()
    print("序列埠測試成功...")

    while True:
        try:
            print("\n\n==================== 燒錄韌體 ====================\n\n")
            os.system("python.exe Scripts\\esptool.py -p "+com_port+" erase_flash")
            if "esp8266" in bin_file_names[0]:
                print('\n選擇燒入esp8266韌體\n')
                os.system("python.exe Scripts\\esptool.py -p "+com_port+" --baud 460800 write_flash --flash_size=detect -fm dio 0 " + bin_files[0])
            elif "esp32" in bin_file_names[0]:
                print('\n選擇燒入esp32韌體\n')
                os.system("python.exe Scripts\esptool.py --chip esp32 --port "+com_port+" write_flash -z 0x1000 "+ bin_files[0])  
            print("\n\n==================== 測試韌體 ====================\n\n")
            for n in range(3):
                print(n, end='...', flush=True)
                pyb = pyboard.Pyboard(com_port)
                time.sleep(2)
                pyb.enter_raw_repl()
                ret=str(pyb.exec('help()'), 'utf-8')
                pyb.exit_raw_repl()
                pyb.close()

                if not "Welcome to MicroPython" in ret:
                    raise IOError("韌體測試失敗")
            print('Ok')

            print("已經燒錄 " + bin_file_names[0])

            if upload_files:
                print("\n\n==================== 上傳檔案 ====================\n\n")

                for i, f in enumerate(upload_files):
                    print(upload_files_name[i])
                    os.system("python.exe Scripts\\ampy.exe --port "+com_port+" put " + f)

                # 檢查檔案是否成功上傳
                ret = subprocess.check_output("python.exe Scripts\\ampy.exe --port "+com_port+" ls", shell=True)
                ret = str(ret, 'utf-8')
                
                for f in upload_files_name:
                    if not "/"+f+"\r\n" in ret:
                        msg = f + " 檔沒有成功上傳"
                        print(msg)
                        raise FileNotFoundError(msg)

            print("\n\n-------------------- 韌體燒錄成功！ --------------------\n\n")
            print("\n\n==================== 測試網路 ====================\n\n")
            os.system("python.exe Scripts\\ampy.exe --port "+com_port+" run D1mini-testscript.py") 

        except Exception as e:
            print("\n\n--- 韌體燒錄失敗！ 請試試看重燒一次, 若重燒仍然失敗的話請列入不良品 ---\n\n")

        finally:
            text = input("請換下一片 ESP32/D1 mini 控制板, 然後按 Enter 鍵燒錄")

except Exception as e:
    print("發生錯誤, 錯誤訊息如下:\n\n" + str(e) + "\n")
    text = input("請按 Enter 鍵關閉視窗")

finally:
    ser.close()


