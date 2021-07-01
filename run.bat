@echo off
setlocal EnableDelayedExpansion
set fname=
set dummy=
set test_script=
set wifi_script=
set /a total = 0

REM �ݦ��S���H test �}�Y�N������եΪ� py ��
for %%f in (test*.py) do (
    set test_script=%%f
)

REM �ݦ��S���H wifi �}�Y�N������եΪ� py ��
for %%f in (wifi*.py) do (
    set wifi_script=%%f
)

REM ���ݦ��S�� esp8266 �}�Y�ɦW��������
for %%f in (esp8266*.bin) do (
    set fname=%%f
    goto start
)
REM �A�ݦ��S�� esp32 �}�Y�ɦW��������
for %%f in (esp32*.bin) do (
    set fname=%%f
    goto start
)

:start
echo -------------------------------------------------
echo ������  �G%fname%
echo ������  �G%test_script%
echo Wi-Fi �ɡG%wifi_script%
set /p port="��J�s���� (��J q ���})�G"
if "%port%"=="q" goto end

:next

REM �M�� errorlevel
(call )
set error="NO"

if not "%fname%"=="" (
    echo -------------------------------------------------
    echo �M�� flash
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py -p %port% erase_flash
    if errorlevel 1 (
        echo !! �M�� flash �ɵo�Ϳ��~
        set error="YES"
        goto error_check
    )
    echo OK
)
if /I "%fname:~0,7%"=="ESP8266" (
    echo -------------------------------------------------
    echo �N������
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py -p %port% --baud 460800 write_flash --flash_size=detect -fm dio 0 %fname%

    if errorlevel 1 (
        echo !! �N������ɵo�Ϳ��~
        set error="YES"
        goto error_check
    )
    echo OK
)
if /I "%fname:~0,5%"=="ESP32" (
    echo -------------------------------------------------
    echo �N������
    echo -------------------------------------------------
    .\python\python.exe .\python\Scripts\esptool.py --chip esp32 --port %port% write_flash -z 0x1000 %fname%

    if errorlevel 1 (
        echo !! �N������ɵo�Ϳ��~
        set error="YES"
        goto error_check
    )
    echo OK
)

if not "%test_script%"=="" (
    echo -------------------------------------------------
    echo ���ն���
    echo -------------------------------------------------
    set error="NO"
    for /f "tokens=*" %%r in ('.\python\scripts\ampy.exe -p %port% run %test_script%') do (
        echo ���յ{�����浲�G�G%%r
        if not "%%r"=="hello" (
            echo !! ���ն���ɵo�Ϳ��~
            set error="YES"
            goto error_check
        )
    )
    if errorlevel 1 (
        set error="YES"
        goto error_check
    )
    echo OK
)

if not "%wifi_script%"=="" (
    echo -------------------------------------------------
    echo ���� Wi-Fi
    echo -------------------------------------------------
    set error="YES"
    for /f "tokens=*" %%r in ('.\python\scripts\ampy.exe -p %port% run %wifi_script%') do (
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
    echo �W���ɮ�
    echo -------------------------------------------------
    for /R .\upload %%f in (*) do (
        echo �W�� %%f �ɮ�
        .\python\scripts\ampy.exe -p %port% put %%f
        if errorlevel 1 (
            echo !! �W�� %%f �ɮ׮ɵo�Ϳ��~
            set error="YES"
            goto error_check
        )
    )
    echo OK
)

echo -------------------------------------------------

:error_check
if %error%=="YES" (
    set /p dummy="�I�I�I�N������, �n�A�դ@���Ъ����� Enter... (��J q ���})"
) else (
    set /a total=total+1
    set /p dummy="�� !total! ���N������, �д��U�@����� Enter �~��... (��J q ���})"
)

if "%dummy%"=="q" (
    goto end
) else (
    goto next
)

:end
REM exit batch file
exit /b 0