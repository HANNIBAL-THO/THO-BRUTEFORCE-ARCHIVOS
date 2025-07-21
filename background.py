from PySide6.QtCore import Qt, QPointF, QTimer, QRectF, QPropertyAnimation, Property, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen, QLinearGradient, QRadialGradient, QPainterPath, QBrush
from PySide6.QtWidgets import QWidget
import math
import random

COLOR_BG = QColor(40, 40, 40, 0)  
COLOR_PRIMARY = QColor(50, 205, 50)  
COLOR_SECONDARY = QColor(124, 252, 0)  
COLOR_TEXT = QColor(0, 255, 0)  
COLOR_DISABLED = QColor(80, 80, 80)  

class Dot:
    def __init__(self, x, y, parent=None, size=4, speed=0.7):
        self.x = x
        self.y = y
        self.size = size
        self.original_size = size
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.target_x = x
        self.target_y = y
        self.parent_widget = parent
        self.set_random_target()
        self.connections = []
        self.pulse_size = 0
        self.pulse_speed = random.uniform(0.02, 0.05)
        self.pulse_dir = 1

    def set_random_target(self):
      
        if not self.parent_widget:
            return
            
        padding = 50
        width = self.parent_widget.width()
        height = self.parent_widget.height()
        
        self.target_x = random.uniform(padding, width - padding)
        self.target_y = random.uniform(padding, height - padding)
        self.angle = math.atan2(self.target_y - self.y, self.target_x - self.x)

    def move(self, width, height):
        
        self.pulse_size += self.pulse_speed * self.pulse_dir
        if abs(self.pulse_size) > 5:
            self.pulse_dir *= -1
            
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        
        if dist > 0:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed
            
        self.x = max(0, min(self.x + dx, width))
        self.y = max(0, min(self.y + dy, height))
        
        dist_to_target = ((self.x - self.target_x) ** 2 + (self.y - self.target_y) ** 2) ** 0.5
        if dist_to_target < 5 or self.x <= 0 or self.x >= width or self.y <= 0 or self.y >= height:
            self.set_random_target()
            
    def draw(self, painter, width, height):
       
        for other_dot in self.connections:
            if other_dot:
                dist = ((self.x - other_dot.x) ** 2 + (self.y - other_dot.y) ** 2) ** 0.5
                if dist < 120:  
                   
                    line_width = 1.5 * (1 - dist / 150)
                    if line_width > 0:
                       
                        gradient = QLinearGradient(self.x, self.y, other_dot.x, other_dot.y)
                        gradient.setColorAt(0, QColor(0, 255, 0, 100))  
                        gradient.setColorAt(1, QColor(0, 200, 0, 40))   
                        
                        painter.setPen(QPen(QBrush(gradient), line_width, Qt.SolidLine, Qt.RoundCap))
                        painter.drawLine(int(self.x), int(self.y), int(other_dot.x), int(other_dot.y))
        
        pulse_factor = 1 + math.sin(self.pulse_size) * 0.3  
        dot_size = int(self.original_size * pulse_factor)
        
        radial = QRadialGradient(self.x, self.y, dot_size * 1.5)
        radial.setColorAt(0, QColor(0, 255, 0, 220))  
        radial.setColorAt(0.7, QColor(0, 200, 0, 150)) 
        radial.setColorAt(1, QColor(0, 150, 0, 40))  
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(radial))
        painter.drawEllipse(int(self.x - dot_size/2), int(self.y - dot_size/2), dot_size, dot_size)

class MovingDotsBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  
        
        self.primary_dots = []
        self.secondary_dots = []
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(30)  
        
        self.primary_count = 40
        self.secondary_count = 40
        
        self.resize(800, 600)
        
        self.time = 0
        
    def resizeEvent(self, event):
       
        width = self.width()
        height = self.height()
        
        if not self.primary_dots:
            for _ in range(self.primary_count):
                x = random.randint(0, width)
                y = random.randint(0, height)
                self.primary_dots.append(Dot(x, y, self, size=5, speed=0.5))
        
        if not self.secondary_dots:
            for _ in range(self.secondary_count):
                x = random.randint(0, width)
                y = random.randint(0, height)
                self.secondary_dots.append(Dot(x, y, self, size=2, speed=0.3))
        
        for dot in self.primary_dots + self.secondary_dots:
            dot.x = min(max(dot.x, 0), width)
            dot.y = min(max(dot.y, 0), height)
            dot.set_random_target()
    
    def update_dots(self):
        if not self.isVisible():
            return
            
        width = self.width()
        height = self.height()
        self.time += 0.05  
        
        for dot in self.primary_dots:
            dot.move(width, height)
            
       
        for dot in self.secondary_dots:
        
            dot.move(width, height)
            
        self.update_connections()
        
        self.update()
    
    def update_connections(self):
      
        all_dots = self.primary_dots + self.secondary_dots
        for dot in all_dots:
            dot.connections = []
            
        for i, dot1 in enumerate(all_dots):
            for j in range(i + 1, len(all_dots)):
                dot2 = all_dots[j]
                dist = ((dot1.x - dot2.x) ** 2 + (dot1.y - dot2.y) ** 2) ** 0.5
                
                max_dist = 120  
                
                if dot1 in self.primary_dots and dot2 in self.primary_dots:
                    max_dist = 150
                
                if dist < max_dist:
                  
                    should_connect = True
                    
                    if dot1.connections:  
                        for conn in dot1.connections:
                            
                            dx1 = dot2.x - dot1.x
                            dy1 = dot2.y - dot1.y
                            dx2 = conn.x - dot1.x
                            dy2 = conn.y - dot1.y
                            
                            dot_product = dx1 * dx2 + dy1 * dy2
                            mag1 = (dx1**2 + dy1**2) ** 0.5
                            mag2 = (dx2**2 + dy2**2) ** 0.5
                            
                            if mag1 > 0 and mag2 > 0:
                                angle = math.degrees(math.acos(min(1, max(-1, dot_product / (mag1 * mag2)))))
                                if angle < 30:  
                                    should_connect = False
                                    break
                    
                    if should_connect and dot2 not in dot1.connections:
                        dot1.connections.append(dot2)
                        dot2.connections.append(dot1)
    
    def paintEvent(self, event):
        if not self.isVisible():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        painter.fillRect(self.rect(), Qt.transparent)
        
        width = self.width()
        height = self.height()
        
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(0, 20, 0, 30))  
        gradient.setColorAt(1, QColor(0, 40, 0, 10))  
        painter.fillRect(self.rect(), gradient)
        
        for dot in self.primary_dots + self.secondary_dots:
            for conn in dot.connections:
                if conn in self.primary_dots or conn in self.secondary_dots:
           
                    if id(dot) < id(conn):
                        dist = ((dot.x - conn.x) ** 2 + (dot.y - conn.y) ** 2) ** 0.5
                        if dist < 150:  
                           
                            line_width = 1.2 * (1 - dist / 180)
                            if line_width > 0.1:
                               
                                grad = QLinearGradient(dot.x, dot.y, conn.x, conn.y)
                                alpha = int(120 * (1 - dist/180)) 
                                grad.setColorAt(0, QColor(0, 255, 0, alpha))
                                grad.setColorAt(1, QColor(0, 200, 0, alpha//2))
                                
                                painter.setPen(QPen(QBrush(grad), line_width, Qt.SolidLine, Qt.RoundCap))
                                painter.drawLine(int(dot.x), int(dot.y), int(conn.x), int(conn.y))
        
        for dot in self.secondary_dots + self.primary_dots:
            dot.draw(painter, width, height)
        
        painter.end()
        
    def cleanup(self):
        
        try:
            if hasattr(self, 'timer') and self.timer and self.timer.isActive():
                self.timer.stop()
                
            if hasattr(self, 'primary_dots'):
                self.primary_dots.clear()
            if hasattr(self, 'secondary_dots'):
                self.secondary_dots.clear()
        except RuntimeError:
            
            pass
    
    def __del__(self):
        self.cleanup()
