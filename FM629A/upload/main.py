import machine,time,sys,select
from machine import ADC,Pin
p = select.poll()        # 建立一個偵測物件
p.register(sys.stdin)    # 偵測標準輸入, 也就是互動介面的輸入
#test!!
adcX = ADC(Pin(32))
adcY = ADC(Pin(33))
adcLight = ADC(Pin(34))
adcChange = ADC(Pin(35))
adcWeapon = ADC(Pin(39))

buttonRightUp = Pin(23,Pin.IN,Pin.PULL_UP)
buttonRightDown = Pin(22,Pin.IN,Pin.PULL_UP)
buttonLeftUp = Pin(21,Pin.IN,Pin.PULL_UP)
buttonLeftDown = Pin(19,Pin.IN,Pin.PULL_UP)
buttonMiddle = Pin(15,Pin.IN,Pin.PULL_UP)
shack = Pin(25,Pin.OUT)

adcX.atten(ADC.ATTN_11DB)        # x軸
adcY.atten(ADC.ATTN_11DB)        # y軸
adcLight.atten(ADC.ATTN_11DB)    # 光敏電阻
adcChange.atten(ADC.ATTN_11DB)   # 可變電阻
adcWeapon.atten(ADC.ATTN_11DB)   # 武器電阻

allData = ['','','','','','','','']

light_min = 0

# map(整數)
def convert(x, in_min, in_max, out_min, out_max):
    return ((x - in_min) * (out_max - out_min) //
           (in_max - in_min) + out_min)  # // 除完取商數

# 被射擊(震動馬達)
def Hit():
    shack.value(1)
    time.sleep(0.2)
    shack.value(0)
            
# 方向控制(五向搖桿)
def Move():
    move_h = 'n'            # 水平
    move_v = 'n'            # 垂直
    move_m = 'n'            # 中間
    
    if(adcX.read()<500):    # 右邊
        move_h = 'r'
    elif(adcX.read()>3500): # 左邊
        move_h = 'l'    
    if(adcY.read()<500):    # 後退
        move_v = 'b'
    elif(adcY.read()>3500): # 前進
        move_v = 'f'
        
    if(buttonMiddle.value() == 0):
        move_m = 'y'
    else:
        move_m = 'n'
        
    return(move_h,move_v,move_m)

# 手電筒(光敏電阻)
def Light():
    #light = 0
    global light_min
    light = convert(adcLight.read(),int(light_min),4095,0,25)
    if light<0:
        light=0
    return str(light)
    
# 換武器(各式電阻)
def Weapon():
    weapon = 'n'
    
    if(adcWeapon.read()>163 and adcWeapon.read()<1269):
        weapon = 'x'      
    elif(adcWeapon.read()>=1269 and adcWeapon.read()<3071):
        weapon = 'y'
    elif(adcWeapon.read()>=3071):
        weapon = 'z'
    elif(adcWeapon.read()<=163):     # 沒插電阻時
        weapon = 'n'
        
    return weapon

# 火焰大小(可變電阻)
def Change():
    change = convert(adcChange.read(),0,4095,55,0)

    return str(change)

sta = 0
shoot = 'g'

# 射擊
def Shoot():
    global sta
    global shoot

    if(buttonRightUp.value()==1 and sta==0):
        shoot = 's'
        sta = 1
    elif(buttonRightUp.value()==0 and sta==1):
        shoot = 'g'
        sta = 0
        
    if(buttonLeftUp.value()==1 and sta==0):
        shoot = 's'
        sta = 2
    elif(buttonLeftUp.value()==0 and sta==2):
        shoot = 'g'
        sta = 0
        
    return shoot

turn = 'm'

# 鏡頭更改
def Turn():
    global turn
    
    if(buttonLeftDown.value()==1 and buttonRightDown.value()==0):
        turn = 'h'
    elif(buttonRightDown.value()==1 and buttonLeftDown.value()==0):
        turn = 'p'
    elif(buttonLeftDown.value()==0 and buttonRightDown.value()==0):
        turn = 'i'
        
    return turn 

LED = Pin(2,Pin.OUT)
LED.value(1)
time.sleep_ms(300)
LED.value(0)
time.sleep_ms(300)
LED.value(1)
time.sleep_ms(300)
LED.value(0)
time.sleep_ms(300)
LED.value(1)
time.sleep_ms(300)
LED.value(0)

light_sum = 0

for i in range(20):
    light_sum = light_sum + adcLight.read()
    time.sleep(0.05)
    
light_min = light_sum/20
 
ac = ''

# 等待連接, 如果與 Unity 連接即可接收與傳送資料
while True:
    # 測試是否有資料待讀取參數 0 是等待 0 毫秒
    while p.poll(0):
        # 讀取資料 1 個字元        
        ac = sys.stdin.read(1)   
    # 如果接收到字元為 a, 則跳出 while True 迴圈
    if(ac == 'a'):
        break

for i in range(50):
    print("ESP32")
    time.sleep_ms(10)

LED.value(1)

while True:
    print(Move()[0]+','+Move()[1]+','+Move()[2]+','+Light()+','+
          Weapon()+','+Change()+','+Shoot()+','+Turn())
    
    # 測試是否有資料待讀取參數 0 是等待 0 毫秒
    while p.poll(0):
        # 讀取資料 1 個字元        
        ac = sys.stdin.read(1)   
    if(ac == 'q'):
        LED.value(0)
        machine.reset()
    elif(ac == 'a'):
        for i in range(50):
            print("ESP32")
            time.sleep_ms(20)
    elif(ac == 't'):
        Hit()
        
    ac = ''        
    time.sleep_ms(10)


