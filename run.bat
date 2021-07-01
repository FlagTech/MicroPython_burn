@echo off
setlocal EnableDelayedExpansion
set fname=
set dummy=
set test_script=
set wifi_script=
set /a total = 0

REM 看有沒有以 test 開頭燒錄後測試用的 py 檔
for %%f in (test*.py) do (
    set test_script=%%f
)

REM 看有沒有以 wifi 開頭燒錄後測試用的 py 檔
for %%f in (wifi*.py) do (
    set wifi_script=%%f
)

REM 先看有沒有 esp8266 開頭檔名的韌體檔
for %%f in (esp8266*.bin) do (
    set fname=%%f
    goto start
)
REM 再看有沒有 esp32 開頭檔名的韌體檔
for %%f in (esp32*.bin) do (
    set fname=%%f
    goto start
)

:start
echo -------------------------------------------------
echo 韌體檔  ：%fname%
echo 測試檔  ：%test_script%
echo Wi-Fi 檔：%wifi_script%
set /p port="輸入連接埠 (輸入 q 離開)："
if "%port%"=="q" goto end

:next

REM 清除 errorlevel
(call )
set error="NO"

if not "%fname%"=="" (
    echo -------------------------------------------------
    echo 清除 flash
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py -p %port% erase_flash
    if errorlevel 1 (
        echo !! 清除 flash 時發生錯誤
        set error="YES"
        goto error_check
    )
    echo OK
)
if /I "%fname:~0,7%"=="ESP8266" (
    echo -------------------------------------------------
    echo 燒錄韌體
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py -p %port% --baud 460800 write_flash --flash_size=detect -fm dio 0 %fname%

    if errorlevel 1 (
        echo !! 燒錄韌體時發生錯誤
        set error="YES"
        goto error_check
    )
    echo OK
)
if /I "%fname:~0,5%"=="ESP32" (
    echo -------------------------------------------------
    echo 燒錄韌體
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py --chip esp32 --port %port% write_flash -z 0x1000 %fname%

    if errorlevel 1 (
        echo !! 燒錄韌體時發生錯誤
        set error="YES"
        goto error_check
    )
    echo OK
)

if not "%test_script%"=="" (
    echo -------------------------------------------------
    echo 測試韌體
    echo -------------------------------------------------
    set error="YES"
    for /f "tokens=*" %%r in ('.\python\python.exe .\python\scripts\ampy.exe -p %port% run %test_script%') do (
        echo 測試程式執行結果：%%r
        if "%%r"=="hello" (
            set error="NO"
        )
    )
    if errorlevel 1 set error="YES"
    if "%error%"=="YES" goto error_check
    echo OK
)

if not "%wifi_script%"=="" (
    echo -------------------------------------------------
    echo 測試 Wi-Fi
    echo -------------------------------------------------
    set error="YES"
    for /f "tokens=*" %%r in ('.\python\python.exe .\python\scripts\ampy.exe -p %port% run %wifi_script%') do (
        if not "%%r"=="" echo %%r
        if "%%r"=="**success**" (
            set error="NO"
        )
    )
    if errorlevel 1 set error="YES"
    if "%error%"=="YES" goto error_check
    echo OK
)

if exist .\upload (
    echo -------------------------------------------------
    echo 上傳檔案
    echo -------------------------------------------------
    for /R .\upload %%f in (*) do (
        echo 上傳 %%f 檔案
        .\python\python.exe .\python\scripts\ampy.exe -p %port% put %%f
        if errorlevel 1 (
            echo !! 上傳 %%f 檔案時發生錯誤
            set error="YES"
            goto error_check
        )
    )
    echo OK
)

echo -------------------------------------------------

:error_check
if %error%=="YES" (
    set /p dummy="！！！燒錄失敗, 要再試一次請直接按 Enter... (輸入 q 離開)"
) else (
    set /a total=total+1
    set /p dummy="第 !total! 片燒錄完成, 請換下一片後按 Enter 繼續... (輸入 q 離開)"
)

if "%dummy%"=="q" (
    goto end
) else (
    goto next
)

:end
REM exit batch file
exit /b 0