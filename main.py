"""
StackForge - Steel Chimney Design Software
Main Entry Point
"""

import sys
from PySide6.QtWidgets import QApplication
from app import StackForgeApp


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("StackForge")
    app.setOrganizationName("StackForge")
    app.setApplicationVersion("1.0.0")

    window = StackForgeApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
