# ESP8266/ESP32 MicroPython 韌體燒錄工具

本工具是旗標科技大量燒錄韌體時所採用的工具, 它會依據以下流程進行：

1. 若有找到 ESP8266 或是 ESP32 開頭的 .bin 檔案, 就會當成要燒錄的 MicroPython 韌體。
2. 若有要燒錄的韌體, 就先清除控制板上的 flash。
3. 依據檔名開頭選用不同的指令燒錄 ESP8266 或是 ESP32 的 MicroPython 韌體。
4. 如果有找到以 test 開頭的 .py 檔, 就會以 ampy 在控制板上執行該檔案, 並依據該程式執行結果是否有任何一行文字為 "hello" 來判斷韌體是否可正確執行 .py 檔案。
5. 如果有找到以 wifi 開頭的 .py 檔, 就會以 ampy 在控制板上執行該檔案, 並依據該程式執行結果是否有任何一行文字為 "**success**" 來判斷該程式測試控制板的網路功能是否成功？wifi 測試程式必須自行負責測試內容, 並在成功時送出一行 "**success**"。在 test_scripts 資料夾下的 test.py 會透過無線網路連線取得 https://flagtech.github.io/flag.txt 內容作為測試。
6. 如果有 upload 資料夾, 就會透過 ampy 工具將 upload 資料夾內的所有檔案一一上傳到控制板上。

以上各項除前 3 項以外戶不依賴, 也就是可以不燒錄韌體只單純測試韌體是否可運作？或是指單純測試控制板無線網路功能。只要再最上層資料夾準備好韌體檔、測試用的 py 檔、以及 upload 資料夾, 執行 run.bat 批次檔即可。

實際應用時, 請複製此倉庫, 建立個別產品的資料夾, 在該資料夾中儲存所要燒錄的韌體與上傳檔案, 或是特殊的測試檔, 在依據要燒錄哪一個產品的控制板來決定複製哪些資料到最上層使用。各產品資料夾建立後請將內容推回到此倉庫中, 讓此倉庫保持最新、最完整的韌體以及上傳檔案。
