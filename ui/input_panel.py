"""
StackForge - Input Panel (All User Inputs)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFormLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QLabel, QHBoxLayout, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from utils.location_data import get_location_list, get_location_data
from core.geometry import calculate_flare_height


class InputPanel(QWidget):
    # Signal emitted when Run button is clicked
    run_design_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Design Inputs")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.create_project_tab()
        self.create_geometry_tab()
        self.create_material_tab()
        self.create_environmental_tab()
        self.create_attachments_tab()
        self.create_preferences_tab()

        # Run button
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Run Complete Design (F5)")
        self.run_btn.setMinimumHeight(42)
        self.run_btn.clicked.connect(self.run_design_clicked.emit)
        btn_layout.addWidget(self.run_btn)
        layout.addLayout(btn_layout)

    def create_project_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)

        self.project_name = QLineEdit()
        self.client_name = QLineEdit()

        self.location = QComboBox()
        self.location.setEditable(True)
        self.location.setInsertPolicy(QComboBox.NoInsert)
        self.location.addItems(get_location_list())
        self.location.setCurrentIndex(-1)
        self.location.setPlaceholderText("Type or select location...")

        self.designed_by = QLineEdit()
        self.checked_by = QLineEdit()

        form.addRow("Project Name *", self.project_name)
        form.addRow("Client Name *", self.client_name)
        form.addRow("Location *", self.location)
        form.addRow("Designed By", self.designed_by)
        form.addRow("Checked By", self.checked_by)

        note = QLabel("Selecting location auto-fills Wind Speed & Seismic Zone")
        note.setStyleSheet("color: #89b4fa; font-size: 11px; padding-top: 6px;")
        form.addRow(note)

        self.tabs.addTab(tab, "Project")

    def create_geometry_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)

        self.total_height = QDoubleSpinBox()
        self.total_height.setRange(5, 300)
        self.total_height.setSuffix(" m")
        self.total_height.setDecimals(2)
        self.total_height.setValue(40.0)

        self.top_id = QDoubleSpinBox()
        self.top_id.setRange(100, 10000)
        self.top_id.setSuffix(" mm")
        self.top_id.setDecimals(1)
        self.top_id.setValue(600)

        self.lined = QComboBox()
        self.lined.addItems(["Unlined", "Lined"])

        self.flare_height = QDoubleSpinBox()
        self.flare_height.setRange(0, 200)
        self.flare_height.setSuffix(" m")
        self.flare_height.setDecimals(2)
        self.flare_height.setValue(0)
        self.flare_height.setSpecialValueText("Auto (Calculated)")

        self.bottom_od = QDoubleSpinBox()
        self.bottom_od.setRange(200, 15000)
        self.bottom_od.setSuffix(" mm")
        self.bottom_od.setDecimals(1)
        self.bottom_od.setValue(2400)

        self.base_elevation = QDoubleSpinBox()
        self.base_elevation.setRange(0, 50)
        self.base_elevation.setSuffix(" m")
        self.base_elevation.setValue(0.0)

        form.addRow("Total Height (H) *", self.total_height)
        form.addRow("Top Nominal ID *", self.top_id)
        form.addRow("Lined / Unlined *", self.lined)
        form.addRow("Flare Height", self.flare_height)
        form.addRow("Bottom Outer Diameter *", self.bottom_od)
        form.addRow("Base Elevation", self.base_elevation)

        self.flare_note = QLabel("Flare Height will be auto-calculated")
        self.flare_note.setStyleSheet("color: #89b4fa; font-size: 11px;")
        form.addRow(self.flare_note)

        self.tabs.addTab(tab, "Geometry")

    def create_material_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)

        self.material = QComboBox()
        self.material.addItems(["IS 2062", "ASTM A36", "Other"])

        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(20, 500)
        self.temperature.setSuffix(" °C")
        self.temperature.setValue(250)

        self.int_corrosion = QDoubleSpinBox()
        self.int_corrosion.setRange(0, 10)
        self.int_corrosion.setSuffix(" mm")
        self.int_corrosion.setValue(3.0)
        self.int_corrosion.setDecimals(1)

        self.ext_corrosion = QDoubleSpinBox()
        self.ext_corrosion.setRange(0, 5)
        self.ext_corrosion.setSuffix(" mm")
        self.ext_corrosion.setValue(0.0)
        self.ext_corrosion.setDecimals(1)

        form.addRow("Shell Material *", self.material)
        form.addRow("Design Temperature *", self.temperature)
        form.addRow("Internal Corrosion *", self.int_corrosion)
        form.addRow("External Corrosion", self.ext_corrosion)

        self.tabs.addTab(tab, "Material")

    def create_environmental_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)

        self.wind_speed = QDoubleSpinBox()
        self.wind_speed.setRange(20, 80)
        self.wind_speed.setSuffix(" m/s")
        self.wind_speed.setValue(47)
        self.wind_speed.setDecimals(1)

        self.terrain = QComboBox()
        self.terrain.addItems(["Category 1", "Category 2", "Category 3", "Category 4"])
        self.terrain.setCurrentIndex(2)

        self.seismic_zone = QComboBox()
        self.seismic_zone.addItems(["Zone 2", "Zone 3", "Zone 4", "Zone 5"])
        self.seismic_zone.setCurrentText("Zone 4")

        self.importance = QDoubleSpinBox()
        self.importance.setRange(1.0, 2.0)
        self.importance.setSingleStep(0.1)
        self.importance.setValue(1.5)
        self.importance.setDecimals(2)

        form.addRow("Basic Wind Speed (Vb) *", self.wind_speed)
        form.addRow("Terrain Category *", self.terrain)
        form.addRow("Seismic Zone *", self.seismic_zone)
        form.addRow("Importance Factor (I)", self.importance)

        note = QLabel("Auto-filled from Location (you can still change)")
        note.setStyleSheet("color: #89b4fa; font-size: 11px;")
        form.addRow(note)

        self.tabs.addTab(tab, "Environmental")

    def create_attachments_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)

        self.num_platforms = QSpinBox()
        self.num_platforms.setRange(0, 10)
        self.num_platforms.setValue(2)

        self.platform_width = QDoubleSpinBox()
        self.platform_width.setRange(300, 2000)
        self.platform_width.setSuffix(" mm")
        self.platform_width.setValue(900)

        self.strakes = QComboBox()
        self.strakes.addItems(["No", "Yes"])

        form.addRow("Number of Platforms", self.num_platforms)
        form.addRow("Platform Width", self.platform_width)
        form.addRow("Helical Strakes", self.strakes)

        self.tabs.addTab(tab, "Attachments")

    def create_preferences_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        form.setSpacing(10)

        self.min_flange_thk = QDoubleSpinBox()
        self.min_flange_thk.setRange(8, 30)
        self.min_flange_thk.setSuffix(" mm")
        self.min_flange_thk.setValue(12)

        self.min_bolt = QComboBox()
        self.min_bolt.addItems(["M20", "M24", "M27", "M30"])
        self.min_bolt.setCurrentText("M24")

        self.base_plate_width = QDoubleSpinBox()
        self.base_plate_width.setRange(200, 500)
        self.base_plate_width.setSuffix(" mm")
        self.base_plate_width.setValue(300)

        form.addRow("Min Flange Thickness", self.min_flange_thk)
        form.addRow("Min Bolt Size", self.min_bolt)
        form.addRow("Base Plate Width", self.base_plate_width)

        self.tabs.addTab(tab, "Preferences")

    def connect_signals(self):
        # Location change → auto fill wind speed + seismic zone
        self.location.currentTextChanged.connect(self.on_location_changed)

        # Geometry change → auto calculate flare height
        self.total_height.valueChanged.connect(self.update_flare_height)
        self.top_id.valueChanged.connect(self.update_flare_height)
        self.lined.currentTextChanged.connect(self.update_flare_height)

    def on_location_changed(self, location_name: str):
        data = get_location_data(location_name)
        if data:
            self.wind_speed.setValue(data["wind_speed"])
            self.seismic_zone.setCurrentText(data["seismic_zone"])

    def update_flare_height(self):
        h = self.total_height.value()
        top_id = self.top_id.value()
        is_lined = self.lined.currentText() == "Lined"

        if h > 0 and top_id > 0:
            suggested = calculate_flare_height(h, top_id, is_lined)
            self.flare_height.setValue(round(suggested, 2))
            self.flare_note.setText(f"Auto-calculated: {suggested:.2f} m (you can override)")

    def get_all_inputs(self) -> dict:
        """Collect all user inputs into a dictionary."""
        return {
            "project_name": self.project_name.text(),
            "client_name": self.client_name.text(),
            "location": self.location.currentText(),
            "designed_by": self.designed_by.text(),
            "checked_by": self.checked_by.text(),
            "total_height": self.total_height.value(),
            "top_id": self.top_id.value(),
            "is_lined": self.lined.currentText() == "Lined",
            "flare_height": self.flare_height.value(),
            "bottom_od": self.bottom_od.value(),
            "base_elevation": self.base_elevation.value(),
            "material": self.material.currentText(),
            "temperature": self.temperature.value(),
            "int_corrosion": self.int_corrosion.value(),
            "ext_corrosion": self.ext_corrosion.value(),
            "wind_speed": self.wind_speed.value(),
            "terrain": self.terrain.currentText(),
            "seismic_zone": self.seismic_zone.currentText(),
            "importance": self.importance.value(),
            "num_platforms": self.num_platforms.value(),
            "platform_width": self.platform_width.value(),
            "strakes": self.strakes.currentText() == "Yes",
            "min_flange_thk": self.min_flange_thk.value(),
            "min_bolt": self.min_bolt.currentText(),
            "base_plate_width": self.base_plate_width.value(),
        }
