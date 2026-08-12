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

py -3.13 -m pip install -U nuitka ordered-set zstandard -r requirements.txt
if errorlevel 1 (
    echo 打包套件安裝失敗。
    pause
    exit /b 1
)

py -3.13 -m nuitka ^
  --mode=onefile ^
  --windows-console-mode=disable ^
  --enable-plugin=pyside6 ^
  --assume-yes-for-downloads ^
  --output-dir=Nuitka_Output ^
  --output-filename=CodeLazy_V0.1.6.exe ^
  --product-name="程式創作室" ^
  --file-description="程式開發管理工具" ^
  --file-version=0.1.6.0 ^
  --product-version=0.1.6.0 ^
  "CodeLazy_V0.1.6.pyw"

if errorlevel 1 (
    echo.
    echo Nuitka 打包失敗，請保留畫面訊息供後續檢查。
    pause
    exit /b 1
)

echo.
echo 打包完成：Nuitka_Output\CodeLazy_V0.1.6.exe
pause
endlocal
