from .settings_tab import SettingsTab
from ..utils import ReadingType
from .. import config

from aqt.qt import *


class ReadingOptions(SettingsTab):
    TITLE = "Readings"

    def init_ui(self):
        self.add_label(
            "Default options for generating readings.\n"
            "These settings will when generating readings in the add-card menu or in the browser.\n"
        )

        reading_layout = QHBoxLayout()
        reading_layout.addWidget(QLabel("Default reading type:"))
        reading_layout.addStretch()
        self.reading_type_cb = QComboBox()
        self.reading_type_cb.addItems(sorted([r.value for r in ReadingType]))
        index = self.reading_type_cb.findText(config.get("reading_type"))
        self.reading_type_cb.setCurrentIndex(index)
        reading_layout.addWidget(self.reading_type_cb)

        trad_icons_layout = QHBoxLayout()
        self.trad_icons_tb = QCheckBox()
        self.trad_icons_tb.setChecked(config.get("traditional_icons"))
        trad_icons_layout.addWidget(QLabel("Traditional Icons:"))
        trad_icons_layout.addStretch()
        trad_icons_layout.addWidget(self.trad_icons_tb)

        self.lyt.addLayout(reading_layout)
        self.lyt.addLayout(trad_icons_layout)

    def save(self):
        config.set("reading_type", self.reading_type_cb.currentText())
        config.set("traditional_icons", self.trad_icons_tb.isChecked())
        config.write()


class FieldOptions(SettingsTab):
    TITLE = "Fields"

    def init_ui(self):
        self.add_label("Setup the simplified, traditional and varients fields")
        fields_layout = QVBoxLayout()
        simp_layout = QHBoxLayout()
        trad_layout = QHBoxLayout()
        var_layout = QHBoxLayout()

        self.simp_cb = QComboBox()
        self.simp_cb_label = QLabel("Field:")
        self.trad_cb = QComboBox()
        self.trad_cb_label = QLabel("Field:")
        self.var_cb = QComboBox()
        self.trad_cb_label = QLabel("Field:")

        self.add_simp_field = QPushButton("Add")
        self.add_trad_field = QPushButton("Add")
        self.add_var_field = QPushButton("Add")

        self.simp_fields = QLabel("Already selected fields: " + ", ".join(config.get("simp_fields")))
        self.trad_fields = QLabel("Already selected fields: " + ", ".join(config.get("trad_fields")))
        self.variant_fields = QLabel("Already selected fields: " + ", ".join(config.get("variant_fields")))


SETTINGS_TABS: list[SettingsTab] = [ReadingOptions]
