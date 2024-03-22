from machine import Pin, I2S
from chat_tools import *
import urequests
import time

record_switch = Pin(5, Pin.IN, Pin.PULL_UP)

wifi_connect("FLAG", "0233110330")
url = 'http://172.16.0.56:5000'

mic_sample_rate = 4000
chunk_size = mic_sample_rate * 2
config(url,mic_sample_rate)

# SD:26 VDD:3V GND:GND WS:27 SCK:25 L/R:GND
audio_in = I2S(0,sck=Pin(25),ws=Pin(27),sd=Pin(26),mode=I2S.RX,bits=16,format=I2S.MONO,rate=mic_sample_rate,ibuf=chunk_size)

while True:
    if record_switch.value() == 0:
        recording_time = 0
        ibuf = bytearray(chunk_size)
        delete_files('input.pcm')
        pcm = open('/input.pcm', 'wb')
        
        print('---請說話---')
        while record_switch.value() == 0 and recording_time <11:
            print('\r🎤:', recording_time, 's', end='')
            t_start = time.time()
            audio_in.readinto(ibuf, chunk_size)
            pcm.write(ibuf)
            t_close = time.time()
            recording_time += (t_close-t_start)
        print('\n---說完了---')
        pcm.close()
        server_reply = upload_pcm('input.pcm',url)
        print(f'語音辨識: {server_reply.text}')
    time.sleep(0.1)






