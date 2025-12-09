@echo off
setlocal
echo Setting up Nyan Cat Pet...

:: 檢查 venv 是否存在，如果不存在或損壞則重新建立
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please check if Python is installed and added to PATH.
        pause
        exit /b 1
    )
)

echo Installing dependencies...
:: 直接使用 venv 中的 pip，避免路徑問題
"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo Starting Nyan Cat...
:: 直接使用 venv 中的 python 執行
"venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo Nyan Cat application exited with an error.
)

echo.
echo Application closed.
pause
