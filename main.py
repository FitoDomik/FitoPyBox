import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QCheckBox, QFileDialog, QTextEdit, QComboBox,
                            QDialog, QTabWidget, QScrollArea, QFrame,
                            QMessageBox, QMenuBar, QMenu, QStatusBar, QSpacerItem,
                            QSizePolicy, QStackedWidget)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor
import subprocess
import json
from datetime import datetime
def find_requirements_file(python_file):
    """Поиск файла requirements.txt в директории Python файла"""
    directory = os.path.dirname(python_file)
    requirements_file = os.path.join(directory, "requirements.txt")
    if os.path.exists(requirements_file):
        return requirements_file
    return None
def extract_imports(python_file):
    """Извлечение импортов из Python файла"""
    imports = set()
    try:
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()
        import_pattern = r'^(?:from\s+(\w+)(?:\.\w+)*\s+import|import\s+(\w+))'
        matches = re.finditer(import_pattern, content, re.MULTILINE)
        for match in matches:
            module = match.group(1) or match.group(2)
            if module and not module.startswith('_'):
                imports.add(module)
        req_file = find_requirements_file(python_file)
        if req_file:
            with open(req_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        imports.add(package)
    except Exception as e:
        print(f"Ошибка при извлечении импортов: {e}")
    return list(imports)
class IconPreviewDialog(QDialog):
    def __init__(self, icon_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Предпросмотр иконки")
        self.setMinimumSize(300, 300)
        layout = QVBoxLayout(self)
        sizes = [16, 32, 48, 64, 128, 256]
        for size in sizes:
            icon = QIcon(icon_path)
            pixmap = icon.pixmap(QSize(size, size))
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
class BuildHistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("История сборок")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout(self)
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Очистить историю")
        clear_button.clicked.connect(self.clear_history)
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        self.load_history()
    def load_history(self):
        try:
            with open("build_history.json", "r") as f:
                history = json.load(f)
                text = ""
                for entry in reversed(history):
                    text += f"[{entry['timestamp']}]\n"
                    text += f"Файл: {entry['file']}\n"
                    text += f"Команда: {entry['command']}\n"
                    text += "-" * 50 + "\n"
                self.history_text.setText(text)
        except FileNotFoundError:
            self.history_text.setText("История пуста")
    def clear_history(self):
        reply = QMessageBox.question(self, "Подтверждение", 
                                   "Вы уверены, что хотите очистить историю?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with open("build_history.json", "w") as f:
                json.dump([], f)
            self.history_text.clear()
class FitoPyBox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FitoPyBox")
        self.setMinimumSize(1000, 800)
        self.setup_styles() 
        self.setup_ui()
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #3d3d3d;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
            }
            QTabBar::tab:hover {
                background-color: #4d4d4d;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0a3d91;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                font-size: 14px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border: 2px solid #0d47a1;
            }
            QLineEdit:disabled {
                background-color: #1e1e1e;
                color: #666666;
            }
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3d3d3d;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0d47a1;
                border-color: #0d47a1;
            }
            QCheckBox::indicator:hover {
                border-color: #0d47a1;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4d4d4d;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMessageBox {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
        """)
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.create_menu()
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        page1 = QWidget()
        page1_layout = QVBoxLayout(page1)
        page1_layout.setSpacing(15)
        file_group = QFrame()
        file_group.setFrameStyle(QFrame.Shape.StyledPanel)
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(10)
        file_label = QLabel("Python файл для конвертации:")
        file_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        file_layout.addWidget(file_label)
        file_input_layout = QHBoxLayout()
        file_input_layout.setSpacing(10)
        self.file_path = QLineEdit()
        self.file_path.setPlaceholderText("Выберите Python файл...")
        browse_button = QPushButton("Обзор")
        browse_button.clicked.connect(self.browse_file)
        auto_deps_button = QPushButton("Найти зависимости")
        auto_deps_button.clicked.connect(self.auto_find_dependencies)
        file_input_layout.addWidget(self.file_path, 1)
        file_input_layout.addWidget(browse_button)
        file_input_layout.addWidget(auto_deps_button)
        file_layout.addLayout(file_input_layout)
        page1_layout.addWidget(file_group)
        page1_layout.addStretch(1)
        nav_layout1 = QHBoxLayout()
        self.next_button1 = QPushButton("Далее")
        self.next_button1.clicked.connect(self.go_next_page)
        nav_layout1.addStretch(1)
        nav_layout1.addWidget(self.next_button1)
        page1_layout.addLayout(nav_layout1)
        self.stacked_widget.addWidget(page1)
        page2 = QWidget()
        page2_layout = QVBoxLayout(page2)
        page2_layout.setSpacing(15)
        build_group = QFrame()
        build_group.setFrameStyle(QFrame.Shape.StyledPanel)
        build_layout = QVBoxLayout(build_group)
        build_layout.setSpacing(10)
        build_label = QLabel("Настройки сборки:")
        build_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        build_layout.addWidget(build_label)
        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)
        name_layout.addWidget(QLabel("Название .exe:"))
        self.exe_name = QLineEdit()
        name_layout.addWidget(self.exe_name, 1)
        build_layout.addLayout(name_layout)
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)
        self.one_file = QCheckBox("Создать один файл")
        self.no_console = QCheckBox("Запуск без консоли")
        self.one_file.setChecked(True)
        options_layout.addWidget(self.one_file)
        options_layout.addWidget(self.no_console)
        build_layout.addLayout(options_layout)
        icon_layout = QHBoxLayout()
        icon_layout.setSpacing(10)
        self.icon_path = QLineEdit()
        self.icon_path.setPlaceholderText("Путь к иконке (.ico)...")
        icon_button = QPushButton("Выбрать иконку")
        icon_button.clicked.connect(self.browse_icon)
        preview_button = QPushButton("Предпросмотр")
        preview_button.clicked.connect(self.preview_icon)
        icon_layout.addWidget(self.icon_path, 1)
        icon_layout.addWidget(icon_button)
        icon_layout.addWidget(preview_button)
        build_layout.addLayout(icon_layout)
        page2_layout.addWidget(build_group)
        page2_layout.addStretch(1)
        nav_layout2 = QHBoxLayout()
        self.back_button2 = QPushButton("Назад")
        self.back_button2.clicked.connect(self.go_previous_page)
        self.next_button2 = QPushButton("Далее")
        self.next_button2.clicked.connect(self.go_next_page)
        nav_layout2.addWidget(self.back_button2)
        nav_layout2.addStretch(1)
        nav_layout2.addWidget(self.next_button2)
        page2_layout.addLayout(nav_layout2)
        self.stacked_widget.addWidget(page2)
        page3 = QWidget()
        page3_layout = QVBoxLayout(page3)
        page3_layout.setSpacing(15)
        advanced_group = QFrame()
        advanced_group.setFrameStyle(QFrame.Shape.StyledPanel)
        advanced_layout = QVBoxLayout(advanced_group)
        advanced_layout.setSpacing(10)
        advanced_label = QLabel("Дополнительные настройки:")
        advanced_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        advanced_layout.addWidget(advanced_label)
        imports_layout = QVBoxLayout()
        imports_layout.setSpacing(5)
        imports_layout.addWidget(QLabel("Скрытые импорты (через запятую):"))
        self.hidden_imports = QLineEdit()
        imports_layout.addWidget(self.hidden_imports)
        advanced_layout.addLayout(imports_layout)
        files_layout = QHBoxLayout()
        files_layout.setSpacing(10)
        self.additional_files = QLineEdit()
        self.additional_files.setPlaceholderText("Пути к доп. файлам/папкам (через ';'). Например: data.json;images/")
        files_button = QPushButton("Добавить файлы")
        files_button.clicked.connect(self.browse_additional_files)
        files_layout.addWidget(self.additional_files, 1)
        files_layout.addWidget(files_button)
        advanced_layout.addLayout(files_layout)
        resource_note_label = QLabel(
            "<p><b>Примечание:</b> Для доступа к этим файлам в вашем скрипте используйте <code>sys._MEIPASS</code>.</p>" +
            "<p>Пример: <code>os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), 'ваш_файл.ext')</code></p>"
        )
        resource_note_label.setStyleSheet("font-size: 11px; color: #aaaaaa;")
        resource_note_label.setWordWrap(True)
        advanced_layout.addWidget(resource_note_label)
        page3_layout.addWidget(advanced_group)
        page3_layout.addStretch(1)
        nav_layout3 = QHBoxLayout()
        self.back_button3 = QPushButton("Назад")
        self.back_button3.clicked.connect(self.go_previous_page)
        self.next_button3 = QPushButton("Далее")
        self.next_button3.clicked.connect(self.go_next_page)
        nav_layout3.addWidget(self.back_button3)
        nav_layout3.addStretch(1)
        nav_layout3.addWidget(self.next_button3)
        page3_layout.addLayout(nav_layout3)
        self.stacked_widget.addWidget(page3)
        page4 = QWidget()
        page4_layout = QVBoxLayout(page4)
        page4_layout.setSpacing(15)
        preview_group = QFrame()
        preview_group.setFrameStyle(QFrame.Shape.StyledPanel)
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(10)
        preview_label = QLabel("Предпросмотр команды:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        preview_layout.addWidget(preview_label)
        self.command_preview = QTextEdit()
        self.command_preview.setReadOnly(True)
        preview_layout.addWidget(self.command_preview, 1)
        page4_layout.addWidget(preview_group)
        page4_layout.addStretch(1)
        self.nav_layout4 = QHBoxLayout()
        self.back_button4 = QPushButton("Назад")
        self.back_button4.clicked.connect(self.go_previous_page)
        self.create_button = QPushButton("Создать .exe")
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-size: 16px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.create_button.clicked.connect(self.create_exe)
        self.open_folder_button = QPushButton("Открыть папку")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.run_exe_button = QPushButton("Запустить .exe")
        self.run_exe_button.clicked.connect(self.run_created_exe)
        self.new_build_button = QPushButton("Новая сборка")
        self.new_build_button.clicked.connect(self.start_new_build)
        self.nav_layout4.addWidget(self.back_button4)
        self.nav_layout4.addStretch(1)
        self.nav_layout4.addWidget(self.create_button)
        self.nav_layout4.addWidget(self.open_folder_button)
        self.nav_layout4.addWidget(self.run_exe_button)
        self.nav_layout4.addWidget(self.new_build_button)
        page4_layout.addLayout(self.nav_layout4)
        self.stacked_widget.addWidget(page4)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готов к работе")
        self.load_history()
        self.update_command_preview()
        self.update_navigation_buttons()
        self.show_result_buttons(False)
    def show_result_buttons(self, visible):
        """Показывает или скрывает кнопки после сборки"""
        self.back_button4.setVisible(not visible)
        self.create_button.setVisible(not visible)
        self.open_folder_button.setVisible(visible)
        self.run_exe_button.setVisible(visible)
        self.new_build_button.setVisible(visible)
    def go_next_page(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(current_index + 1)
            if self.stacked_widget.currentIndex() == self.stacked_widget.count() - 1:
                self.update_command_preview() 
                self.show_result_buttons(False) 
            self.update_navigation_buttons()
    def go_previous_page(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)
            self.update_navigation_buttons()
            if current_index == self.stacked_widget.count() - 1:
                self.show_result_buttons(False)
    def update_navigation_buttons(self):
        current_index = self.stacked_widget.currentIndex()
        total_pages = self.stacked_widget.count()
        self.next_button1.setVisible(False)
        self.back_button2.setVisible(False)
        self.next_button2.setVisible(False)
        self.back_button3.setVisible(False)
        self.next_button3.setVisible(False)
        if current_index == 0:
            self.next_button1.setVisible(True)
        elif current_index == 1:
            self.back_button2.setVisible(True)
            self.next_button2.setVisible(True)
        elif current_index == 2:
            self.back_button3.setVisible(True)
            self.next_button3.setVisible(True)
    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)
        history_menu = menubar.addMenu("История")
        view_history_action = history_menu.addAction("Просмотр истории")
        view_history_action.triggered.connect(self.show_history)
        clear_history_action = history_menu.addAction("Очистить историю")
        clear_history_action.triggered.connect(self.clear_history)
    def show_history(self):
        dialog = BuildHistoryDialog(self)
        dialog.exec()
    def clear_history(self):
        reply = QMessageBox.question(self, "Подтверждение",
                                   "Вы уверены, что хотите очистить историю?",
                                   QMessageBox.StandardButton.Yes |
                                   QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with open("build_history.json", "w") as f:
                json.dump([], f)
            self.statusBar.showMessage("История очищена")
    def preview_icon(self):
        if not self.icon_path.text():
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите иконку")
            return
        dialog = IconPreviewDialog(self.icon_path.text(), self)
        dialog.exec()
    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите Python файл", "", "Python Files (*.py)")
        if file_name:
            self.file_path.setText(file_name)
            if not self.exe_name.text():
                self.exe_name.setText(os.path.splitext(os.path.basename(file_name))[0])
            self.statusBar.showMessage(f"Выбран файл: {file_name}")
    def browse_icon(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите иконку", "", "Icon Files (*.ico)")
        if file_name:
            self.icon_path.setText(file_name)
            self.statusBar.showMessage(f"Выбрана иконка: {file_name}")
    def browse_additional_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите дополнительные файлы")
        if files:
            self.additional_files.setText(";".join(files))
            self.statusBar.showMessage(f"Добавлено файлов: {len(files)}")
    def update_command_preview(self):
        command = ["pyinstaller"]
        if self.one_file.isChecked():
            command.append("--onefile")
        if self.no_console.isChecked():
            command.append("--noconsole")
        if self.icon_path.text():
            command.extend(["--icon", self.icon_path.text()])
        if self.hidden_imports.text():
            imports = [imp.strip() for imp in self.hidden_imports.text().split(",") if imp.strip()]
            for imp in imports:
                command.extend(["--hidden-import", imp])
        if self.additional_files.text():
            files = [f.strip() for f in self.additional_files.text().split(";") if f.strip()]
            for file in files:
                command.append(f"--add-data={file}{os.pathsep}.")
        if self.file_path.text():
            command.append(self.file_path.text())
        self.command_preview.setText(" ".join(command))
    def create_exe(self):
        if not self.file_path.text():
            QMessageBox.warning(self, "Предупреждение", "Выберите Python файл для конвертации")
            self.stacked_widget.setCurrentIndex(0)
            self.update_navigation_buttons()
            return
        try:
            subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        except FileNotFoundError:
            reply = QMessageBox.question(self, "PyInstaller не найден",
                                       "PyInstaller не найден в вашей системе. Хотите установить его?",
                                       QMessageBox.StandardButton.Yes |
                                       QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.install_pyinstaller()
            else:
                self.statusBar.showMessage("Сборка отменена: PyInstaller не найден")
            return
        except subprocess.CalledProcessError as e:
             QMessageBox.critical(self, "Ошибка PyInstaller", f"Ошибка при проверке PyInstaller: {e}")
             self.statusBar.showMessage("Ошибка PyInstaller")
             return
        command = [c for c in self.command_preview.toPlainText().split(" ") if c]
        if self.exe_name.text():
             try:
                 file_index = command.index(self.file_path.text())
                 command.insert(file_index, self.exe_name.text())
                 command.insert(file_index, "--name")
             except ValueError:
                 command.extend(["--name", self.exe_name.text()])
        try:
            self.statusBar.showMessage("Создание .exe файла...")
            process = subprocess.Popen(command, cwd=os.path.dirname(self.file_path.text()))
            process.wait()
            if process.returncode == 0:
                self.add_to_history()
                self.statusBar.showMessage("Файл успешно создан!")
                QMessageBox.information(self, "Успех", "Файл .exe успешно создан!")
                self.show_result_buttons(True) 
            else:
                 self.statusBar.showMessage("Ошибка при создании .exe")
                 QMessageBox.critical(self, "Ошибка", f"Ошибка при создании .exe. Код завершения: {process.returncode}")
                 self.show_result_buttons(False) 
        except Exception as e:
            self.statusBar.showMessage("Ошибка при создании .exe")
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
            self.show_result_buttons(False) 
    def install_pyinstaller(self):
        try:
            self.statusBar.showMessage("Установка PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller==6.3.0"])
            self.statusBar.showMessage("PyInstaller успешно установлен.")
            QMessageBox.information(self, "Установка завершена", "PyInstaller успешно установлен.")
        except subprocess.CalledProcessError as e:
            self.statusBar.showMessage("Ошибка при установке PyInstaller")
            QMessageBox.critical(self, "Ошибка установки", f"Не удалось установить PyInstaller: {e}")
    def add_to_history(self):
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": self.command_preview.toPlainText(),
            "file": self.file_path.text()
        }
        history = self.load_history()
        history.append(history_entry)
        try:
            with open("build_history.json", "w") as f:
                json.dump(history, f, indent=4)
        except Exception as e:
             print(f"Ошибка сохранения истории: {e}")
    def load_history(self):
        try:
            with open("build_history.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    def auto_find_dependencies(self):
        if not self.file_path.text():
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите Python файл")
            return
        try:
            imports = extract_imports(self.file_path.text())
            if imports:
                self.hidden_imports.setText(", ".join(imports))
                self.update_command_preview()
                self.statusBar.showMessage(f"Найдено зависимостей: {len(imports)}")
                QMessageBox.information(self, "Успех", 
                    f"Найдены следующие зависимости:\n{', '.join(imports)}")
            else:
                self.statusBar.showMessage("Зависимости не найдены")
                QMessageBox.information(self, "Информация", "Зависимости не найдены")
        except Exception as e:
            self.statusBar.showMessage("Ошибка при поиске зависимостей")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске зависимостей: {e}")
    def open_output_folder(self):
        if not self.file_path.text() or not self.exe_name.text():
            QMessageBox.warning(self, "Предупреждение", "Невозможно определить путь к файлу.")
            return
        output_dir = os.path.join(os.path.dirname(self.file_path.text()), "dist")
        if os.path.exists(output_dir):
            try:
                os.startfile(output_dir)
                self.statusBar.showMessage(f"Открыта папка: {output_dir}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть папку: {e}")
                self.statusBar.showMessage("Ошибка открытия папки")
        else:
            QMessageBox.warning(self, "Предупреждение", "Выходная папка не найдена.")
            self.statusBar.showMessage("Выходная папка не найдена")
    def run_created_exe(self):
        if not self.file_path.text() or not self.exe_name.text():
             QMessageBox.warning(self, "Предупреждение", "Невозможно определить путь к файлу.")
             return
        exe_path = os.path.join(os.path.dirname(self.file_path.text()), "dist", self.exe_name.text() + ".exe")
        if os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path])
                self.statusBar.showMessage(f"Запущен файл: {exe_path}")
            except Exception as e:
                 QMessageBox.critical(self, "Ошибка", f"Не удалось запустить файл: {e}")
                 self.statusBar.showMessage("Ошибка запуска файла")
        else:
             QMessageBox.warning(self, "Предупреждение", "Исполняемый файл не найден.")
             self.statusBar.showMessage("Исполняемый файл не найден")
    def start_new_build(self):
        self.file_path.clear()
        self.exe_name.clear()
        self.icon_path.clear()
        self.hidden_imports.clear()
        self.additional_files.clear()
        self.command_preview.clear()
        self.stacked_widget.setCurrentIndex(0)
        self.update_navigation_buttons()
        self.statusBar.showMessage("Готов к работе")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    if os.path.exists("FitoPyBox.ico"):
        app_icon = QIcon("FitoPyBox.ico")
        app.setWindowIcon(app_icon)
    window = FitoPyBox()
    window.show()
    sys.exit(app.exec()) 