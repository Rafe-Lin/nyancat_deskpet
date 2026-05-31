@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PYTHON_VERSION=3.12.10"
set "PYTHON_TARGET=%LOCALAPPDATA%\Programs\Python\Python312"
set "PYTHON_INSTALLER=%TEMP%\nyancat-python-%PYTHON_VERSION%-amd64.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"

echo Setting up Nyan Cat Pet...

if not exist "main.py" (
    echo.
    echo main.py was not found next to run.bat.
    echo If you opened this from inside a zip file, extract the whole zip first,
    echo then double-click run.bat from the extracted folder.
    pause
    exit /b 1
)

if not exist "assets\nyan_cat.png" (
    echo.
    echo assets\nyan_cat.png was not found.
    echo Extract the whole zip before running run.bat.
    pause
    exit /b 1
)

if exist "venv\Scripts\python.exe" goto venv_ready

call :find_python
if not defined PY_EXE (
    call :install_python_windows
    call :find_python
)

if not defined PY_EXE (
    echo.
    echo Python was not found and automatic installation was not available.
    echo Install Python 3.10 or newer from https://www.python.org/downloads/
    echo Then run this file again.
    pause
    exit /b 1
)

echo Creating virtual environment...
"%PY_EXE%" %PY_ARGS% -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

:venv_ready
set "VENV_PY=venv\Scripts\python.exe"

echo Checking dependencies...
"%VENV_PY%" -c "import PyQt6, PIL" >nul 2>nul
if errorlevel 1 (
    echo Installing missing dependencies...
    "%VENV_PY%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed.
)

echo Starting Nyan Cat...
"%VENV_PY%" main.py

if errorlevel 1 (
    echo Nyan Cat application exited with an error.
)

echo.
echo Application closed.
pause
exit /b 0

:find_python
set "PY_EXE="
set "PY_ARGS="
if exist "%PYTHON_TARGET%\python.exe" (
    set "PY_EXE=%PYTHON_TARGET%\python.exe"
    exit /b 0
)

py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if not errorlevel 1 (
    set "PY_EXE=py"
    set "PY_ARGS=-3"
    exit /b 0
)

python -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if not errorlevel 1 (
    set "PY_EXE=python"
    exit /b 0
)

python3 -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if not errorlevel 1 (
    set "PY_EXE=python3"
    exit /b 0
)
exit /b 0

:install_python_windows
echo Python was not found. Trying automatic user-level install...

where winget >nul 2>nul
if not errorlevel 1 (
    echo Trying winget first...
    winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    call :find_python
    if defined PY_EXE exit /b 0
)

echo Trying direct download from python.org...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
if errorlevel 1 (
    echo Failed to download Python installer.
    exit /b 0
)

echo Installing Python %PYTHON_VERSION% for the current user...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=0 Include_launcher=1 Include_pip=1 Include_tcltk=1 Include_test=0 TargetDir="%PYTHON_TARGET%"
if errorlevel 1 (
    echo Python installer failed.
    exit /b 0
)

if exist "%PYTHON_TARGET%\python.exe" (
    echo Python installed at "%PYTHON_TARGET%".
)
exit /b 0
