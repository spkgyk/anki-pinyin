from aqt.qt import *
from copy import deepcopy
from aqt.utils import showInfo

from ..config import Config
from .settings_tab import SettingsTab
from ..utils import ReadingType, OutputMode


class ReadingOptions(SettingsTab):
    TITLE = "Generation"

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

        self.load_note_dict()
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


class CSSJSGenerationSettings(SettingsTab):
    TITLE = "Notes"

    def init_ui(self):
        self.add_label("Automatic CSS JS generation settings.")

        self.load_note_dict()

        self.front_table = QTableWidget()
        self.back_table = QTableWidget()

        self.nt_cb = QComboBox()
        self.ct_cb = QComboBox()
        self.fb_cb = QComboBox()

        self.nt_cb.currentTextChanged.connect(self.reveal_ct)
        self.nt_cb.addItems(sorted(self.collection.keys()))

        self.ct_cb.currentTextChanged.connect(self.load_table)

        self.fb_cb.currentTextChanged.connect(self.load_table)

        self.lyt.addWidget(self.nt_cb)
        self.lyt.addWidget(self.ct_cb)
        self.lyt.addWidget(self.fb_cb)

    def reveal_ct(self, text: str):
        self.ct_cb.clear()
        self.ct_cb.addItems(self.collection[text]["card_types"])

        self.fb_cb.clear()
        self.fb_cb.addItems(self.collection[text]["fields"])

    def load_table(self, text):
        front_back: list[tuple[str, QTableWidget]] = [("qfmt", self.front_table), ("afmt", self.back_table)]
        # for fmt, list_widget in front_back:
        #     list_widget.clear()
        #     list_widget.verticalHeader().hide()
        #     list_widget.setColumnCount(4)
        #     list_widget.setHorizontalHeaderLabels(["Field", "Reading Type", "Reading Mode", "Tone Coloring"])

        #     list_widget.horizontalHeader().resizeSection(0, 200)

        #     list_widget.setRowCount(len(fields_settings))

        #     for i, (field_name, field_settings) in enumerate(fields_settings):
        #         if self.hide_field(field_name):
        #             list_widget.hideRow(i)

        #         field_name_clean = self.clean_field_name(field_name)

        #         field_item = QTableWidgetItem(field_name_clean)
        #         field_item.setFlags(field_item.flags() & ~(Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable))

        #         list_widget.setItem(i, 0, field_item)

        #         if self.current_lang:
        #             for j, f in enumerate(self.current_lang.field_settings):
        #                 setting_box = QComboBox()
        #                 setting_box.addItems([f.label for f in f.options])
        #                 list_widget.setCellWidget(i, j + 1, setting_box)
        #                 if f.name in field_settings:
        #                     value = field_settings[f.name]
        #                     for k, o in enumerate(f.options):
        #                         if o.value == value:
        #                             setting_box.setCurrentIndex(k)
        #                             break


SETTINGS_TABS: list[SettingsTab] = [ReadingOptions]
