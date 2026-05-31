import sys
import random
import math
import shutil
from pathlib import Path
from PIL import Image
from PyQt6.QtWidgets import (
    QWidget, QMenu, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QCheckBox, QSpinBox, QGroupBox, QFileDialog, QMessageBox,
    QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QElapsedTimer
from PyQt6.QtGui import QPainter, QPixmap, QColor, QAction, QBrush, QPen, QConicalGradient, QFont


ASSET_DIR = Path("assets")
CUSTOM_FRAME_PREFIX = "custom_character"
GPT_SPRITE_PROMPT = """Use the attached character image as the exact main character reference.
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
- Output as a single PNG sprite sheet."""

class WorkStopperOverlay(QWidget):
    def __init__(self, parent_pet):
        super().__init__()
        self.parent_pet = parent_pet
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Cover the whole screen
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Animation timer for disco effects
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update)
        self.anim_timer.start(50)
        
        self.angle = 0
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 1. Dim background
        painter.fillRect(self.rect(), QColor(0, 0, 0, 200))
        
        # 2. Exaggerated Disco Lights (Conical Gradient)
        center = self.rect().center()
        gradient = QConicalGradient(QPointF(center), self.angle)
        gradient.setColorAt(0.0, QColor(255, 0, 0, 100))
        gradient.setColorAt(0.16, QColor(255, 255, 0, 100))
        gradient.setColorAt(0.33, QColor(0, 255, 0, 100))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 100))
        gradient.setColorAt(0.66, QColor(0, 0, 255, 100))
        gradient.setColorAt(0.83, QColor(255, 0, 255, 100))
        gradient.setColorAt(1.0, QColor(255, 0, 0, 100))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        
        # 3. Pulsing Text
        self.angle = (self.angle + 5) % 360
        scale = 1.0 + 0.1 * math.sin(self.angle * 0.1)
        
        font = QFont("Arial", 40, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        
        text = "STOP WORKING!\nPLAY WITH ME!"
        text_rect = painter.boundingRect(self.rect(), Qt.AlignmentFlag.AlignCenter, text)
        
        painter.translate(center)
        painter.scale(scale, scale)
        painter.translate(-center)
        
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)
        
    def mousePressEvent(self, event):
        # Dismiss overlay
        self.hide()
        self.parent_pet.show()
        self.parent_pet.activateWindow()


class PixelSettingsPanel(QWidget):
    def __init__(self, pet):
        super().__init__()
        self.pet = pet
        self.setWindowTitle("Nyan Settings")
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedWidth(280)
        self.setStyleSheet("""
            QWidget {
                background: #16161f;
                color: #f8f8ff;
                font-family: Consolas, "Courier New", monospace;
                font-size: 11px;
            }
            QGroupBox {
                border: 2px solid #45f0ff;
                margin-top: 8px;
                padding: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                color: #ffd447;
            }
            QPushButton {
                background: #2b2d42;
                border: 2px solid #f72585;
                padding: 6px;
            }
            QPushButton:hover { background: #3b3f66; }
            QSlider::groove:horizontal {
                height: 6px;
                background: #303045;
                border: 1px solid #777;
            }
            QSlider::handle:horizontal {
                width: 12px;
                margin: -5px 0;
                background: #45f0ff;
                border: 2px solid #ffffff;
            }
            QSpinBox {
                background: #222236;
                border: 2px solid #45f0ff;
                padding: 3px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #45f0ff;
                background: #222236;
            }
            QCheckBox::indicator:checked { background: #ffd447; }
        """)

        root = QVBoxLayout(self)
        root.setSpacing(8)

        timing_box = QGroupBox("REST")
        timing_layout = QVBoxLayout(timing_box)
        self.rest_spin = QSpinBox()
        self.rest_spin.setRange(1, 240)
        self.rest_spin.setSuffix(" min")
        self.rest_spin.setValue(self.pet.rest_interval_minutes)
        self.rest_spin.valueChanged.connect(self.pet.set_rest_interval)
        self.work_check = QCheckBox("Enable break reminder")
        self.work_check.setChecked(self.pet.work_mode_enabled)
        self.work_check.toggled.connect(self.pet.set_work_mode_enabled)
        timing_layout.addWidget(QLabel("Interval"))
        timing_layout.addWidget(self.rest_spin)
        timing_layout.addWidget(self.work_check)

        animation_box = QGroupBox("ANIMATION")
        animation_layout = QVBoxLayout(animation_box)
        self.size_slider = self._slider(60, 180, self.pet.cat_scale, self.pet.set_cat_scale)
        self.speed_slider = self._slider(0, 18, self.pet.move_speed, self.pet.set_move_speed)
        self.particle_slider = self._slider(0, 100, self.pet.particle_density, self.pet.set_particle_density)
        self.trail_slider = self._slider(3, 14, self.pet.trail_depth, self.pet.set_trail_depth)
        self.trail_check = QCheckBox("Rainbow trail")
        self.trail_check.setChecked(self.pet.trail_enabled)
        self.trail_check.toggled.connect(self.pet.set_trail_enabled)

        for label, slider in (
            ("Cat size", self.size_slider),
            ("Fly speed", self.speed_slider),
            ("3D particles", self.particle_slider),
            ("Trail depth", self.trail_slider),
        ):
            animation_layout.addWidget(QLabel(label))
            animation_layout.addWidget(slider)
        animation_layout.addWidget(self.trail_check)

        character_box = QGroupBox("CHARACTER")
        character_layout = QVBoxLayout(character_box)
        upload_button = QPushButton("Upload 4-frame sheet")
        upload_button.clicked.connect(self.pet.import_character_sheet_dialog)
        reset_button = QPushButton("Reset character")
        reset_button.clicked.connect(self.pet.reset_character)
        prompt_button = QPushButton("Copy GPT prompt")
        prompt_button.clicked.connect(self.copy_gpt_prompt)
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlainText(GPT_SPRITE_PROMPT)
        self.prompt_text.setReadOnly(True)
        self.prompt_text.setFixedHeight(92)
        character_layout.addWidget(upload_button)
        character_layout.addWidget(reset_button)
        character_layout.addWidget(prompt_button)
        character_layout.addWidget(self.prompt_text)

        button_row = QHBoxLayout()
        hide_button = QPushButton("Close UI")
        hide_button.clicked.connect(self.hide)
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(QApplication.instance().quit)
        button_row.addWidget(hide_button)
        button_row.addWidget(quit_button)

        root.addWidget(timing_box)
        root.addWidget(animation_box)
        root.addWidget(character_box)
        root.addLayout(button_row)

    def _slider(self, min_value, max_value, value, slot):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_value, max_value)
        slider.setValue(value)
        slider.valueChanged.connect(slot)
        return slider

    def copy_gpt_prompt(self):
        QApplication.clipboard().setText(GPT_SPRITE_PROMPT)
        QMessageBox.information(self, "Copied", "GPT sprite prompt copied.")


class NyanCatPet(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load assets
        self.frames = []
        self.current_frame_idx = 0
        self.load_assets()
        
        # Animation timer (Faster: 50ms)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_frame)
        self.anim_timer.start(50) 
        
        # Movement
        self.dragging = False
        self.drag_position = QPoint()
        self.press_timer = QElapsedTimer()
        
        # Auto movement
        self.auto_move_timer = QTimer(self)
        self.auto_move_timer.timeout.connect(self.auto_move)
        self.auto_move_timer.start(50)
        self.move_speed = 5
        self.speed_x = self.move_speed
        self.speed_y = 0
        self.time_step = 0

        # Effects
        self.particles = []
        self.click_particles = [] # 3D particles
        self.trail_particles = []
        self.cat_scale = 100
        self.particle_density = 55
        self.trail_depth = 11
        self.trail_enabled = True
        
        # Transparent Rainbow Colors
        alpha = 150
        self.rainbow_colors = [
            QColor(255, 0, 0, alpha),    # Red
            QColor(255, 165, 0, alpha),  # Orange
            QColor(255, 255, 0, alpha),  # Yellow
            QColor(50, 205, 50, alpha),  # Green
            QColor(0, 191, 255, alpha),  # Blue
            QColor(148, 0, 211, alpha)   # Purple
        ]
        self.wave_offset = 0
        
        # Resize window to accommodate trail
        self.update_window_size()
        
        # Initial position
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() // 2, screen.height() // 2)

        # Work Mode (Pomodoro)
        self.rest_interval_minutes = 25
        self.work_mode_enabled = True
        self.work_timer = QTimer(self)
        self.work_timer.setSingleShot(True)
        self.work_timer.timeout.connect(self.return_from_work)
        self.overlay = WorkStopperOverlay(self)
        self.settings_panel = PixelSettingsPanel(self)
        
        self.start_drag_pos = QPoint()
        self.is_drag_gesture = False

    def load_assets(self):
        try:
            custom_frames = self.load_frame_set(CUSTOM_FRAME_PREFIX)
            if custom_frames:
                self.frames = custom_frames
                return

            run_frames = self.load_frame_set("nyan_cat_run")
            if run_frames:
                self.frames = run_frames
                return

            fallback_pixmap = QPixmap(str(ASSET_DIR / "nyan_cat.png"))
            if fallback_pixmap.isNull():
                raise Exception("Failed to load nyan_cat.png")
            self.frames = [fallback_pixmap]
        except Exception as e:
            print(f"Error loading assets: {e}")
            pixmap = QPixmap(64, 40)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QBrush(Qt.GlobalColor.gray))
            painter.drawRect(0, 0, 64, 40)
            painter.end()
            self.frames = [pixmap]

    def load_frame_set(self, prefix):
        frames = []
        for idx in range(4):
            pixmap = QPixmap(str(ASSET_DIR / f"{prefix}_{idx}.png"))
            if pixmap.isNull():
                return []
            frames.append(pixmap)
        return frames

    def import_character_sheet_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self.settings_panel,
            "Select 4-frame sprite sheet",
            "",
            "Images (*.png *.webp *.jpg *.jpeg *.bmp)"
        )
        if not filename:
            return

        try:
            self.create_custom_character_frames(Path(filename))
            self.load_assets()
            self.current_frame_idx = 0
            self.trail_particles.clear()
            self.update_window_size()
            self.update()
            QMessageBox.information(self.settings_panel, "Character loaded", "Custom character applied.")
        except Exception as e:
            QMessageBox.warning(self.settings_panel, "Import failed", str(e))

    def create_custom_character_frames(self, source_path):
        ASSET_DIR.mkdir(exist_ok=True)
        image = Image.open(source_path).convert("RGBA")
        if image.width < 4 or image.height < 4:
            raise ValueError("Image is too small.")

        cells = []
        for idx in range(4):
            left = idx * image.width // 4
            right = (idx + 1) * image.width // 4
            cell = image.crop((left, 0, right, image.height))
            cell = self.remove_chroma_green(cell)
            bbox = cell.getbbox()
            if not bbox:
                raise ValueError(f"Frame {idx + 1} is empty after background removal.")
            cells.append(cell.crop(bbox))

        target_height = 72
        scaled = []
        for cell in cells:
            scale = target_height / cell.height
            target_width = max(1, round(cell.width * scale))
            scaled.append(cell.resize((target_width, target_height), Image.Resampling.LANCZOS))

        canvas_width = max(frame.width for frame in scaled) + 8
        canvas_height = target_height + 8
        baseline = canvas_height - 3
        normalized = []
        for idx, frame in enumerate(scaled):
            canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
            canvas.alpha_composite(frame, ((canvas_width - frame.width) // 2, baseline - frame.height))
            canvas.save(ASSET_DIR / f"{CUSTOM_FRAME_PREFIX}_{idx}.png")
            normalized.append(canvas)

        sheet = Image.new("RGBA", (canvas_width * 4, canvas_height), (0, 0, 0, 0))
        for idx, frame in enumerate(normalized):
            sheet.alpha_composite(frame, (idx * canvas_width, 0))
        sheet.save(ASSET_DIR / f"{CUSTOM_FRAME_PREFIX}_sheet.png")
        shutil.copyfile(source_path, ASSET_DIR / f"{CUSTOM_FRAME_PREFIX}_source{source_path.suffix.lower()}")

    def remove_chroma_green(self, image):
        image = image.copy()
        pixels = image.load()
        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]
                if a == 0:
                    continue

                bright_key = g > 150 and r < 135 and b < 135
                green_dominant = g > 70 and g > r * 1.22 and g > b * 1.22
                if bright_key or green_dominant:
                    strength = min(1.0, max(0.0, (g - max(r, b) - 20) / 120))
                    if strength > 0.35 or bright_key:
                        pixels[x, y] = (0, 0, 0, 0)
                    else:
                        pixels[x, y] = (r, min(g, max(r, b) + 8), b, int(a * (1 - strength)))
                elif g > max(r, b) + 18:
                    pixels[x, y] = (r, min(g, max(r, b) + 8), b, a)
        return image

    def reset_character(self):
        for idx in range(4):
            frame_path = ASSET_DIR / f"{CUSTOM_FRAME_PREFIX}_{idx}.png"
            if frame_path.exists():
                frame_path.unlink()
        sheet_path = ASSET_DIR / f"{CUSTOM_FRAME_PREFIX}_sheet.png"
        if sheet_path.exists():
            sheet_path.unlink()
        for path in ASSET_DIR.glob(f"{CUSTOM_FRAME_PREFIX}_source.*"):
            path.unlink()
        self.load_assets()
        self.current_frame_idx = 0
        self.trail_particles.clear()
        self.update_window_size()
        self.update()
        QMessageBox.information(self.settings_panel, "Reset", "Default character restored.")

    def update_frame(self):
        self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frames)
        self.wave_offset += 2 + max(0, self.move_speed - 5) * 0.2
        
        # Update background particles (Stars)
        if random.random() < self.particle_density / 180:
            p_x = random.randint(0, self.width())
            p_y = random.randint(0, self.height())
            self.particles.append({'x': p_x, 'y': p_y, 'life': 20, 'speed': random.randint(2, 5)})
            
        for p in self.particles:
            p['x'] -= p['speed']
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]

        if self.trail_enabled:
            self.spawn_trail_particles()

        for p in self.trail_particles:
            p['x'] -= p['speed']
            p['y'] += math.sin((self.wave_offset + p['phase']) * 0.15) * p['drift']
            p['z'] += p['vz']
            p['life'] -= 1
            p['twinkle'] += 0.25
        self.trail_particles = [p for p in self.trail_particles if p['life'] > 0]
        
        # Update 3D click particles
        for p in self.click_particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['z'] += p['vz'] # Z moves towards/away
            p['vy'] += 0.5 # Gravity
            p['life'] -= 1
            
        self.click_particles = [p for p in self.click_particles if p['life'] > 0 and p['z'] > 0.1]
        
        self.update()

    def auto_move(self):
        if self.dragging:
            return
            
        self.time_step += 0.2
        self.speed_x = self.move_speed
        self.speed_y = int(math.sin(self.time_step) * max(3, self.move_speed + 3))
        
        current_pos = self.pos()
        new_x = current_pos.x() + self.speed_x
        new_y = current_pos.y() + self.speed_y
        
        screen = QApplication.primaryScreen().geometry()
        if new_x > screen.width():
            new_x = -self.width()
        elif new_x < -self.width():
            new_x = screen.width()
            
        self.move(new_x, new_y)

    def start_work_mode(self):
        if not self.work_mode_enabled:
            return
        print(f"Starting work mode: See you in {self.rest_interval_minutes} minutes!")
        self.hide()
        self.work_timer.start(self.rest_interval_minutes * 60 * 1000)

    def return_from_work(self):
        self.overlay.showFullScreen()
        # We don't show self here, the overlay will show self when clicked

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        cat_pixmap = self.scaled_cat_pixmap()
        cat_x = self.width() - cat_pixmap.width() - 20
        cat_y = (self.height() - cat_pixmap.height()) // 2
        
        # Draw pixel rainbow base strips under the 3D sparkle field.
        segment_width = max(14, int(18 * self.cat_scale / 100))
        segment_height = max(2, cat_pixmap.height() // 6)
        num_segments = self.trail_depth

        if self.trail_enabled:
            for i in range(num_segments):
                x = cat_x - (i * segment_width)
                y_offset = int(math.sin((self.wave_offset + i) * 0.5) * max(3, cat_pixmap.height() * 0.08))
                alpha_scale = max(0.18, 1.0 - (i / max(1, num_segments)) * 0.55)
                
                for c_idx, color in enumerate(self.rainbow_colors):
                    band_color = QColor(color)
                    band_color.setAlpha(int(color.alpha() * alpha_scale))
                    painter.fillRect(x, cat_y + (c_idx * segment_height) + y_offset, 
                                     segment_width, segment_height, band_color)

            for p in sorted(self.trail_particles, key=lambda item: item['z']):
                if p['x'] < 2 or p['x'] > cat_x + cat_pixmap.width():
                    continue
                scale = 170 / (170 + p['z'])
                size = max(1, int(p['size'] * scale))
                alpha = int(210 * min(1.0, p['life'] / 30.0))
                glow = QColor(p['color'])
                glow.setAlpha(max(35, alpha // 3))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glow))
                painter.drawRect(int(p['x'] - size), int(p['y'] - size), size * 3, size * 3)
                color = QColor(p['color'])
                color.setAlpha(alpha)
                painter.setBrush(QBrush(color.lighter(130 + int(math.sin(p['twinkle']) * 30))))
                painter.drawRect(int(p['x']), int(p['y']), size, size)
                                 
        # Draw Particles (Stars)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.particles:
            painter.drawRect(p['x'], p['y'], 2, 2)
            
        # Draw 3D Click Particles
        # Sort by Z to draw back-to-front (simple painter's algorithm)
        # But here we just draw them on top for pop effect
        for p in self.click_particles:
            # Perspective projection
            scale = 200 / (200 + p['z'])
            screen_x = p['x']
            screen_y = p['y']
            size = int(5 * scale)
            
            if size > 0:
                color = QColor(p['color'])
                color.setAlpha(int(255 * min(1.0, p['life'] / 20.0)))
                painter.setBrush(QBrush(color))
                painter.drawRect(int(screen_x), int(screen_y), size, size)
        
        # Draw Cat
        painter.drawPixmap(cat_x, cat_y, cat_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.start_drag_pos = event.globalPosition().toPoint()
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_drag_gesture = False
            self.press_timer.restart()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.globalPosition().toPoint()
            # A larger threshold prevents slow drags from becoming accidental clicks.
            if (current_pos - self.start_drag_pos).manhattanLength() > 10:
                self.is_drag_gesture = True
                
            self.move(current_pos - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            distance = (event.globalPosition().toPoint() - self.start_drag_pos).manhattanLength()
            short_press = self.press_timer.isValid() and self.press_timer.elapsed() < 240
            if short_press and distance <= 6 and not self.is_drag_gesture:
                self.spawn_click_particles(event.position())
                self.start_work_mode()
        self.dragging = False

    def show_context_menu(self, pos):
        menu = QMenu()
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        menu.exec(pos)

    def show_settings(self):
        if self.settings_panel.isVisible():
            self.settings_panel.hide()
        else:
            self.settings_panel.move(self.x() - self.settings_panel.width() - 10, self.y())
            self.settings_panel.show()
            self.settings_panel.raise_()

    def scaled_cat_pixmap(self):
        pixmap = self.frames[self.current_frame_idx]
        if self.cat_scale == 100:
            return pixmap
        width = max(1, int(pixmap.width() * self.cat_scale / 100))
        height = max(1, int(pixmap.height() * self.cat_scale / 100))
        return pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)

    def update_window_size(self):
        pixmap = self.scaled_cat_pixmap() if self.frames else QPixmap(64, 40)
        trail_space = self.trail_tail_width() + max(80, self.particle_density * 2)
        self.resize(max(320, pixmap.width() + trail_space + 90), max(170, pixmap.height() + 115))

    def trail_tail_width(self):
        segment_width = max(14, int(18 * self.cat_scale / 100))
        return max(180, self.trail_depth * segment_width + 110)

    def spawn_trail_particles(self):
        if self.particle_density <= 0:
            return
        cat_pixmap = self.scaled_cat_pixmap()
        cat_x = self.width() - cat_pixmap.width() - 20
        cat_y = (self.height() - cat_pixmap.height()) // 2
        count = max(1, self.particle_density // 18)
        tail_width = self.trail_tail_width()
        for _ in range(count):
            band = random.randrange(len(self.rainbow_colors))
            distance = random.randint(10, tail_width)
            depth = distance / max(1, tail_width)
            self.trail_particles.append({
                'x': cat_x - distance,
                'y': cat_y + band * max(2, cat_pixmap.height() // 6) + random.randint(-5, 8),
                'z': random.uniform(0, 120) + depth * 80,
                'vz': random.uniform(-0.8, 1.2),
                'speed': random.uniform(2.5, 6.5 + self.move_speed * 0.2),
                'size': random.randint(2, 6),
                'life': random.randint(20, 52),
                'phase': random.uniform(0, 20),
                'drift': random.uniform(0.3, 2.4),
                'twinkle': random.uniform(0, math.tau),
                'color': self.rainbow_colors[band],
            })

    def spawn_click_particles(self, position):
        if self.particle_density <= 0:
            return
        for _ in range(8 + self.particle_density // 2):
            self.click_particles.append({
                'x': position.x(),
                'y': position.y(),
                'z': 0,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-5, 5),
                'vz': random.uniform(1, 10),
                'life': 40,
                'color': random.choice(self.rainbow_colors)
            })

    def set_rest_interval(self, minutes):
        self.rest_interval_minutes = minutes

    def set_work_mode_enabled(self, enabled):
        self.work_mode_enabled = enabled
        if not enabled and self.work_timer.isActive():
            self.work_timer.stop()
            self.show()

    def set_cat_scale(self, value):
        old_center = self.geometry().center()
        self.cat_scale = value
        self.update_window_size()
        self.move(old_center - self.rect().center())
        self.update()

    def set_move_speed(self, value):
        self.move_speed = value
        self.speed_x = value

    def set_particle_density(self, value):
        self.particle_density = value
        self.update_window_size()

    def set_trail_depth(self, value):
        self.trail_depth = value
        self.update_window_size()

    def set_trail_enabled(self, enabled):
        self.trail_enabled = enabled
        if not enabled:
            self.trail_particles.clear()
        self.update()
