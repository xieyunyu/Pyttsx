@echo off
echo 正在嘗試解決 Python 程式的問題...
echo.

REM 設定 Python 程式所在的資料夾
set PYTHON_DIR="C:\Users\690\Dev\02_TEST"
cd /d %PYTHON_DIR%

REM 啟動虛擬環境 (如果使用)
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM 檢查 Python 版本
echo 檢查 Python 版本...
python --version
python3 --version
echo.

REM 更新 pip
echo 更新 pip...
python -m pip install --upgrade pip
echo.

REM 重新安裝 pydub
echo 重新安裝 pydub...
pip uninstall -y pydub
pip install pydub
echo.

REM **移除或註釋掉安裝 pyaudio的部分**
echo 嘗試安裝 pyaudio...
python -m pip install pyaudio
echo.

REM 嘗試安裝 pyaudioop (如果需要，但先檢查程式碼是否需要)
REM echo 嘗試安裝 pyaudioop...
REM pip install pyaudioop
REM echo.

REM 執行 Python 程式 (請將您的 Python 腳本名稱更新到下方)

REM echo 執行 Python 程式...

REM python "Test_pyttsx3_v07.py"

pause
echo 程式執行完畢。