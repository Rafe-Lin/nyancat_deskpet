#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
echo "Setting up Nyan Cat Pet..."

PY_CMD=""
VENV_PY="venv/bin/python"

if [ ! -x "$VENV_PY" ] && [ -x "venv/Scripts/python.exe" ]; then
    VENV_PY="venv/Scripts/python.exe"
fi

find_python() {
    if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
        PY_CMD="python3"
    elif command -v python >/dev/null 2>&1 && python -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
        PY_CMD="python"
    elif command -v py >/dev/null 2>&1 && py -3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' >/dev/null 2>&1; then
        PY_CMD="py -3"
    fi
}

install_python_if_possible() {
    if command -v winget.exe >/dev/null 2>&1; then
        echo "Python was not found. Trying to install Python 3.12 with winget..."
        winget.exe install -e --id Python.Python.3.12 || true
    elif command -v brew >/dev/null 2>&1; then
        echo "Python was not found. Trying to install Python with Homebrew..."
        brew install python || true
    elif command -v apt-get >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
        echo "Python was not found. Trying to install Python with apt..."
        sudo apt-get update || true
        sudo apt-get install -y python3 python3-venv python3-pip || true
    fi
}

if [ ! -x "$VENV_PY" ]; then
    find_python
    if [ -z "$PY_CMD" ]; then
        install_python_if_possible
        find_python
    fi

    if [ -z "$PY_CMD" ]; then
        echo ""
        echo "Python was not found and automatic installation was not available."
        echo "Install Python 3.10 or newer, then run this script again."
        exit 1
    fi

    echo "Creating virtual environment..."
    # shellcheck disable=SC2086
    $PY_CMD -m venv venv
fi

echo "Checking dependencies..."
if "$VENV_PY" -c 'import PyQt6, PIL' >/dev/null 2>&1; then
    echo "Dependencies already installed."
else
    echo "Installing missing dependencies..."
    "$VENV_PY" -m pip install -r requirements.txt
fi

echo "Starting Nyan Cat..."
"$VENV_PY" main.py
