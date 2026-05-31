# Nyan Cat Desktop Pet

A cute Nyan Cat desktop pet that flies around your screen with a rainbow trail!

## Features
- **Flying Nyan Cat**: Animated sprite flying across the screen.
- **Rainbow Trail**: A colorful, transparent, waving trail follows the cat.
- **Pixel Settings UI**: Right-click the cat and open Settings to tune break interval, size, speed, particles, rainbow trail, and custom character art.
- **Interactive**:
    - **Drag**: Click and drag the cat to move it.
    - **3D Particles**: Click the cat to see a burst of 3D particles!
    - **Auto-fly**: The cat flies automatically in a sine wave pattern when released.
    - **Quit**: Right-click to access the context menu and quit.

## Quick Start (Single Command)

You can run the application with a single command. The script will find `py`, `python`, or `python3`, create the virtual environment, install missing dependencies only when needed, and start the pet. On a fresh Windows machine it will try `winget` first, then fall back to downloading the official Python installer from python.org and installing it for the current user.

### Windows
Extract the zip first, then double-click `run.bat` from the extracted folder. You can also run it in the terminal:
```powershell
.\run.bat
```

### MacOS / Linux
Run the shell script:
```bash
sh run.sh
```

## Custom Character

Right-click the pet, open **Settings**, then use **Upload 4-frame sheet**. The image should be one horizontal PNG with four equal-width frames. Transparent background works best; a flat `#00ff00` green background is also supported and will be removed automatically.

Use **Copy GPT prompt** in Settings, or paste this prompt into GPT with one character image attached:

```text
Use the attached character image as the exact main character reference.
Create a 4-frame horizontal running animation sprite sheet.

Requirements:
- Keep the character's identity, colors, costume, face, and silhouette recognizable.
- Four equal-width frames in one row: frame 1, frame 2, frame 3, frame 4.
- Side view, character facing right.
- Same baseline, same character scale, same bounding box, centered in each frame.
- Smooth run cycle with visibly different leg/arm or body poses.
- Transparent background preferred. If transparency is not available, use a perfectly flat solid #00ff00 chroma-key background.
- No shadows, no floor, no extra objects, no text, no watermark.
- Leave generous padding around each frame so it can be cropped cleanly.
- Output as a single PNG sprite sheet.
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
