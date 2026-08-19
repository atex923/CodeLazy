@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo 找不到 Python Launcher，請先安裝 Python 3.13。
    pause
    exit /b 1
)

py -3.13 -c "import PySide6" >nul 2>nul
if errorlevel 1 (
    echo 正在安裝 PySide6...
    py -3.13 -m pip install -r requirements.txt
    if errorlevel 1 (
        echo PySide6 安裝失敗。
        pause
        exit /b 1
    )
)

start "" pyw -3.13 "CodeLazy_V0.1.13.pyw"
endlocal
