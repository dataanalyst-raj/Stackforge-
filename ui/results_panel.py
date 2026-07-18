"""
StackForge - Results Panel
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class ResultsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Design Results")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Summary Tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlaceholderText("Run the design to see results here...")
        self.tabs.addTab(self.summary_text, "Summary")

        # Geometry Tab
        self.geometry_table = QTableWidget(0, 6)
        self.geometry_table.setHorizontalHeaderLabels([
            "Zone", "Length (m)", "Top OD (mm)", "Bottom OD (mm)", "Thickness (mm)", "Weight (kg)"
        ])
        self.geometry_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.geometry_table, "Geometry")

        # Wind Loads Tab
        self.wind_table = QTableWidget(0, 5)
        self.wind_table.setHorizontalHeaderLabels([
            "Zone", "Static (kg)", "Dynamic (kg)", "Gust (kg)", "HMW+Dyn (kg)"
        ])
        self.wind_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.wind_table, "Wind Loads")

        # Stress Tab
        self.stress_table = QTableWidget(0, 7)
        self.stress_table.setHorizontalHeaderLabels([
            "Zone", "Axial (kg)", "Moment (kg-m)", "σc", "σb", "Total", "Status"
        ])
        self.stress_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabs.addTab(self.stress_table, "Shell Stress")

        # Base & Flange Tab
        self.base_text = QTextEdit()
        self.base_text.setReadOnly(True)
        self.tabs.addTab(self.base_text, "Base & Flange")

    def display_results(self, results: dict):
        """Populate all result tabs from the calculation engine output."""
        self._show_summary(results)
        self._show_geometry(results)
        self._show_wind(results)
        self._show_stress(results)
        self._show_base_flange(results)

    def _show_summary(self, results: dict):
        s = results.get("summary", {})
        g = results.get("geometry", {})
        d = results.get("dynamic", {})
        across = d.get("across_wind", {})

        text = f"""
STACKFORGE - DESIGN SUMMARY
{'='*50}

GEOMETRY
  Total Height        : {g.get('total_height', 0):.2f} m
  Flare Height        : {g.get('flare_height', 0):.2f} m
  Top OD              : {g.get('top_od', 0):.1f} mm
  Bottom OD           : {g.get('bottom_od', 0):.1f} mm
  Number of Zones     : {len(g.get('zones', []))}

DYNAMIC PROPERTIES
  Natural Frequency   : {s.get('natural_frequency', 0):.4f} Hz
  Time Period         : {s.get('period', 0):.4f} sec
  Across Wind Check   : {across.get('conclusion', 'N/A')}
  Critical Velocity   : {across.get('Vcr', 0):.2f} m/s

LOADS
  Total Weight        : {s.get('total_weight', 0):.0f} kg
  Base Moment         : {s.get('base_moment', 0):.0f} kg-m
  Base Shear          : {s.get('base_shear', 0):.0f} kg

STRESS CHECK
  Max Utilization     : {s.get('max_utilization', 0):.1f} %

{'='*50}
Design completed successfully.
"""
        self.summary_text.setText(text)

    def _show_geometry(self, results: dict):
        zones = results.get("geometry", {}).get("zones", [])
        weights = results.get("weights", {}).get("zones", [])
        thicknesses = results.get("thicknesses", [])

        self.geometry_table.setRowCount(len(zones))
        for i, z in enumerate(zones):
            thk = thicknesses[i]["practical_thickness"] if i < len(thicknesses) else 0
            wt = weights[i]["shell_weight"] if i < len(weights) else 0

            self.geometry_table.setItem(i, 0, QTableWidgetItem(str(z["zone_no"])))
            self.geometry_table.setItem(i, 1, QTableWidgetItem(f"{z['length']:.2f}"))
            self.geometry_table.setItem(i, 2, QTableWidgetItem(f"{z['top_od']:.1f}"))
            self.geometry_table.setItem(i, 3, QTableWidgetItem(f"{z['bottom_od']:.1f}"))
            self.geometry_table.setItem(i, 4, QTableWidgetItem(f"{thk:.0f}"))
            self.geometry_table.setItem(i, 5, QTableWidgetItem(f"{wt:.0f}"))

    def _show_wind(self, results: dict):
        wind_zones = results.get("wind", {}).get("zones", [])
        self.wind_table.setRowCount(len(wind_zones))
        for i, w in enumerate(wind_zones):
            self.wind_table.setItem(i, 0, QTableWidgetItem(str(w["zone_no"])))
            self.wind_table.setItem(i, 1, QTableWidgetItem(f"{w['static_3sec']:.0f}"))
            self.wind_table.setItem(i, 2, QTableWidgetItem(f"{w['dynamic']:.0f}"))
            self.wind_table.setItem(i, 3, QTableWidgetItem(f"{w['gust']:.0f}"))
            self.wind_table.setItem(i, 4, QTableWidgetItem(f"{w['hmw_plus_dynamic']:.0f}"))

    def _show_stress(self, results: dict):
        stresses = results.get("stress", [])
        self.stress_table.setRowCount(len(stresses))
        for i, s in enumerate(stresses):
            self.stress_table.setItem(i, 0, QTableWidgetItem(str(s["zone_no"])))
            self.stress_table.setItem(i, 1, QTableWidgetItem(f"{s['axial_force']:.0f}"))
            self.stress_table.setItem(i, 2, QTableWidgetItem(f"{s['moment']:.0f}"))
            self.stress_table.setItem(i, 3, QTableWidgetItem(f"{s['sigma_c']:.1f}"))
            self.stress_table.setItem(i, 4, QTableWidgetItem(f"{s['sigma_b']:.1f}"))
            self.stress_table.setItem(i, 5, QTableWidgetItem(f"{s['sigma_total']:.1f}"))

            status_item = QTableWidgetItem(s["status"])
            if s["status"] == "OK":
                status_item.setForeground(QColor("#a6e3a1"))
            else:
                status_item.setForeground(QColor("#f38ba8"))
            self.stress_table.setItem(i, 6, status_item)

    def _show_base_flange(self, results: dict):
        base = results.get("base", {})
        flanges = results.get("flanges", [])

        text = "BASE CHAIR DESIGN\n" + "="*40 + "\n\n"
        bolts = base.get("bolts", {})
        text += f"Base OD              : {base.get('base_od', 0):.0f} mm\n"
        text += f"Number of Bolts      : {bolts.get('num_bolts', 0)}\n"
        text += f"Bolt Size            : {bolts.get('bolt_size', '-')}\n"
        text += f"Bolt Circle Diameter : {bolts.get('bolt_circle', 0):.0f} mm\n"
        text += f"Bolt Force           : {bolts.get('bolt_force', 0):.0f} kg\n"
        text += f"Base Plate Thickness : {base.get('base_plate', {}).get('t_practical_mm', 0):.0f} mm\n"
        text += f"Compression Plate    : {base.get('compression_plate_thk', 0):.0f} mm\n"
        text += f"Gusset Status        : {base.get('gusset', {}).get('status', '-')}\n"

        text += "\n\nFLANGE DESIGN\n" + "="*40 + "\n\n"
        for f in flanges:
            text += (f"Section {f.get('section', '-')}:  "
                     f"OD={f.get('flange_od', 0):.0f}  "
                     f"Thk={f.get('thickness', 0):.0f} mm  "
                     f"Bolt={f.get('bolt_size', '-')} × {f.get('num_bolts', 0)}  "
                     f"Force={f.get('bolt_force', 0):.0f} kg  "
                     f"[{f.get('status', '-')}]\n")

        self.base_text.setText(text)
