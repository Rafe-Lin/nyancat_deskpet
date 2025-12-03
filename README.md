# Nyan Cat Desktop Pet

A cute Nyan Cat desktop pet that flies around your screen with a rainbow trail!

## Features
- **Flying Nyan Cat**: Animated sprite flying across the screen.
- **Rainbow Trail**: A colorful, transparent, waving trail follows the cat.
- **Interactive**:
    - **Drag**: Click and drag the cat to move it.
    - **3D Particles**: Click the cat to see a burst of 3D particles!
    - **Auto-fly**: The cat flies automatically in a sine wave pattern when released.
    - **Quit**: Right-click to access the context menu and quit.

## Quick Start (Single Command)

You can run the application with a single command. This script will automatically create the virtual environment, install dependencies, and start the pet.

### Windows
Double-click `run.bat` or run it in the terminal:
```powershell
.\run.bat
```

### MacOS / Linux
Run the shell script:
```bash
sh run.sh
```

## Manual Installation

If you prefer to set it up manually:

1. **Create a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   # MacOS/Linux
   python3 -m venv venv
   ```

2. **Activate the environment**:
   ```bash
   # Windows
   .\venv\Scripts\activate
   # MacOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Troubleshooting
- **Cat shows as a checkerboard/box**: This means the transparency isn't working or the image is missing.
- **Permission on MacOS**: If the cat doesn't move or respond, check System Preferences > Security & Privacy > Accessibility and allow your terminal app.
