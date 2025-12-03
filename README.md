# Nyan Cat Desktop Pet

A cute Nyan Cat desktop pet that flies around your screen with a rainbow trail!

## Features
- **Flying Nyan Cat**: Animated sprite.
- **Rainbow Trail**: Colorful trail effect.
- **Interactive**: Drag to move, right-click to quit.
- **Cross-Platform**: Runs on Windows and MacOS.

## Installation

1. **Clone the repository** (or download the files).
2. **Set up a virtual environment**:

   **Windows**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **MacOS/Linux**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

**Windows**:
```powershell
python main.py
```

**MacOS**:
```bash
python main.py
```

## Troubleshooting
- If the cat doesn't appear transparent, ensure your window manager supports transparency.
- On MacOS, you might need to grant the terminal accessibility permissions if interaction is wonky.
