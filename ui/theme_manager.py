"""
StackForge - Theme Manager (Dark / Light)
"""

from PySide6.QtWidgets import QApplication


DARK_THEME = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    background: #1e1e2e;
}
QTabBar::tab {
    background: #313244;
    color: #cdd6f4;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background: #89b4fa;
    color: #1e1e2e;
    font-weight: bold;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #89b4fa;
}
QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #b4befe;
}
QPushButton:pressed {
    background-color: #74c7ec;
}
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 12px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
}
QMenuBar::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QMenu {
    background-color: #313244;
    color: #cdd6f4;
}
QMenu::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
}
QToolBar {
    background-color: #181825;
    border: none;
    spacing: 6px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QHeaderView::section {
    background-color: #313244;
    color: #cdd6f4;
    padding: 6px;
    border: 1px solid #45475a;
}
QTableWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    gridline-color: #45475a;
}
"""

LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f5f5f7;
    color: #1d1d1f;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #d2d2d7;
    background: #ffffff;
}
QTabBar::tab {
    background: #e8e8ed;
    color: #1d1d1f;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background: #0071e3;
    color: white;
    font-weight: bold;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #1d1d1f;
    border: 1px solid #d2d2d7;
    border-radius: 4px;
    padding: 5px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0071e3;
}
QPushButton {
    background-color: #0071e3;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0077ed;
}
QPushButton:pressed {
    background-color: #006edb;
}
QGroupBox {
    border: 1px solid #d2d2d7;
    border-radius: 6px;
    margin-top: 12px;
    font-weight: bold;
    color: #0071e3;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QMenuBar {
    background-color: #ffffff;
    color: #1d1d1f;
}
QMenuBar::item:selected {
    background-color: #0071e3;
    color: white;
}
QMenu {
    background-color: #ffffff;
    color: #1d1d1f;
}
QMenu::item:selected {
    background-color: #0071e3;
    color: white;
}
QStatusBar {
    background-color: #ffffff;
    color: #6e6e73;
}
QToolBar {
    background-color: #ffffff;
    border: none;
    spacing: 6px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QHeaderView::section {
    background-color: #e8e8ed;
    color: #1d1d1f;
    padding: 6px;
    border: 1px solid #d2d2d7;
}
QTableWidget {
    background-color: #ffffff;
    color: #1d1d1f;
    gridline-color: #d2d2d7;
}
"""


class ThemeManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_theme = "dark"

    def apply_theme(self, theme_name: str):
        app = QApplication.instance()
        if theme_name == "dark":
            app.setStyleSheet(DARK_THEME)
            self.current_theme = "dark"
        else:
            app.setStyleSheet(LIGHT_THEME)
            self.current_theme = "light"

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.apply_theme("light")
        else:
            self.apply_theme("dark")
