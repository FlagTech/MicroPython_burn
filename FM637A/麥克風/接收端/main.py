import machine

from machine import I2S, Pin
import os
import time

record_switch = Pin(5, Pin.IN, Pin.PULL_UP)
mic_sample_rate = 8000
chunk_size = mic_sample_rate * 2
def delete_files(file_name):
    if file_name in uos.listdir("/"):
        try:
            uos.remove(f"/{file_name}")
        except Exception as e:
            print(f"刪除失敗: {e}")
    else:
        pass
# SD:26 VDD:3V GND:GND WS:27 SCK:25 L/R:GND
audio_in = I2S(0,sck=Pin(25),ws=Pin(27),sd=Pin(26),mode=I2S.RX,bits=16,format=I2S.MONO,rate=mic_sample_rate,ibuf=chunk_size)
#delete_files('input.pcm')
pcm = open('/input.pcm', 'wb')



# 配置音频输出到 MAX98357
spk_sample_rate = 8000  # 采样率
audio_out = I2S(1, sck=Pin(12), ws=Pin(14), sd=Pin(13), mode=I2S.TX, bits=16, format=I2S.MONO, rate=spk_sample_rate, ibuf=8000)

    
while True:
    if record_switch.value() == 0:
        delete_files('input.pcm')
        pcm = open('/input.pcm', 'wb')
        recording_time = 1
        print('---請說話---')
        while recording_time < 2:
            print('\r🎤:', recording_time, 's', end='')
            ibuf = bytearray(chunk_size)
            audio_in.readinto(ibuf, chunk_size)
            pcm.write(ibuf)
            ibuf = None 
            gc.collect()
            recording_time += 1 
        print('\n---說完了---')
        pcm.close()
        gc.collect()
        
        # 打开PCM音频文件

        with open("input.pcm", "rb") as f:
            print('\n---播放---')
            while True:
                data = f.read(1024)  # 每次读取1024字节数据
                if not data:
                    data = None
                    break
                audio_out.write(data)  # 将数据写入I2S输出
        gc.collect()
        
    time.sleep(0.1)

