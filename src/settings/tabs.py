from .settings_tab import SettingsTab
from ..utils import ReadingType
from .. import config

from aqt import mw
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
        self.collection = self.load_note_dict()
        self.fields = self.load_fields()
        self.add_label("Setup the simplified, traditional and varients fields")
        fields_layout = QHBoxLayout()

        # ct_label_layout = QVBoxLayout()
        # ct_cb_layout = QVBoxLayout()
        field_label_layout = QVBoxLayout()
        field_cb_layout = QVBoxLayout()
        button_layout = QVBoxLayout()
        already_layout = QVBoxLayout()

        # self.simp_ct_cb_label = QLabel("Card:")
        # self.simp_ct_cb = QComboBox()
        self.simp_field_cb_label = QLabel("Field:")
        self.simp_field_cb = QComboBox()
        self.simp_field_cb.addItems(self.fields)
        self.add_simp_field = QPushButton("Add")
        self.add_simp_field.clicked.connect(self.simp_add)
        self.simp_fields = QLabel("Already selected fields: " + ", ".join(config.get("simp_fields")))

        # self.simp_ct_cb.currentIndexChanged.connect(self.simp_selection_changed)
        # self.simp_ct_cb.addItems(sorted(list(self.collection.keys())))

        # self.trad_ct_cb_label = QLabel("Card:")
        # self.trad_ct_cb = QComboBox()
        self.trad_field_cb_label = QLabel("Field:")
        self.trad_field_cb = QComboBox()
        self.trad_field_cb.addItems(self.fields)
        self.add_trad_field = QPushButton("Add")
        self.add_trad_field.clicked.connect(self.trad_add)
        self.trad_fields = QLabel("Already selected fields: " + ", ".join(config.get("trad_fields")))

        # self.trad_ct_cb.currentIndexChanged.connect(self.trad_selection_changed)
        # self.trad_ct_cb.addItems(sorted(list(self.collection.keys())))

        # self.var_ct_cb_label = QLabel("Card:")
        # self.var_ct_cb = QComboBox()
        self.var_field_cb_label = QLabel("Field:")
        self.var_field_cb = QComboBox()
        self.var_field_cb.addItems(self.fields)
        self.add_var_field = QPushButton("Add")
        self.add_var_field.clicked.connect(self.var_add)
        self.var_fields = QLabel("Already selected fields: " + ", ".join(config.get("variant_fields")))

        # self.var_ct_cb.currentIndexChanged.connect(self.var_selection_changed)
        # self.var_ct_cb.addItems(sorted(list(self.collection.keys())))

        # ct_label_layout.addWidget(self.simp_ct_cb_label)
        # ct_label_layout.addWidget(self.trad_ct_cb_label)
        # ct_label_layout.addWidget(self.var_ct_cb_label)

        # ct_cb_layout.addWidget(self.simp_ct_cb)
        # ct_cb_layout.addWidget(self.trad_ct_cb)
        # ct_cb_layout.addWidget(self.var_ct_cb)

        field_label_layout.addWidget(self.simp_field_cb_label)
        field_label_layout.addWidget(self.trad_field_cb_label)
        field_label_layout.addWidget(self.var_field_cb_label)

        field_cb_layout.addWidget(self.simp_field_cb)
        field_cb_layout.addWidget(self.trad_field_cb)
        field_cb_layout.addWidget(self.var_field_cb)

        button_layout.addWidget(self.add_simp_field)
        button_layout.addWidget(self.add_trad_field)
        button_layout.addWidget(self.add_var_field)

        already_layout.addWidget(self.simp_fields)
        already_layout.addWidget(self.trad_fields)
        already_layout.addWidget(self.var_fields)

        # fields_layout.addLayout(ct_label_layout)
        # fields_layout.addLayout(ct_cb_layout)
        fields_layout.addLayout(field_label_layout)
        fields_layout.addLayout(field_cb_layout)
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

    # def simp_selection_changed(self):
    #     self.simp_field_cb.clear()
    #     self.simp_field_cb.addItems(sorted(self.collection.get(self.simp_ct_cb.currentText()).get("fields")))

    # def trad_selection_changed(self):
    #     self.trad_field_cb.clear()
    #     self.trad_field_cb.addItems(sorted(self.collection.get(self.simp_ct_cb.currentText()).get("fields")))

    # def var_selection_changed(self):
    #     self.var_field_cb.clear()
    #     self.var_field_cb.addItems(sorted(self.collection.get(self.simp_ct_cb.currentText()).get("fields")))

    def simp_add(self):
        self.simp_fields.setText(self.simp_fields.text() + ", " + self.simp_field_cb.currentText())
        self.simp_field_cb.removeItem(self.simp_field_cb.currentIndex())
        self.simp_field_cb.setCurrentIndex(0)

    def trad_add(self):
        self.trad_fields.setText(self.trad_fields.text() + ", " + self.trad_field_cb.currentText())
        self.trad_field_cb.removeItem(self.trad_field_cb.currentIndex())
        self.trad_field_cb.setCurrentIndex(0)

    def var_add(self):
        self.var_fields.setText(self.var_fields.text() + ", " + self.var_field_cb.currentText())
        self.var_field_cb.removeItem(self.var_field_cb.currentIndex())
        self.var_field_cb.setCurrentIndex(0)

    def save(self):
        simp_fields = self.simp_fields.text().split(": ", 1)[-1]
        simp_fields = sorted(x.lower().capitalize() for x in simp_fields.split(", "))
        trad_fields = self.trad_fields.text().split(": ", 1)[-1]
        trad_fields = sorted(x.lower().capitalize() for x in trad_fields.split(", "))
        var_fields = self.var_fields.text().split(": ", 1)[-1]
        var_fields = sorted(x.lower().capitalize() for x in var_fields.split(", "))
        config.set("simp_fields", simp_fields)
        config.set("trad_fields", trad_fields)
        config.set("variant_fields", var_fields)
        config.write()


SETTINGS_TABS: list[SettingsTab] = [ReadingOptions, FieldOptions]
