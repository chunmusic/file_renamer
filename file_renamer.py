import sys
import os
import ctypes
from pathlib import Path

# ------------------------------ PySide6 imports ------------------------------
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFileDialog,
    QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QStyle,
    QToolButton, QFrame, QSizePolicy, QStackedWidget
)
from PySide6.QtGui import QIcon, QPalette, QAction
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize


# ------------------------------ Utils ---------------------------------------
def resource_path(relative_path: str) -> str:
    """Return absolute path to resource (handles PyInstaller onefile)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


# ------------------------------ Main Window ---------------------------------
class FileRenamerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Renamer")
        self.resize(800, 600)
        self.setWindowFlags(Qt.Window)
        self.setFixedSize(self.size())

        # App/window icon (taskbar appearance)
        try:
            icon = QIcon(resource_path("assets/app.ico"))
            self.setWindowIcon(icon)
        except Exception:
            pass

        # ----- ROOT LAYOUT: header (hamburger) + body (sidebar + content) -----
        root = QWidget()
        self.setCentralWidget(root)
        root_v = QVBoxLayout(root)
        root_v.setContentsMargins(0, 0, 0, 0)
        root_v.setSpacing(0)

        # ---------------- Header bar with hamburger button --------------------
        self.header = QFrame(objectName="HeaderBar")
        self.header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.header.setFixedHeight(48)
        header_h = QHBoxLayout(self.header)
        header_h.setContentsMargins(12, 6, 12, 6)
        header_h.setSpacing(8)

        # Hamburger: text-based ☰ for consistent cross-platform look
        self.hamburger = QToolButton(objectName="Hamburger")
        self.hamburger.setText("☰")
        self.hamburger.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hamburger.setAutoRaise(True)
        self.hamburger.setFixedSize(QSize(36, 36))
        self.hamburger.clicked.connect(self.toggle_sidebar)

        self.header_title = QLabel("File Renamer", objectName="HeaderTitle")

        header_h.addWidget(self.hamburger)
        header_h.addSpacing(4)
        header_h.addWidget(self.header_title)
        header_h.addStretch(1)

        root_v.addWidget(self.header)

        # ---------------- Body: sidebar + main content -----------------------
        body = QFrame(objectName="Body")
        body_h = QHBoxLayout(body)
        body_h.setContentsMargins(0, 0, 0, 0)
        body_h.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame(objectName="Sidebar")
        self.sidebar.setFixedWidth(220)  # expanded width
        self.sidebar_min_w = 0
        self.sidebar_max_w = 220
        self.sidebar.setMinimumWidth(self.sidebar_min_w)
        self.sidebar.setMaximumWidth(self.sidebar_max_w)
        side_v = QVBoxLayout(self.sidebar)
        side_v.setContentsMargins(10, 10, 10, 10)
        side_v.setSpacing(8)

        self.btn_nav_rename = QPushButton("Rename Files", objectName="SideButton")
        self.btn_nav_rename.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon))
        self.btn_nav_rename.setCheckable(True)
        self.btn_nav_rename.setChecked(True)

        self.btn_nav_settings = QPushButton("Settings", objectName="SideButton")
        # Use a gear-like standard icon (appearance varies by platform/theme)
        self.btn_nav_settings.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        self.btn_nav_settings.setCheckable(True)
        self.btn_nav_settings.setChecked(False)

        # Navigation
        self.btn_nav_rename.clicked.connect(self.focus_rename_view)
        self.btn_nav_settings.clicked.connect(self.focus_settings_view)

        side_v.addWidget(self.btn_nav_rename)
        side_v.addWidget(self.btn_nav_settings)
        side_v.addStretch(1)

        # ---------------- Content: stacked pages -----------------------------
        self.content = QFrame(objectName="ContentArea")
        content_v = QVBoxLayout(self.content)
        content_v.setContentsMargins(20, 20, 20, 20)
        content_v.setSpacing(12)

        self.stack = QStackedWidget(self.content)
        content_v.addWidget(self.stack)

        # ---------------- Page 0: Rename view ---------------------------------
        self.rename_page = QWidget()
        rename_v = QVBoxLayout(self.rename_page)
        rename_v.setContentsMargins(0, 0, 0, 0)
        rename_v.setSpacing(12)

        self.folder_label = QLabel("Folder Path:", objectName="StrongBodyLabel")

        # Folder input and browse button in the same row
        row1 = QHBoxLayout()
        self.folder_input = QLineEdit(placeholderText="Select or paste a folder path")
        self.folder_input.setObjectName("LineEdit")
        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("PrimaryButton")
        self.browse_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        self.browse_button.clicked.connect(self.browse_folder)
        row1.addWidget(self.folder_input, 1)
        row1.addWidget(self.browse_button, 0)

        rename_v.addWidget(self.folder_label)
        rename_v.addLayout(row1)

        self.prefix_label = QLabel("File Prefix:", objectName="StrongBodyLabel")
        self.prefix_input = QLineEdit()
        self.prefix_input.setObjectName("LineEdit")
        self.prefix_input.setText("file")
        rename_v.addWidget(self.prefix_label)
        rename_v.addWidget(self.prefix_input)

        self.start_num_label = QLabel("Start Number:", objectName="StrongBodyLabel")
        self.start_num_input = QLineEdit()
        self.start_num_input.setObjectName("LineEdit")
        self.start_num_input.setText("1")
        self.start_num_input.setMaxLength(12)
        rename_v.addWidget(self.start_num_label)
        rename_v.addWidget(self.start_num_input)

        self.rename_button = QPushButton("Rename Files")
        self.rename_button.setObjectName("PrimaryButton")
        self.rename_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        self.rename_button.clicked.connect(self.rename_files)
        rename_v.addWidget(self.rename_button)

        self.status_label = QLabel("Ready", objectName="StrongBodyLabel")
        rename_v.addWidget(self.status_label)

        # ---------------- Page 1: Settings view ------------------------------
        self.settings_page = QWidget()
        settings_v = QVBoxLayout(self.settings_page)
        settings_v.setContentsMargins(0, 0, 0, 0)
        settings_v.addStretch(1)
        settings_label = QLabel("Under maintenance")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_label.setObjectName("StrongBodyLabel")
        settings_v.addWidget(settings_label)
        settings_v.addStretch(1)

        self.stack.addWidget(self.rename_page)
        self.stack.addWidget(self.settings_page)
        self.stack.setCurrentIndex(0)

        # Assemble body
        body_h.addWidget(self.sidebar)
        body_h.addWidget(self.content)
        root_v.addWidget(body, 1)

        # Sidebar animation
        self._sidebar_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self._sidebar_anim.setDuration(180)
        self._sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Apply stylesheet
        self.apply_stylesheet()

    # ------------------------------ Slots -----------------------------------
    def toggle_sidebar(self):
        current = self.sidebar.maximumWidth()
        target = self.sidebar_max_w if current == self.sidebar_min_w else self.sidebar_min_w
        self._sidebar_anim.stop()
        self._sidebar_anim.setStartValue(current)
        self._sidebar_anim.setEndValue(target)
        self._sidebar_anim.start()

    def focus_rename_view(self):
        self.btn_nav_rename.setChecked(True)
        self.btn_nav_settings.setChecked(False)
        self.stack.setCurrentIndex(0)

    def focus_settings_view(self):
        self.btn_nav_rename.setChecked(False)
        self.btn_nav_settings.setChecked(True)
        self.stack.setCurrentIndex(1)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def rename_files(self):
        folder = self.folder_input.text().strip()
        prefix = self.prefix_input.text().strip()
        start_num_text = self.start_num_input.text().strip()

        if not folder or not os.path.isdir(folder):
            self.message_box("Error", "Please select a valid folder!", QMessageBox.Icon.Critical)
            return

        if not prefix:
            self.message_box("Error", "Prefix cannot be empty!", QMessageBox.Icon.Critical)
            return

        try:
            if start_num_text == "":
                raise ValueError
            start_num = int(start_num_text)
            if start_num < 0:
                raise ValueError("Start number must be non-negative!")
            padding_length = len(start_num_text) if start_num_text.startswith("0") else 1
        except Exception:
            self.message_box("Error", "Start number must be a valid non-negative integer!", QMessageBox.Icon.Critical)
            return

        try:
            path = Path(folder)
            files = [f for f in path.iterdir() if f.is_file()]
            if not files:
                self.message_box("Warning", "No files found in the selected folder!", QMessageBox.Icon.Warning)
                return

            files.sort(key=lambda p: p.name.lower())

            for i, file in enumerate(files, start=start_num):
                extension = file.suffix
                padded_num = f"{i:0{padding_length}d}" if padding_length > 1 else str(i)
                new_name = f"{prefix}{padded_num}{extension}"
                new_path = path / new_name

                if new_path.exists():
                    raise FileExistsError(f"Target filename already exists: {new_name}")

                file.rename(new_path)

            self.message_box("Success", "Files renamed successfully!", QMessageBox.Icon.Information)
            self.status_label.setText("Files renamed successfully!")
        except Exception as e:
            self.message_box("Error", f"Failed to rename files: {e}", QMessageBox.Icon.Critical)
            self.status_label.setText(f"Error: {e}")

    # ------------------------------ Helpers ---------------------------------
    def message_box(self, title: str, text: str, icon: QMessageBox.Icon):
        box = QMessageBox(self)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setWindowIcon(self.windowIcon())
        box.exec()

    def apply_stylesheet(self):
        TEAL       = "#00a19a"
        TEAL_HOVER = "#0aaea7"
        TEAL_PRESS = "#08978f"
        TEXT       = "#1f2937"       # slate-800
        BORDER     = "#d9dfe6"       # light gray border
        INPUT_BG   = "#ffffff"
        HEADER_BG  = "rgba(255,255,255,0.82)"

        self.setStyleSheet(f"""
            /* ---- App background (soft gradient) ---- */
            QFrame#Body, QFrame#ContentArea {{
                background: qlineargradient(
                    x1:0 y1:0, x2:1 y2:1,
                    stop:0  #f7f0eb,
                    stop:0.5 #f9fbff,
                    stop:1  #eef8f5
                );
            }}

            /* ---- Header ---- */
            QFrame#HeaderBar {{
                background: {HEADER_BG};
                border-bottom: 1px solid {BORDER};
            }}
            QLabel#HeaderTitle {{
                font-weight: 600;
                font-size: 16px;
                color: {TEXT};
            }}
            QToolButton#Hamburger {{
                border-radius: 10px;
                padding: 6px;
                font-size: 18px;
                font-weight: bold;
                color: {TEXT};
                background: transparent;
            }}
            QToolButton#Hamburger:hover {{
                background: rgba(0,0,0,0.06);
            }}

            /* ---- Sidebar ---- */
            QFrame#Sidebar {{
                background: rgba(255,255,255,0.65);
                border-right: 1px solid {BORDER};
            }}
            QPushButton#SideButton {{
                text-align: left;
                padding: 10px 12px;
                border-radius: 10px;
                border: 1px solid transparent;
                font-size: 14px;
                color: {TEXT};
            }}
            QPushButton#SideButton:hover {{
                background: rgba(0,0,0,0.05);
            }}
            QPushButton#SideButton:checked {{
                background: rgba(0,161,154,0.18);
                border: 1px solid rgba(0,161,154,0.45);
            }}

            /* ---- Content controls ---- */
            QLabel#StrongBodyLabel {{
                font-weight: 600;
                font-size: 14px;
                color: {TEXT};
            }}
            QLineEdit#LineEdit {{
                font-size: 14px;
                padding: 10px 12px;
                border-radius: 10px;
                border: 1px solid {BORDER};
                background: {INPUT_BG};
                color: {TEXT};
            }}
            QLineEdit#LineEdit:focus {{
                border: 2px solid {TEAL};
                outline: none;
            }}

            /* ---- Buttons ---- */
            QPushButton {{
                font-size: 14px;
                padding: 10px 16px;
                border-radius: 10px;
                border: 1px solid {BORDER};
                background: rgba(255,255,255,0.85);
                color: {TEXT};
            }}
            QPushButton:hover {{
                background: rgba(0,0,0,0.04);
            }}

            /* Primary buttons (Browse / Rename) – teal like screenshot */
            QPushButton#PrimaryButton {{
                background: {TEAL};
                color: white;
                border: none;
            }}
            QPushButton#PrimaryButton:hover {{
                background: {TEAL_HOVER};
            }}
            QPushButton#PrimaryButton:pressed {{
                background: {TEAL_PRESS};
            }}
        """)


# ---------------------------------- Main ------------------------------------
if __name__ == "__main__":
    # Assign a unique AppUserModelID (helps Windows show the correct taskbar icon)
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.chunzps.filerenamer")
    except Exception:
        pass

    app = QApplication(sys.argv)

    # Set app-level icon
    try:
        app.setWindowIcon(QIcon(resource_path("assets/app.ico")))
    except Exception:
        pass

    win = FileRenamerApp()
    win.show()
    sys.exit(app.exec())
