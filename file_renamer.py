import sys
import os
import ctypes
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLabel
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from qfluentwidgets import (
    setTheme,
    Theme,
    FluentWindow,
    MessageBox,
    FluentIcon,
    NavigationItemPosition,
    PrimaryPushButton,
    LineEdit,
    BodyLabel,
    StrongBodyLabel
)


def resource_path(relative_path: str) -> str:
    """Return absolute path to resource (handles PyInstaller onefile)."""
    if hasattr(sys, "_MEIPASS"):  # PyInstaller temp dir
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


class FileRenamerApp(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Renamer")
        self.resize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(self.size())

        # ---- Set app/window icon (this controls taskbar appearance) ----
        icon = QIcon(resource_path("assets/app.ico"))
        self.setWindowIcon(icon)

        # Create main widget and layout
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainInterface")
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Folder input
        self.folder_label = StrongBodyLabel("Folder Path:")
        self.folder_input = LineEdit()
        self.browse_button = PrimaryPushButton("Browse", self, FluentIcon.FOLDER)
        self.browse_button.clicked.connect(self.browse_folder)
        self.layout.addWidget(self.folder_label)
        self.layout.addWidget(self.folder_input)
        self.layout.addWidget(self.browse_button)

        # Prefix input
        self.prefix_label = StrongBodyLabel("File Prefix:")
        self.prefix_input = LineEdit()
        self.prefix_input.setText("file")
        self.layout.addWidget(self.prefix_label)
        self.layout.addWidget(self.prefix_input)

        # Start number input
        self.start_num_label = StrongBodyLabel("Start Number:")
        self.start_num_input = LineEdit()
        self.start_num_input.setText("1")
        self.layout.addWidget(self.start_num_label)
        self.layout.addWidget(self.start_num_input)

        # Rename button
        self.rename_button = PrimaryPushButton("Rename Files", self, FluentIcon.SEND)
        self.rename_button.clicked.connect(self.rename_files)
        self.layout.addWidget(self.rename_button)

        # Status label
        self.status_label = StrongBodyLabel("Ready")
        self.layout.addWidget(self.status_label)

        # Add main widget as a sub-interface
        self.addSubInterface(
            self.main_widget,
            FluentIcon.DOCUMENT,
            "Rename Files",
            position=NavigationItemPosition.TOP,
        )

        # Theme setup
        setTheme(Theme.AUTO)
        # self.setMicaEffectEnabled(True)  # optional for Windows mica effect

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def rename_files(self):
        folder = self.folder_input.text()
        prefix = self.prefix_input.text()
        start_num = self.start_num_input.text()

        if not folder or not os.path.isdir(folder):
            MessageBox("Error", "Please select a valid folder!", self).exec()
            return

        if not prefix:
            MessageBox("Error", "Prefix cannot be empty!", self).exec()
            return

        try:
            start_num = int(start_num)
            if start_num < 0:
                raise ValueError("Start number must be non-negative!")
            input_num = self.start_num_input.text().lstrip('0') or '0'
            padding_length = len(self.start_num_input.text()) if self.start_num_input.text().startswith('0') else 1
        except ValueError:
            MessageBox("Error", "Start number must be a valid integer!", self).exec()
            return

        try:
            path = Path(folder)
            files = [f for f in path.iterdir() if f.is_file()]
            if not files:
                MessageBox("Warning", "No files found in the selected folder!", self).exec()
                return

            for i, file in enumerate(files, start=start_num):
                extension = file.suffix
                padded_num = f"{i:0{padding_length}d}" if padding_length > 1 else str(i)
                new_name = f"{prefix}{padded_num}{extension}"
                new_path = path / new_name
                file.rename(new_path)

            MessageBox("Success", "Files renamed successfully!", self).exec()
            self.status_label.setText("Files renamed successfully!")
        except Exception as e:
            MessageBox("Error", f"Failed to rename files: {str(e)}", self).exec()
            self.status_label.setText(f"Error: {str(e)}")


if __name__ == "__main__":
    # ---- Assign a unique AppUserModelID (required for taskbar icon) ----
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.chunzps.filerenamer")
    except Exception:
        pass

    app = QApplication(sys.argv)

    # ---- Set app-level icon (helps Windows show the right taskbar icon) ----
    app.setWindowIcon(QIcon(resource_path("assets/app.ico")))

    window = FileRenamerApp()
    window.show()
    app.exec()
