@echo off
REM ��� UTF8 �s�X
REM chcp 65001 > nul
setlocal EnableDelayedExpansion
set fname=
set dummy=
set /a total = 0

REM �]�w�����ɮת����|
set firmware_path=%1
if "%1"=="" (
  set irmware_path=.
)

set chip=
REM ���ݦ��S�� esp8266 �}�Y�ɦW��������
for %%f in (%firmware_path%\esp8266*.bin) do (
    set fname=%%f
    set chip=ESP8266
    goto start
)
REM �A�ݦ��S�� esp32 �}�Y�ɦW��������
for %%f in (%firmware_path%\esp32*.bin) do (
    set fname=%%f
    set chip=ESP32
    goto start
)

if "%fname%"=="" (
  echo �䤣�춴���ɡI
  echo �Ϊk�G
  echo    run �����ɪ����| ^(�S���w�w�]���ثe�ؿ�^)
  set /p key="�Ы� Enter �����C"
  goto end
)

:start
echo -------------------------------------------------
echo ������  �G!fname!
set /p port="��J�s���� (��J q ���})�G"
if "!port!"=="q" goto end

:next

REM �M�� errorlevel
(call )
set error="NO"

if not "!fname!"=="" (
    echo -------------------------------------------------
    echo �M�� flash
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py -p !port! erase_flash
    if errorlevel 1 (
        echo !! �M�� flash �ɵo�Ϳ��~
        set error="YES"
        goto error_check
    )
    echo OK
)
if "%chip%"=="ESP8266" (
    echo -------------------------------------------------
    echo �N�� ESP8266 ����
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py -p !port! --baud 460800 write_flash --flash_size=detect -fm dio 0 !fname!

    if errorlevel 1 (
        echo !! �N������ɵo�Ϳ��~
        set error="YES"
        goto error_check
    )
    echo OK
)
if /I "!chip!"=="ESP32" (
    echo -------------------------------------------------
    echo �N�� ESP32 ����
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py --chip esp32 --port !port! write_flash -z 0x1000 !fname!

    if errorlevel 1 (
        echo !! �N������ɵo�Ϳ��~
        set error="YES"
        goto error_check
    )
    echo OK
)

if exist %firmware_path%\upload (
    echo -------------------------------------------------
    echo �W���ɮ�
    echo -------------------------------------------------
    for /R %firmware_path%\upload %%f in (*) do (
        echo �W�� %%f �ɮ�
        .\python\python.exe .\python\scripts\ampy.exe -p !port! put %%f
        if errorlevel 1 (
            echo !! �W�� %%f �ɮ׮ɵo�Ϳ��~
            set error="YES"
            goto error_check
        )
    )
    echo OK
)

REM �A�ݦ��S�� test �}�Y�� .py ������
for %%f in (%firmware_path%\test_OK*.py) do (
    echo -------------------------------------------------
    echo ���տ�X���G�� **OK** ���{���G%%f
    echo -------------------------------------------------
    set error="Yes"
    for /f "tokens=*" %%r in ('.\python\python.exe .\python\Lib\site-packages\ampy\cli.py -p !port! run %%f') do (
        echo ^> %%r
        if "%%r"=="**OK**" (
            set error="NO"
        ) 
    )    
    if errorlevel 1 set error="YES"
    if "!error!"=="YES" goto error_check
    echo OK.
)

REM �A�ݦ��S�� test_raw �}�Y�� .py ������
for %%f in (%firmware_path%\test_raw*.py) do (
    echo -------------------------------------------------
    echo ���ժ�����X���{���G%%f
    echo -------------------------------------------------
    set error="No"
    .\python\python.exe .\python\Lib\site-packages\ampy\cli.py -p !port! run %%f
    if errorlevel 1 set error="YES"
    if "!error!"=="YES" goto error_check
)

echo -------------------------------------------------

:error_check
if !error!=="YES" (
    set /p dummy="�I�I�I�N������, �n�A�դ@���Ъ����� Enter... (��J q ���}"
) else (
    set /a total=total+1
    set /p dummy="�� !total! ���N������, �д��U�@����� Enter �~��... (��J q ���})"
)

if "!dummy!"=="q" (
    goto end
) else (
    goto next
)

:end
echo �`�@ !total! ���N������.
REM �_�즨 big5 �s�X
REM chcp 950 > nul
REM exit batch file
exit /b 0
