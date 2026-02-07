import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QPushButton, QTextEdit, QFrame,
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QSlider
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QFont


class VideoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialize the UI matching the Figma design"""
        self.setWindowTitle("Video Editor")
        self.setGeometry(100, 100, 1400, 800)
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout (vertical: toolbar + content)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # TOP TOOLBAR
        toolbar = self.createToolbar()
        main_layout.addWidget(toolbar)
        
        # MAIN CONTENT AREA (horizontal splitter)
        content_splitter = self.createContentArea()
        main_layout.addWidget(content_splitter, 1)
        
        main_widget.setLayout(main_layout)

    def createToolbar(self):
        """Create the top toolbar"""
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("background-color: #2a2a2a; border-bottom: 1px solid #444;")
        toolbar_frame.setMaximumHeight(50)
        
        layout = QHBoxLayout(toolbar_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Logo/Title
        title = QLabel("Video Editor")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Menu buttons
        for txt in ["File", "Edit", "View", "Help"]:
            btn = QPushButton(txt)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
            """)
            layout.addWidget(btn)
        
        layout.addStretch()
        return toolbar_frame

    def createContentArea(self):
        """Create main content area with left, center, and right panels"""
        # Main horizontal splitter for left|center|right
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANEL - Recording Panel (20%)
        left_panel = self.createRecordingPanel()
        main_splitter.addWidget(left_panel)
        
        # CENTER PANEL - Preview + Timeline (60%)
        center_panel = self.createCenterPanel()
        main_splitter.addWidget(center_panel)
        
        # RIGHT PANEL - Properties Panel (20%)
        right_panel = self.createPropertiesPanel()
        main_splitter.addWidget(right_panel)
        
        # Set initial sizes (20%, 60%, 20%)
        main_splitter.setSizes([280, 840, 280])
        
        return main_splitter

    def createRecordingPanel(self):
        """Left sidebar - Recording controls"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #333;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Recording")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Record Screen Button
        record_screen_btn = QPushButton("🎥 Record Screen")
        record_screen_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        layout.addWidget(record_screen_btn)
        
        # Record Camera Button
        record_camera_btn = QPushButton("📹 Record Camera")
        record_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c3aed;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        layout.addWidget(record_camera_btn)
        
        # Separator
        sep = QFrame()
        sep.setStyleSheet("background-color: #333;")
        sep.setMaximumHeight(1)
        layout.addWidget(sep)
        
        # Media Library Section
        media_title = QLabel("Media Library")
        media_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        media_title.setStyleSheet("color: white;")
        layout.addWidget(media_title)
        
        # Dummy media items
        for i in range(3):
            media_item = QLabel(f"Media {i+1}")
            media_item.setStyleSheet("color: #999; padding: 5px; background-color: #2a2a2a; border-radius: 3px;")
            layout.addWidget(media_item)
        
        layout.addStretch()
        return frame

    def createCenterPanel(self):
        """Center area - Preview + Timeline"""
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # PREVIEW WINDOW (70%)
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background-color: #0a0a0a; border: 1px solid #333;")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview content
        preview_label = QLabel("Preview Window")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_label.setFont(QFont("Arial", 14))
        preview_label.setStyleSheet("color: #666;")
        preview_label.setMinimumHeight(300)
        preview_layout.addWidget(preview_label)
        
        # Playback controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #333;")
        controls_frame.setMaximumHeight(50)
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(10, 5, 10, 5)
        
        play_btn = QPushButton("▶")
        play_btn.setMaximumWidth(40)
        controls_layout.addWidget(play_btn)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #333;
                height: 5px;
            }
            QSlider::handle:horizontal {
                background: #2563eb;
                width: 12px;
                margin: -3px 0;
                border-radius: 6px;
            }
        """)
        controls_layout.addWidget(slider)
        
        time_label = QLabel("0:00 / 0:00")
        time_label.setStyleSheet("color: white; min-width: 100px;")
        controls_layout.addWidget(time_label)
        
        preview_layout.addWidget(controls_frame)
        center_splitter.addWidget(preview_frame)
        
        # TIMELINE (30%)
        timeline_frame = QFrame()
        timeline_frame.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #333;")
        timeline_layout = QVBoxLayout(timeline_frame)
        timeline_layout.setContentsMargins(10, 10, 10, 10)
        
        timeline_title = QLabel("Timeline")
        timeline_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        timeline_title.setStyleSheet("color: white;")
        timeline_layout.addWidget(timeline_title)
        
        # Timeline tracks placeholder
        tracks_label = QLabel("Video Tracks will appear here")
        tracks_label.setStyleSheet("color: #666; padding: 20px;")
        tracks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timeline_layout.addWidget(tracks_label)
        
        center_splitter.addWidget(timeline_frame)
        
        # Set sizes (70% preview, 30% timeline)
        center_splitter.setSizes([490, 210])
        
        return center_splitter

    def createPropertiesPanel(self):
        """Right sidebar - Properties"""
        frame = QFrame()
        frame.setStyleSheet("background-color: #1e1e1e; border-left: 1px solid #333;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Properties")
        title.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        # Resolution
        res_group = QGroupBox("Resolution")
        res_group.setStyleSheet("color: white; border: 1px solid #333; padding: 10px;")
        res_layout = QVBoxLayout()
        
        res_combo = QComboBox()
        res_combo.addItems(["1920x1080", "1280x720", "640x480"])
        res_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #333;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        res_layout.addWidget(res_combo)
        res_group.setLayout(res_layout)
        layout.addWidget(res_group)
        
        # Frame Rate
        fps_group = QGroupBox("Frame Rate")
        fps_group.setStyleSheet("color: white; border: 1px solid #333; padding: 10px;")
        fps_layout = QVBoxLayout()
        
        fps_spin = QSpinBox()
        fps_spin.setValue(30)
        fps_spin.setMaximum(120)
        fps_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #333;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        fps_layout.addWidget(fps_spin)
        fps_group.setLayout(fps_layout)
        layout.addWidget(fps_group)
        
        # Effects
        effects_group = QGroupBox("Effects")
        effects_group.setStyleSheet("color: white; border: 1px solid #333; padding: 10px;")
        effects_layout = QVBoxLayout()
        
        for effect in ["Blur", "Brightness", "Contrast"]:
            check = QCheckBox(effect)
            check.setStyleSheet("color: white;")
            effects_layout.addWidget(check)
        
        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)
        
        layout.addStretch()
        return frame


def main():
    app = QApplication(sys.argv)
    
    # Apply dark theme
    app.setStyle("Fusion")
    
    editor = VideoEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
