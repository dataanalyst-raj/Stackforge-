"""
StackForge - Main Application Window
"""

import os
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStatusBar, QToolBar, QMessageBox, QFileDialog
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from ui.theme_manager import ThemeManager
from ui.input_panel import InputPanel
from ui.results_panel import ResultsPanel
from core.engine import run_complete_design
from core.report_generator import generate_pdf_report


class StackForgeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StackForge - Steel Chimney Design Software")
        self.resize(1450, 920)

        self.theme_manager = ThemeManager(self)
        self.current_results = None

        self.init_ui()
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()

        # Apply default theme (Dark)
        self.theme_manager.apply_theme("dark")

        # Connect Run button
        self.input_panel.run_design_clicked.connect(self.run_design)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Left side - Inputs
        self.input_panel = InputPanel()
        main_layout.addWidget(self.input_panel, stretch=2)

        # Right side - Results
        self.results_panel = ResultsPanel()
        main_layout.addWidget(self.results_panel, stretch=3)

    def create_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_pdf = QAction("Export Report (PDF)", self)
        export_pdf.setShortcut("Ctrl+P")
        export_pdf.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf)

        export_excel = QAction("Export Report (Excel)", self)
        file_menu.addAction(export_excel)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Calculate Menu
        calc_menu = menubar.addMenu("&Calculate")

        run_all = QAction("Run Complete Design", self)
        run_all.setShortcut("F5")
        run_all.triggered.connect(self.run_design)
        calc_menu.addAction(run_all)

        # View Menu
        view_menu = menubar.addMenu("&View")

        dark_action = QAction("Dark Theme", self)
        dark_action.triggered.connect(lambda: self.theme_manager.apply_theme("dark"))
        view_menu.addAction(dark_action)

        light_action = QAction("Light Theme", self)
        light_action.triggered.connect(lambda: self.theme_manager.apply_theme("light"))
        view_menu.addAction(light_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About StackForge", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        run_action = QAction("▶  Run Design", self)
        run_action.triggered.connect(self.run_design)
        toolbar.addAction(run_action)

        toolbar.addSeparator()

        pdf_action = QAction("Export PDF", self)
        pdf_action.triggered.connect(self.export_pdf)
        toolbar.addAction(pdf_action)

        toolbar.addSeparator()

        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self.theme_manager.toggle_theme)
        toolbar.addAction(theme_action)

    def create_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Ready | StackForge v1.0.0")

    def run_design(self):
        """Execute complete design calculation."""
        try:
            self.statusBar().showMessage("Calculating... Please wait")
            inputs = self.input_panel.get_all_inputs()

            # Basic validation
            if inputs["total_height"] < 5:
                QMessageBox.warning(self, "Input Error", "Total Height must be at least 5 m.")
                return
            if inputs["top_id"] < 100:
                QMessageBox.warning(self, "Input Error", "Top Nominal ID is too small.")
                return
            if inputs["bottom_od"] <= inputs["top_id"]:
                QMessageBox.warning(self, "Input Error", "Bottom OD must be greater than Top ID.")
                return

            results = run_complete_design(inputs)
            self.current_results = results

            if "error" in results:
                QMessageBox.critical(self, "Calculation Error", results["error"])
                return

            # Display results
            self.results_panel.display_results(results)

            summary = results.get("summary", {})
            self.statusBar().showMessage(
                f"Design Complete | Weight: {summary.get('total_weight', 0):.0f} kg | "
                f"Freq: {summary.get('natural_frequency', 0):.3f} Hz | "
                f"Max Utilization: {summary.get('max_utilization', 0):.1f}%"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during calculation:\n\n{str(e)}")
            self.statusBar().showMessage("Calculation failed")

    def export_pdf(self):
        """Export current results to PDF."""
        if not self.current_results:
            QMessageBox.warning(self, "No Results", "Please run the design first before exporting.")
            return

        default_name = f"StackForge_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            default_name,
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        try:
            generate_pdf_report(self.current_results, path)
            QMessageBox.information(self, "Success", f"PDF report saved successfully:\n{path}")
            self.statusBar().showMessage(f"PDF exported: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to generate PDF:\n\n{str(e)}")

    def show_about(self):
        QMessageBox.about(
            self,
            "About StackForge",
            "<h2>StackForge</h2>"
            "<p><b>Professional Steel Chimney Design Software</b></p>"
            "<p>Version 1.0.0</p>"
            "<p>Based on IS 6533, IS 875 (Part 3) & IS 1893</p>"
            "<p>Dark / Light Theme Supported</p>"
        )
