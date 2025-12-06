import sys
import random
import math
from PyQt6.QtWidgets import QWidget, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QPointF
from PyQt6.QtGui import QPainter, QPixmap, QColor, QAction, QCursor, QBrush, QPen, QRadialGradient, QConicalGradient, QFont

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
        
        # Auto movement
        self.auto_move_timer = QTimer(self)
        self.auto_move_timer.timeout.connect(self.auto_move)
        self.auto_move_timer.start(50)
        self.speed_x = 5 # Faster movement
        self.speed_y = 0
        self.time_step = 0
        
        # Effects
        self.particles = []
        self.click_particles = [] # 3D particles
        
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
        self.resize(300, 150)
        
        # Initial position
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() // 2, screen.height() // 2)

        # Work Mode (Pomodoro)
        self.work_timer = QTimer(self)
        self.work_timer.setSingleShot(True)
        self.work_timer.timeout.connect(self.return_from_work)
        self.overlay = WorkStopperOverlay(self)
        
        self.start_drag_pos = QPoint()
        self.is_drag_gesture = False

    def load_assets(self):
        try:
            full_pixmap = QPixmap("assets/nyan_cat.png")
            if full_pixmap.isNull():
                raise Exception("Failed to load nyan_cat.png")
            self.frames = [full_pixmap]
        except Exception as e:
            print(f"Error loading assets: {e}")
            pixmap = QPixmap(64, 40)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QBrush(Qt.GlobalColor.gray))
            painter.drawRect(0, 0, 64, 40)
            painter.end()
            self.frames = [pixmap]

    def update_frame(self):
        self.current_frame_idx = (self.current_frame_idx + 1) % len(self.frames)
        self.wave_offset += 2 # Faster wave
        
        # Update background particles (Stars)
        if random.random() < 0.4:
            p_x = random.randint(0, self.width())
            p_y = random.randint(0, self.height())
            self.particles.append({'x': p_x, 'y': p_y, 'life': 20, 'speed': random.randint(2, 5)})
            
        for p in self.particles:
            p['x'] -= p['speed']
            p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]
        
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
        self.speed_y = int(math.sin(self.time_step) * 8)
        
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
        print("Starting work mode: See you in 25 minutes!")
        self.hide()
        # 25 minutes = 25 * 60 * 1000 ms
        # For testing purposes, I'll set this to 5 seconds if you want to verify quickly, 
        # but per requirements it is 25 minutes.
        # self.work_timer.start(5000) # 5 seconds debug
        self.work_timer.start(25 * 60 * 1000) 

    def return_from_work(self):
        self.overlay.showFullScreen()
        # We don't show self here, the overlay will show self when clicked

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        cat_pixmap = self.frames[self.current_frame_idx]
        cat_x = self.width() - cat_pixmap.width() - 20
        cat_y = (self.height() - cat_pixmap.height()) // 2
        
        # Draw Rainbow Trail (Shorter)
        segment_width = 20
        segment_height = cat_pixmap.height() // 6
        num_segments = 6 # Shorter trail
        
        for i in range(num_segments):
            x = cat_x - (i * segment_width)
            y_offset = int(math.sin((self.wave_offset + i) * 0.5) * 5)
            
            for c_idx, color in enumerate(self.rainbow_colors):
                painter.fillRect(x, cat_y + (c_idx * segment_height) + y_offset, 
                                 segment_width, segment_height, color)
                                 
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
                color = p['color']
                color.setAlpha(int(255 * min(1.0, p['life'] / 20.0)))
                painter.setBrush(QBrush(color))
                painter.drawEllipse(int(screen_x), int(screen_y), size, size)
        
        # Draw Cat
        painter.drawPixmap(cat_x, cat_y, cat_pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.start_drag_pos = event.globalPosition().toPoint()
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_drag_gesture = False
            
            # Spawn 3D particles
            for _ in range(20):
                self.click_particles.append({
                    'x': event.position().x(),
                    'y': event.position().y(),
                    'z': 0,
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-5, 5),
                    'vz': random.uniform(1, 10),
                    'life': 40,
                    'color': random.choice(self.rainbow_colors)
                })
                
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.globalPosition().toPoint()
            # If moved more than 5 pixels, consider it a drag
            if (current_pos - self.start_drag_pos).manhattanLength() > 5:
                self.is_drag_gesture = True
                
            self.move(current_pos - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.is_drag_gesture:
                # It was a click!
                self.start_work_mode()
        self.dragging = False

    def show_context_menu(self, pos):
        menu = QMenu()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        menu.exec(pos)
