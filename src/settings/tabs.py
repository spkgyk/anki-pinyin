from aqt import mw
from aqt.qt import *
from copy import deepcopy

from ..config import Config
from .settings_tab import SettingsTab
from ..utils import ReadingType, OutputMode


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
        index = self.reading_type_cb.findText(Config.reading_type.value)
        self.reading_type_cb.setCurrentIndex(index)
        reading_layout.addWidget(self.reading_type_cb)

        trad_icons_layout = QHBoxLayout()
        self.trad_icons_tb = QCheckBox()
        self.trad_icons_tb.setChecked(Config.traditional_icons)
        trad_icons_layout.addWidget(QLabel("Traditional Icons:"))
        trad_icons_layout.addStretch()
        trad_icons_layout.addWidget(self.trad_icons_tb)

        self.lyt.addLayout(reading_layout)
        self.lyt.addLayout(trad_icons_layout)

        self.collection = self.load_note_dict()
        self.fields = self.load_fields()
        self.add_label(
            "Setup the simplified, traditional and variant fields.\n"
            "These fields will be automatically filled in conjunction with the focused field."
        )
        fields_layout = QHBoxLayout()

        field_label_layout = QVBoxLayout()
        field_cb_layout = QVBoxLayout()
        output_mode_label_layout = QVBoxLayout()
        output_mode_cb_layout = QVBoxLayout()
        button_layout = QVBoxLayout()
        already_layout = QVBoxLayout()

        self.simp_field_cb_label = QLabel("Field:")
        self.simp_field_cb = QComboBox()
        self.simp_field_cb.addItems(self.fields)
        self.simp_output_mode_cb_label = QLabel("Output Mode:")
        self.simp_output_mode_cb = QComboBox()
        self.simp_output_mode_cb.addItems([x.value for x in OutputMode])
        self.add_simp_field = QPushButton("Add")
        self.add_simp_field.clicked.connect(self.simp_add)
        self.simp_fields = deepcopy(Config.simp_fields)
        self.simp_fields_label = QLabel(self.simp_fields.to_set_text())

        self.trad_field_cb_label = QLabel("Field:")
        self.trad_field_cb = QComboBox()
        self.trad_field_cb.addItems(self.fields)
        self.trad_output_mode_cb_label = QLabel("Output Mode:")
        self.trad_output_mode_cb = QComboBox()
        self.trad_output_mode_cb.addItems([x.value for x in OutputMode])
        self.add_trad_field = QPushButton("Add")
        self.add_trad_field.clicked.connect(self.trad_add)
        self.trad_fields = deepcopy(Config.trad_fields)
        self.trad_fields_label = QLabel(self.trad_fields.to_set_text())

        self.var_field_cb_label = QLabel("Field:")
        self.var_field_cb = QComboBox()
        self.var_field_cb.addItems(self.fields)
        self.var_output_mode_cb_label = QLabel("Output Mode:")
        self.var_output_mode_cb = QComboBox()
        self.var_output_mode_cb.addItems([x.value for x in OutputMode])
        self.add_var_field = QPushButton("Add")
        self.add_var_field.clicked.connect(self.var_add)
        self.var_fields = deepcopy(Config.variant_fields)
        self.var_fields_label = QLabel(self.var_fields.to_set_text())

        field_label_layout.addWidget(self.simp_field_cb_label)
        field_label_layout.addWidget(self.trad_field_cb_label)
        field_label_layout.addWidget(self.var_field_cb_label)

        field_cb_layout.addWidget(self.simp_field_cb)
        field_cb_layout.addWidget(self.trad_field_cb)
        field_cb_layout.addWidget(self.var_field_cb)

        output_mode_label_layout.addWidget(self.simp_output_mode_cb_label)
        output_mode_label_layout.addWidget(self.trad_output_mode_cb_label)
        output_mode_label_layout.addWidget(self.var_output_mode_cb_label)

        output_mode_cb_layout.addWidget(self.simp_output_mode_cb)
        output_mode_cb_layout.addWidget(self.trad_output_mode_cb)
        output_mode_cb_layout.addWidget(self.var_output_mode_cb)

        button_layout.addWidget(self.add_simp_field)
        button_layout.addWidget(self.add_trad_field)
        button_layout.addWidget(self.add_var_field)

        already_layout.addWidget(self.simp_fields_label)
        already_layout.addWidget(self.trad_fields_label)
        already_layout.addWidget(self.var_fields_label)

        fields_layout.addLayout(field_label_layout)
        fields_layout.addLayout(field_cb_layout)
        fields_layout.addLayout(output_mode_label_layout)
        fields_layout.addLayout(output_mode_cb_layout)
        fields_layout.addLayout(button_layout)
        fields_layout.addLayout(already_layout)

        self.lyt.addLayout(fields_layout)

    def load_note_dict(self):
        all_models = mw.col.models.all()
        collection = {}

        for note in all_models:
            collection[note["name"]] = {}
            collection[note["name"]]["cardTypes"] = [ct["name"] for ct in note["tmpls"]]
            collection[note["name"]]["fields"] = [f["name"] for f in note["flds"]]
            collection[note["name"]]["id"] = note["id"]

        return collection

    def load_fields(self):
        return sorted(list({field for item in self.collection.values() for field in item["fields"]}))

    def simp_add(self):
        self.simp_fields[self.simp_field_cb.currentText()] = OutputMode(self.simp_output_mode_cb.currentText())
        self.simp_fields_label.setText(self.simp_fields.to_set_text())

    def trad_add(self):
        self.trad_fields[self.trad_field_cb.currentText()] = OutputMode(self.trad_output_mode_cb.currentText())
        self.trad_fields_label.setText(self.trad_fields.to_set_text())

    def var_add(self):
        self.var_fields[self.var_field_cb.currentText()] = OutputMode(self.var_output_mode_cb.currentText())
        self.var_fields_label.setText(self.var_fields.to_set_text())

    def save(self):
        Config.reading_type = ReadingType(self.reading_type_cb.currentText())
        Config.traditional_icons = self.trad_icons_tb.isChecked()
        Config.simp_fields = self.simp_fields
        Config.trad_fields = self.trad_fields
        Config.variant_fields = self.var_fields
        Config.write()


SETTINGS_TABS: list[SettingsTab] = [ReadingOptions]
