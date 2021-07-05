import network, urequests, sys, time

ap_list = ["FLAG-SCHOOL"]

ap_data = {
    "FlagTest":    {"passwd": "0233110330",
                    "url": "https://flagtech.github.io/flag.txt",
                    "checkstr": "FLAG"},
    "FLAG":    {"passwd": "0233110330",
                    "url": "https://flagtech.github.io/flag.txt",
                    "checkstr": "FLAG"},
    "FlagTest2":    {"passwd": "0233110330",
                    "url": "https://flagtech.github.io/flag.txt",
                    "checkstr": "FLAG"},
    "FlagoWiFi":   {"passwd": "0233110330",
                    "url": "https://flagtech.github.io/flag.txt",
                    "checkstr": "FLAG" },
    "FLAG-SCHOOL": {"passwd": "12345678",
                    "url": "https://flagtech.github.io/flag.txt",
                    "checkstr": "FLAG" },
    "D1miniAP":    {"passwd": "12345678",
                    "url": "http://192.168.4.1",
                    "checkstr": "FLAG" },
    "D1miniAP-2":  {"passwd": "12345678",
                    "url": "http://192.168.4.1",
                    "checkstr": "FLAG" },
    "FLAG-WS7-253":  {"passwd": "",
                    "url": "https://flagtech.github.io/flag.txt",
                    "checkstr": "FLAG" },
    "TP-LINK_7BC2A0":  {"passwd": "48559898",
                    "url": "https://flagtech.github.io/flag.txt",
                    "checkstr": "FLAG" },
}

for ap in ap_list:
    ssid = ap
    passwd = ap_data[ap]["passwd"]
    url = ap_data[ap]["url"]
    checkstr = ap_data[ap]["checkstr"]
    
    print("正在連線 WiFi: " + ssid)
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(ssid, passwd)

    maxtry = 30
    n = 1
    while not sta_if.isconnected():
        time.sleep(1)
        print(n, end="..")
        if n > maxtry:
            print("發生錯誤！！！無法連線 WiFi 網路！！！")
            sys.exit(0)
            break
        n = n + 1

    print('network config:', sta_if.ifconfig())

    try:
        print("\n正在連線 " + url)
        ret=urequests.get(url).text
        if checkstr in ret:
            print("**OK**\n" + ret)
        else:
            raise Exception("在網頁中找不到字串 " + checkstr)
        sta_if.disconnect()
    except Exception as e:
        print("**failed**\n發生錯誤！！！無法取得網路資料！！！ 錯誤：", str(e))
        sys.exit(0)

