from machine import Pin, I2S
import gc
import time
spk_sample_rate = 20000
record_switch = Pin(5, Pin.IN, Pin.PULL_UP)
# Vin:3V GND:GND SD:不接 GAIN:不接 DIN:13 BCLK:12 LRC:14
audio_out = I2S(1, sck=Pin(12), ws=Pin(14),
                sd=Pin(13),
                mode=I2S.TX,
                bits=16,
                format=I2S.MONO,
                rate=spk_sample_rate,
                ibuf=8000)
gc.collect()
while True:
    if record_switch.value() == 0:
        with open("temp.wav", "rb") as f:
            print('\n---播放---')
            while True:
                data = f.read(1024)  # 每次读取1024字节数据
                if not data:
                    data = None
                    break
                audio_out.write(data)  # 将数据写入I2S输出
        gc.collect()
    time.sleep(0.1)
