import sys
import os
import threading
import time
import pyzipper
import zipfile
import rarfile
import py7zr
import getpass
import shutil
from PySide6.QtCore import QEvent, Qt, QTimer, QFile, QTextStream, QPoint, QSize, QObject, Signal, QMetaObject, Q_ARG
from PySide6.QtGui import QIcon, QColor, QPainter, QPen, QFont, QLinearGradient, QBrush, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QTextEdit, QProgressBar, QMessageBox, 
    QLineEdit, QHBoxLayout, QRadioButton, QButtonGroup,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect, QStyle
)

class SuccessEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, title, message):
        super().__init__(self.EVENT_TYPE)
        self.title = title
        self.message = message
from PySide6.QtCore import Qt, QTimer, QFile, QTextStream, QPoint, QSize
from PySide6.QtGui import QIcon, QColor, QPainter, QPen, QFont, QLinearGradient, QBrush, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QTextEdit, QProgressBar, QMessageBox, 
    QLineEdit, QHBoxLayout, QRadioButton, QButtonGroup,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)

from background import MovingDotsBackground

script_dir = os.path.dirname(os.path.abspath(__file__))
rarfile.UNRAR_TOOL = os.path.join(script_dir, 'assets', 'unrar.exe')

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(32)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(10)
        
        self.title_container = QWidget()
        self.title_layout = QHBoxLayout(self.title_container)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setSpacing(10)
        
        self.logo = QLabel()
        self.logo.setPixmap(QIcon(os.path.join(script_dir, "assets", "cyberius.ico")).pixmap(24, 24))
        self.title = QLabel("THO BRUTEFORCE | BY HANNIBAL THO | DISCORD : discord.gg/uPESr5v7yQ ")
        
        self.title_layout.addWidget(self.logo)
        self.title_layout.addWidget(self.title)
        self.title_layout.addStretch()
        
        self.control_buttons = QWidget()
        self.control_layout = QHBoxLayout(self.control_buttons)
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.setSpacing(5)
        
        self.minimize_button = QPushButton("—")
        self.maximize_button = QPushButton("□")
        self.close_button = QPushButton("✕")
        
        for btn in [self.minimize_button, self.maximize_button, self.close_button]:
            btn.setFixedSize(24, 24)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: lime;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: rgba(50, 50, 50, 200);
                }
                QPushButton:pressed {
                    background-color: rgba(30, 30, 30, 200);
                }
            """)
        
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #ff5555;
                border: none;
                font-weight: bold;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(255, 85, 85, 50);
            }
            QPushButton:pressed {
                background-color: rgba(255, 85, 85, 30);
            }
        """)
        
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.close_button.clicked.connect(self.parent.close)
     
        self.control_layout.addWidget(self.minimize_button)
        self.control_layout.addWidget(self.maximize_button)
        self.control_layout.addWidget(self.close_button)
        
        self.layout.addWidget(self.title_container)
        self.layout.addStretch()
        self.layout.addWidget(self.control_buttons)
        
        self.setStyleSheet("""
            background-color: rgba(20, 20, 20, 220);
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        
        self.title.setStyleSheet("""
            QLabel {
                color: lime;
                font-weight: bold;
                font-size: 12px;
            }
        """)
    
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_button.setText("□")
        else:
            self.parent.showMaximized()
            self.maximize_button.setText("❐")

class GlassPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            background-color: rgba(10, 10, 10, 80);
            border-radius: 8px;
            border: 1px solid rgba(0, 255, 0, 50);
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(32)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(40, 40, 40, 200);
                color: lime;
                border: 1px solid rgba(0, 255, 0, 80);
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(0, 255, 0, 120);
            }
            QPushButton:pressed {
                background-color: rgba(30, 30, 30, 200);
            }
            QPushButton:disabled {
                color: rgb(100, 120, 80);
                border: 1px solid rgba(100, 120, 80, 80);
                background-color: rgba(30, 30, 30, 100);
            }
        """)

class PrimaryButton(StyledButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 255, 0, 30);
                color: lime;
                border: 2px solid lime;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 0, 50);
            }
            QPushButton:pressed {
                background-color: rgba(0, 255, 0, 20);
            }
            QPushButton:disabled {
                color: rgb(100, 120, 80);
                border: 2px solid rgba(100, 120, 80, 80);
                background-color: rgba(30, 30, 30, 100);
            }
        """)

class StyledRadioButton(QRadioButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QRadioButton {
                color: lime;
                padding: 4px 4px 4px 24px;
                font-size: 12px;
                min-height: 20px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid lime;
                border-radius: 8px;
                background-color: rgba(20, 20, 20, 200);
            }
            QRadioButton::indicator:checked {
                background-color: lime;
                border: 2px solid lime;
            }
            QRadioButton:hover {
                color: rgb(200, 255, 150);
            }
        """)

class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(32)
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(40, 40, 40, 200);
                color: lime;
                border: 1px solid rgba(0, 255, 0, 80);
                border-radius: 6px;
                padding: 6px 12px;
                selection-background-color: rgba(0, 255, 0, 100);
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 255, 0, 150);
            }
        """)

class StyledTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(30, 30, 30, 200);
                color: lime;
                border: 1px solid rgba(0, 255, 0, 80);
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Monospace';
                font-size: 11px;
            }
        """)

class StyledProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(0, 255, 0, 80);
                border-radius: 4px;
                text-align: center;
                color: lime;
                background-color: rgba(30, 30, 30, 200);
                height: 20px;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: lime;
                width: 10px;
                margin: 0.5px;
                border-radius: 2px;
            }
        """)

class SectionTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                color: lime;
                font-size: 13px;
                font-weight: bold;
                margin: 8px 0 4px 0;
                padding-bottom: 4px;
                border-bottom: 1px solid rgba(0, 255, 0, 50);
            }
        """)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.running = False
        self.current_thread = None
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("THO BRUTEFORCE")
        self.resize(900, 700)
        self.center_window()
        
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                color: lime;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit, QLineEdit, QPushButton, QLabel, QRadioButton, QProgressBar {
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.main_layout.setSpacing(0)
        
        self.background = MovingDotsBackground(self)
        def resizeEvent(self, event):
            
            if hasattr(self, 'background'):
                self.background.setGeometry(0, 0, self.width(), self.height())
            super().resizeEvent(event)
        self.background.lower()  
        
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        self.content = QWidget()
        self.content.setStyleSheet("background-color: rgba(10, 10, 10, 120); border-radius: 0 0 8px 8px;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(15)
        
        self.glass_panel = GlassPanel()
        self.panel_layout = QVBoxLayout(self.glass_panel)
        self.panel_layout.setContentsMargins(15, 15, 15, 15)
        self.panel_layout.setSpacing(12)
        
        self.username = getpass.getuser()
        self.archive_path = None
        self.dict_path = None
        self.output_path = None
        self.correct_password = None
        self.logs = []
        
        self.drag_position = None
        
        self.init_ui()
        
        self.content_layout.addWidget(self.glass_panel)
        self.main_layout.addWidget(self.content)
        
        self.log_updater = QTimer()
        self.log_updater.timeout.connect(self.update_log)
        self.log_updater.start(100)
    
    def center_window(self):
        frame = self.frameGeometry()
        center_point = self.screen().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < self.title_bar.height():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.drag_position = None
    
    def init_ui(self):
        
        title = QLabel("THO BRUTEFORCE")
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: bold;
                color: lime;
                text-align: center;
                margin: 0 0 12px 0;
                padding-bottom: 8px;
                border-bottom: 1px solid rgba(0, 255, 0, 50);
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        self.panel_layout.addWidget(title)
        
        user_info = QLabel(f"👤 Usuario actual: {self.username}")
        work_dir = QLabel(f"📂 Carpeta de trabajo: {script_dir}")
        work_dir.setWordWrap(True)
        
        self.panel_layout.addWidget(user_info)
        self.panel_layout.addWidget(work_dir)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0, 255, 0, 30);")
        self.panel_layout.addWidget(separator)
        
        self.panel_layout.addWidget(SectionTitle("Archivo Comprimido"))
        
        self.label = QLabel("📎 Ningún archivo seleccionado")
        self.label.setWordWrap(True)
        
        self.zip_button = StyledButton("Seleccionar archivo (.zip, .rar, .7z)")
        self.zip_button.clicked.connect(self.select_archive)
        
        self.panel_layout.addWidget(self.label)
        self.panel_layout.addWidget(self.zip_button)
        
        self.panel_layout.addWidget(SectionTitle("Método de Ataque"))
        
        mode_group = QButtonGroup(self)
        self.radio_brute = StyledRadioButton("Usar diccionario")
        self.radio_manual = StyledRadioButton("Usar contraseña manual")
        self.radio_brute.setChecked(True)
        
        mode_group.addButton(self.radio_brute)
        mode_group.addButton(self.radio_manual)
        
        radio_container = QWidget()
        radio_container.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid rgba(0, 255, 0, 80);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        radio_layout = QHBoxLayout(radio_container)
        radio_layout.setContentsMargins(5, 5, 5, 5)
        radio_layout.setSpacing(20)
        
        radio_layout.addWidget(self.radio_brute)
        radio_layout.addWidget(self.radio_manual)
        radio_layout.addStretch()
        
        self.panel_layout.addWidget(radio_container)
        
        self.dict_button = StyledButton("Seleccionar Diccionario (.txt)")
        self.dict_button.clicked.connect(self.select_dict)
        self.dict_button.setEnabled(True)
        
        self.manual_pass = StyledLineEdit("🔐 Ingrese la contraseña manualmente")
        self.manual_pass.setEnabled(False)
        
        self.radio_brute.toggled.connect(self.toggle_mode)
        self.radio_manual.toggled.connect(self.toggle_mode)
        
        self.panel_layout.addWidget(self.dict_button)
        self.panel_layout.addWidget(self.manual_pass)
        
        self.panel_layout.addWidget(SectionTitle("Destino de Extracción"))
        
        self.output_label = QLabel("📁 Ninguna carpeta seleccionada")
        self.output_label.setWordWrap(True)
        
        self.output_button = StyledButton("Seleccionar carpeta de destino")
        self.output_button.clicked.connect(self.select_output)
        
        self.panel_layout.addWidget(self.output_label)
        self.panel_layout.addWidget(self.output_button)
        
        self.start_button = PrimaryButton("🚀 INICIAR BRUTEFORCE")
        self.start_button.clicked.connect(self.start_process)
        self.panel_layout.addWidget(self.start_button)
        
        self.progress_bar = StyledProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Listo")
        self.panel_layout.addWidget(self.progress_bar)
        
        self.panel_layout.addWidget(SectionTitle("Registro de Actividad"))
        
        self.log = StyledTextEdit()
        self.log.setMinimumHeight(150)
        self.panel_layout.addWidget(self.log)
        
        self.panel_layout.addStretch()
    
    def toggle_mode(self):
        is_manual = self.radio_manual.isChecked()
        self.dict_button.setEnabled(not is_manual)
        self.manual_pass.setEnabled(is_manual)
    
    def select_archive(self):
        file_filter = "Archivos comprimidos (*.zip *.rar *.7z);;Todos los archivos (*.*)"
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo comprimido", "", file_filter)
        
        if file_name:
            self.archive_path = file_name
            self.label.setText(f"📎 Archivo seleccionado: {os.path.basename(file_name)}")
    
    def select_dict(self):
        file_filter = "Archivos de texto (*.txt);;Todos los archivos (*.*)"
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de diccionario", "", file_filter)
        
        if file_name:
            self.dict_path = file_name
            self.dict_button.setText(f"📝 {os.path.basename(file_name)}")
    
    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino")
        
        if folder:
            self.output_path = folder
            self.output_label.setText(f"📁 Carpeta de destino: {folder}")
    
    def update_log(self):
        try:
            if hasattr(self, 'log') and hasattr(self, 'logs') and self.logs:
                
                logs_copy = self.logs.copy()
                log_text = '\n'.join(logs_copy[-100:]) 
                self.log.setPlainText(log_text)
                self.log.verticalScrollBar().setValue(
                    self.log.verticalScrollBar().maximum()
                )
        except Exception as e:
            print(f"Error in update_log: {str(e)}")
    
    def safe_log(self, message):
        if not hasattr(self, 'logs'):
            self.logs = []
        
        self.logs.append(message)
        
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]
    
    def set_ui_enabled(self, enabled):
        self.zip_button.setEnabled(enabled)
        self.dict_button.setEnabled(enabled and not self.radio_manual.isChecked())
        self.radio_brute.setEnabled(enabled)
        self.radio_manual.setEnabled(enabled)
        self.manual_pass.setEnabled(enabled and self.radio_manual.isChecked())
        self.output_button.setEnabled(enabled)
        self.start_button.setEnabled(enabled)
        
        if enabled:
            self.start_button.setText(" INICIAR BRUTEFORCE")
        else:
            self.start_button.setText("Procesando...")
    
    def check_thread_status(self):
        if hasattr(self, 'current_thread') and self.current_thread and self.current_thread.is_alive():
            return True
        return False
            
    def start_process(self):
        try:
           
            self.set_ui_enabled(False)
            
            if not hasattr(self, 'archive_path') or not os.path.exists(self.archive_path):
                self.show_error("Error", "Por favor selecciona un archivo comprimido")
                self.set_ui_enabled(True)
                return
                
            if not hasattr(self, 'output_path') or not os.path.isdir(self.output_path):
                self.show_error("Error", "Por favor selecciona una carpeta de destino")
                self.set_ui_enabled(True)
                return
                
            if not self.radio_manual.isChecked() and (not hasattr(self, 'dict_path') or not os.path.isfile(self.dict_path)):
                self.show_error("Error", "Por favor selecciona un diccionario de contraseñas")
                self.set_ui_enabled(True)
                return
                
            self.log.clear()
            self.logs = []
            
            if not hasattr(self, 'log_timer'):
                self.log_timer = QTimer()
                self.log_timer.timeout.connect(self.update_log)
            
            self.log_timer.start(100)  
            
            if self.radio_manual.isChecked():
                password = self.manual_pass.text().strip()
                if not password:
                    self.show_error("Error", "Por favor ingresa una contraseña")
                    self.set_ui_enabled(True)
                    return
                thread = threading.Thread(target=self.test_password, args=(password,))
            else:
                thread = threading.Thread(target=self.brute_force_archive)
            
            thread.daemon = True
            thread.start()
            
            if not hasattr(self, 'thread_check_timer'):
                self.thread_check_timer = QTimer()
                self.thread_check_timer.timeout.connect(self.check_thread_status)
            
            self.thread_check_timer.start(500)  
            
        except Exception as e:
            self.safe_log(f"❌ Error al iniciar el proceso: {str(e)}")
            self.set_ui_enabled(True)
            if hasattr(self, 'log_timer') and self.log_timer.isActive():
                self.log_timer.stop()
            if hasattr(self, 'thread_check_timer') and self.thread_check_timer.isActive():
                self.thread_check_timer.stop()
    
    def extract_with_retry(self, archive_path, password, output_path=None, is_nested=False):
        """Helper method to extract files with password retry logic"""
        if output_path is None:
            output_path = self.output_path
            
        ext = os.path.splitext(archive_path)[1].lower()
        success = False
        extracted_files = []
        
        try:
            self.safe_log(f"🔍 Procesando archivo: {os.path.basename(archive_path)}")
            
            if ext == ".zip":
                try:
                    with pyzipper.AESZipFile(archive_path) as zf:
                        try:
                           
                            file_list = zf.namelist()
                            if not file_list:
                                self.safe_log("⚠️ El archivo ZIP está vacío")
                                return False, []
                                
                            first_file = file_list[0]
                            with zf.open(first_file, 'r', pwd=password.encode('utf-8')) as f:
                                f.read(1)  
                                
                            self.safe_log(f"✅ Contraseña correcta para {os.path.basename(archive_path)}")
                            
                            zf.extractall(path=output_path, pwd=password.encode('utf-8'))
                            extracted_files = [os.path.join(output_path, f) for f in file_list]
                            success = True
                            
                        except (RuntimeError, zipfile.BadZipFile) as e:
                            if "Bad password" in str(e) or "Bad password for file" in str(e):
                                return False, []
                            raise
                            
                except Exception as e:
                    self.safe_log(f"❌ Error al procesar archivo ZIP: {str(e)}")
                    return False, []
                        
            elif ext == ".rar":
                try:
                    with rarfile.RarFile(archive_path) as rf:
                        try:
                            
                            file_list = rf.namelist()
                            if not file_list:
                                self.safe_log("⚠️ El archivo RAR está vacío")
                                return False, []
                                
                            first_file = file_list[0]
                            with rf.open(first_file, 'r', pwd=password) as f:
                                f.read(1)  
                                
                            self.safe_log(f"✅ Contraseña correcta para {os.path.basename(archive_path)}")
                            
                            rf.extractall(path=output_path, pwd=password)
                            extracted_files = [os.path.join(output_path, f) for f in file_list]
                            success = True
                            
                        except (rarfile.BadRarFile, rarfile.BadRarName) as e:
                            if "Bad password" in str(e) or "password" in str(e).lower():
                                return False, []
                            raise
                            
                except Exception as e:
                    self.safe_log(f"❌ Error al procesar archivo RAR: {str(e)}")
                    return False, []
                        
            elif ext == ".7z":
                try:
                    with py7zr.SevenZipFile(archive_path, mode='r', password=password) as zf:
                        try:
                            
                            file_list = zf.getnames()
                            if not file_list:
                                self.safe_log("⚠️ El archivo 7z está vacío")
                                return False, []
                                
                            zf.getinfo(file_list[0])
                            self.safe_log(f"✅ Contraseña correcta para {os.path.basename(archive_path)}")
                            
                            zf.extractall(path=output_path)
                            extracted_files = [os.path.join(output_path, f) for f in file_list]
                            success = True
                            
                        except (py7zr.Bad7zFile, Exception) as e:
                            if "password" in str(e).lower() or "crc" in str(e).lower():
                                return False, []
                            raise
                            
                except Exception as e:
                    self.safe_log(f"❌ Error al procesar archivo 7z: {str(e)}")
                    return False, []
            
            if success and extracted_files:
                self.safe_log(f"✅ Extraídos {len(extracted_files)} archivos de {os.path.basename(archive_path)}")
            
            return success, extracted_files
            
        except Exception as e:
            error_msg = f"Error inesperado al procesar {os.path.basename(archive_path)}: {str(e)}"
            self.safe_log(f"❌ {error_msg}")
            return False, []
    
    def test_password(self, password):
        try:
            ext = os.path.splitext(self.archive_path)[1].lower()
            temp_dir = os.path.join(self.output_path, "_temp_extraction")
                
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            os.makedirs(temp_dir, exist_ok=True)
                
            self.safe_log("\n" + "="*50)
            self.safe_log(f"🔍 Probando contraseña: {password}")
                
            success, extracted_files = self.extract_with_retry(self.archive_path, password, temp_dir)
            if not success:
                return False
                
            self.safe_log(f"✅ ¡Contraseña correcta!: {password}")
            self.safe_log(f"📂 Archivos extraídos a: {self.output_path}")
                
            nested_archives = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in ['.zip', '.rar', '.7z']:
                        nested_archives.append(os.path.join(root, file))
            
            if nested_archives:
                self.safe_log(f"🔍 Se encontraron {len(nested_archives)} archivos anidados")
                
                for nested_archive in nested_archives:
                    rel_path = os.path.relpath(nested_archive, temp_dir)
                    output_subdir = os.path.join(self.output_path, os.path.dirname(rel_path))
                    os.makedirs(output_subdir, exist_ok=True)
                    
                    self.safe_log(f"🔍 Procesando archivo anidado: {os.path.basename(nested_archive)}")
                    
                    nested_success, _ = self.extract_with_retry(
                        nested_archive, 
                        password, 
                        output_path=output_subdir,
                        is_nested=True
                    )
                    
                    if not nested_success:
                        self.safe_log(f"⚠️ No se pudo extraer el archivo anidado: {os.path.basename(nested_archive)}")
                        self.safe_log("ℹ️  El archivo anidado puede requerir una contraseña diferente")
            
            self.safe_log("📂 Moviendo archivos a la ubicación final...")
            
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join(self.output_path, os.path.basename(item))
                
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        
                        for subitem in os.listdir(src):
                            try:
                                shutil.move(os.path.join(src, subitem), 
                                         os.path.join(dst, os.path.basename(subitem)))
                            except Exception as e:
                                self.safe_log(f"⚠️ No se pudo mover {subitem}: {str(e)}")
                    else:
                       
                        base, ext = os.path.splitext(item)
                        counter = 1
                        while os.path.exists(dst):
                            new_name = f"{base}_{counter}{ext}"
                            dst = os.path.join(self.output_path, new_name)
                            counter += 1
                        try:
                            shutil.move(src, dst)
                        except Exception as e:
                            self.safe_log(f"⚠️ No se pudo mover {item}: {str(e)}")
                else:
                    try:
                        shutil.move(src, dst)
                    except Exception as e:
                        self.safe_log(f"⚠️ No se pudo mover {item}: {str(e)}")
            
            self.safe_log("✅ ¡Extracción completada exitosamente!")
            self.safe_log("="*50 + "\n")
            
            QApplication.instance().postEvent(
                self, 
                SuccessEvent(
                    "¡Éxito!",
                    f"Contraseña encontrada: {password}\n\n"
                    f"Los archivos han sido extraídos a:\n{self.output_path}"
                )
            )
            return True
            
        except Exception as e:
            self.safe_log(f"❌ Error al probar la contraseña: {str(e)}")
            return False
            
        finally:
         
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                self.safe_log(f"⚠️ No se pudo eliminar el directorio temporal: {str(e)}")
    
    def brute_force_archive(self):
        
        try:
            self.running = True
            
            try:
                with open(self.dict_path, 'r', encoding='utf-8', errors='ignore') as f:
                    passwords = [line.strip() for line in f if line.strip()]
            except Exception as e:
                self.safe_log(f"❌ Error al leer el archivo de diccionario: {str(e)}")
                QMetaObject.invokeMethod(self, "cleanup_after_operation", Qt.QueuedConnection)
                return
                
            total = len(passwords)
            if total == 0:
                self.safe_log("❌ El archivo de diccionario está vacío")
                QMetaObject.invokeMethod(self, "cleanup_after_operation", Qt.QueuedConnection)
                return

            self.safe_log(f"🔍 Iniciando ataque de fuerza bruta con {total} contraseñas...")
            self.safe_log(f"📂 Archivo: {os.path.basename(self.archive_path)}")
            self.safe_log(f"📝 Diccionario: {os.path.basename(self.dict_path)}")
            
            QMetaObject.invokeMethod(self.progress_bar, "setMaximum", 
                                  Qt.QueuedConnection,
                                  Q_ARG(int, total))
            QMetaObject.invokeMethod(self.progress_bar, "setValue",
                                  Qt.QueuedConnection,
                                  Q_ARG(int, 0))
            
            start_time = time.time()
            password_found = False
            
            for i, password in enumerate(passwords, 1):
                if not hasattr(self, 'running') or not self.running:
                    self.safe_log("❌ Proceso detenido por el usuario")
                    break
                
                if i % 10 == 0 or i == total or i == 1:
                    elapsed = time.time() - start_time
                    speed = i / elapsed if elapsed > 0 else 0
                    progress_text = f"Probando... {i}/{total} | {speed:.1f} p/s | {elapsed:.1f}s"
                    
                    QMetaObject.invokeMethod(self.progress_bar, "setValue",
                                          Qt.QueuedConnection,
                                          Q_ARG(int, i))
                    QMetaObject.invokeMethod(self.progress_bar, "setFormat",
                                          Qt.QueuedConnection,
                                          Q_ARG(str, progress_text))
                
                if self.test_password(password):
                    password_found = True
                    elapsed = time.time() - start_time
                    self.safe_log(f"\n✅ ¡Contraseña encontrada en el intento {i} de {total}!")
                    self.safe_log(f"🔑 Contraseña: {password}")
                    self.safe_log(f"⏱️ Tiempo transcurrido: {elapsed:.1f} segundos")
                    
                    QMetaObject.invokeMethod(self, "show_success",
                                          Qt.QueuedConnection,
                                          Q_ARG(str, "¡Contraseña encontrada!"),
                                          Q_ARG(str, (
                                              f"Se encontró la contraseña en el intento {i} de {total}.\n\n"
                                              f"Contraseña: {password}\n\n"
                                              f"Los archivos han sido extraídos a:\n{self.output_path}"
                                          )))
                    break
            
            if not password_found and hasattr(self, 'running') and self.running:
                self.safe_log("❌ Contraseña no encontrada en el diccionario")
                QMetaObject.invokeMethod(self, "show_error",
                                      Qt.QueuedConnection,
                                      Q_ARG(str, "Error"),
                                      Q_ARG(str, "No se encontró la contraseña en el diccionario proporcionado."))
                
        except Exception as e:
            error_msg = f"❌ Error durante el ataque de fuerza bruta: {str(e)}"
            self.safe_log(error_msg)
            QMetaObject.invokeMethod(self, "show_error",
                                  Qt.QueuedConnection,
                                  Qt.Q_ARG(str, "Error"),
                                  Qt.Q_ARG(str, error_msg))
                                  
        finally:
           
            QMetaObject.invokeMethod(self, "cleanup_after_operation", 
                                  Qt.QueuedConnection)

    def test_password(self, password):
        try:
            ext = os.path.splitext(self.archive_path)[1].lower()
            temp_dir = os.path.join(self.output_path, "_temp_extraction")
                
            if os.path.exists(temp_dir):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            os.makedirs(temp_dir, exist_ok=True)
                
            self.safe_log("\n" + "="*50)
            self.safe_log(f"🔍 Probando contraseña: {password}")
                
            success, extracted_files = self.extract_with_retry(self.archive_path, password, temp_dir)
                
            if not success:
                return False
                
            self.safe_log(f"✅ ¡Contraseña correcta!: {password}")
            self.safe_log(f"📂 Archivos extraídos a: {self.output_path}")
                
            nested_archives = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext in ['.zip', '.rar', '.7z']:
                        nested_archives.append(os.path.join(root, file))
            
            if nested_archives:
                self.safe_log(f"🔍 Se encontraron {len(nested_archives)} archivos anidados")
                
                for nested_archive in nested_archives:
                    rel_path = os.path.relpath(nested_archive, temp_dir)
                    output_subdir = os.path.join(self.output_path, os.path.dirname(rel_path))
                    os.makedirs(output_subdir, exist_ok=True)
                    
                    self.safe_log(f"🔍 Procesando archivo anidado: {os.path.basename(nested_archive)}")
                    
                    nested_success, _ = self.extract_with_retry(
                        nested_archive, 
                        password, 
                        output_path=output_subdir,
                        is_nested=True
                    )
                    
                    if not nested_success:
                        self.safe_log(f"⚠️ No se pudo extraer el archivo anidado: {os.path.basename(nested_archive)}")
            
            self.safe_log("📂 Moviendo archivos a la ubicación final...")
            
            for item in os.listdir(temp_dir):
                src = os.path.join(temp_dir, item)
                dst = os.path.join(self.output_path, os.path.basename(item))
                
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        
                        for subitem in os.listdir(src):
                            try:
                                shutil.move(os.path.join(src, subitem), 
                                         os.path.join(dst, os.path.basename(subitem)))
                            except Exception as e:
                                self.safe_log(f"⚠️ No se pudo mover {subitem}: {str(e)}")
                    else:
                        
                        base, ext = os.path.splitext(item)
                        counter = 1
                        while os.path.exists(dst):
                            new_name = f"{base}_{counter}{ext}"
                            dst = os.path.join(self.output_path, new_name)
                            counter += 1
                        try:
                            shutil.move(src, dst)
                        except Exception as e:
                            self.safe_log(f"⚠️ No se pudo mover {item}: {str(e)}")
                else:
                    try:
                        shutil.move(src, dst)
                    except Exception as e:
                        self.safe_log(f"⚠️ No se pudo mover {item}: {str(e)}")
            
            self.safe_log("✅ ¡Extracción completada exitosamente!")
            self.safe_log("="*50 + "\n")
            
            QApplication.instance().postEvent(
                self, 
                SuccessEvent(
                    "¡Éxito!",
                    f"Contraseña encontrada: {password}\n\n"
                    f"Los archivos han sido extraídos a:\n{self.output_path}"
                )
            )
            return True
            
        except Exception as e:
            self.safe_log(f"❌ Error al probar la contraseña: {str(e)}")
            return False
            
        finally:
            
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                self.safe_log(f"⚠️ No se pudo eliminar el directorio temporal: {str(e)}")
    
    def show_success(self, title, message):
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: rgb(20, 20, 20);
                border: 1px solid lime;
                color: lime;
            }
            QLabel {
                color: lime;
                font-size: 12px;
            }
            QPushButton {
                background-color: rgba(40, 40, 40, 200);
                color: lime;
                border: 1px solid rgba(0, 255, 0, 80);
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 80px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(0, 255, 0, 120);
            }
        """)
        
        msg.move(
            self.x() + (self.width() - msg.width()) // 2,
            self.y() + (self.height() - msg.height()) // 2
        )
        
        msg.exec_()
    
    def event(self, event):
       
        if isinstance(event, SuccessEvent):
            self.show_success(event.title, event.message)
            return True
        return super().event(event)
        
    def show_error(self, title, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: rgb(20, 20, 20);
                border: 1px solid #ff5555;
            }
            QLabel {
                color: lime;
            }
            QPushButton {
                background-color: rgba(40, 40, 40, 200);
                color: lime;
                border: 1px solid rgba(0, 255, 0, 80);
                border-radius: 6px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(0, 255, 0, 120);
            }
        """)
        
        msg.exec_()

def main():
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        
        if not os.environ.get("QT_SCALE_FACTOR"):
            if hasattr(Qt, 'AA_EnableHighDpiScaling'):
                QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
                QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    except Exception as e:
        print(f"Warning: Could not set high DPI settings: {e}")
        app = QApplication(sys.argv)
    
    app.setApplicationName("THO BRUTEFORCE")
    app.setApplicationDisplayName("THO BRUTEFORCE")
    app.setApplicationVersion("1.0.0")
    app.setStyle("Fusion")
    
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)
    
    window = MainWindow()
    
    icon_path = os.path.join(script_dir, "assets", "icono.png")
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))
    
    
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()