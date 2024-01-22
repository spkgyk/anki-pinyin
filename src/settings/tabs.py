import platform

from aqt.qt import *
from copy import deepcopy
from aqt.theme import theme_manager

from ..config import Config
from .settings_tab import SettingsTab
from ..utils import ReadingType, OutputMode


def is_windows_10():
    system = platform.system()
    release = platform.release()

    if system == "Windows" and "10" in release:
        return True
    return False


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


# class CSSJSGenerationSettings(SettingsTab):
#     TITLE = "Notes"

#     def init_ui(self):
#         self.add_label("Automatic CSS JS generation settings.")

#         self.load_note_dict()

#         self.autoCSSJS = QCheckBox()
#         self.profileAF = QComboBox()
#         self.noteTypeAF = QComboBox()
#         self.cardTypeAF = QComboBox()
#         self.fieldAF = QComboBox()
#         self.sideAF = QComboBox()
#         self.displayAF = QComboBox()
#         self.readingAF = QComboBox()
#         self.addEditAF = QPushButton("Add")
#         self.afTable = self.getAFTable()

#         afl = QVBoxLayout()  # active fields layout

#         afh1 = QHBoxLayout()
#         afh1.addWidget(QLabel("Auto CSS & JS Generation:"))
#         afh1.addWidget(self.autoCSSJS)
#         afh1.addStretch()
#         afl.addLayout(afh1)

#         afh2 = QHBoxLayout()
#         afh2.addWidget(self.profileAF)
#         afh2.addWidget(self.noteTypeAF)
#         afh2.addWidget(self.cardTypeAF)
#         afh2.addWidget(self.fieldAF)
#         afh2.addWidget(self.sideAF)
#         afh2.addWidget(self.displayAF)
#         afh2.addWidget(self.readingAF)
#         afl.addLayout(afh2)

#         afh3 = QHBoxLayout()
#         afh3.addStretch()
#         afh3.addWidget(self.addEditAF)
#         afl.addLayout(afh3)

#         afl.addWidget(self.afTable)

#         self.lyt.addLayout(afl)

#         self.profileAF.currentIndexChanged.connect(self.profileChange)

#     def getAFTable(self):
#         afTable = QTableWidget(self)
#         if is_windows_10() and theme_manager.night_mode != True:
#             afTable.setStyleSheet(
#                 "QHeaderView::section{"
#                 "border-top:0px solid #D8D8D8;"
#                 "border-left:0px solid #D8D8D8;"
#                 "border-right:1px solid #D8D8D8;"
#                 "border-bottom: 1px solid #D8D8D8;"
#                 "background-color:white;"
#                 "padding:4px;"
#                 "}"
#                 "QTableCornerButton::section{"
#                 "border-top:0px solid #D8D8D8;"
#                 "border-left:0px solid #D8D8D8;"
#                 "border-right:1px solid #D8D8D8;"
#                 "border-bottom: 1px solid #D8D8D8;"
#                 "background-color:white;"
#                 "}"
#             )
#         afTable.setSortingEnabled(True)
#         afTable.setColumnCount(8)
#         afTable.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
#         afTable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#         tableHeader = afTable.horizontalHeader()
#         afTable.setHorizontalHeaderLabels(["Profile", "Note Type", "Card Type", "Field", "Side", "Display Type", "Reading Type", ""])
#         tableHeader.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
#         tableHeader.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
#         tableHeader.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
#         tableHeader.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
#         tableHeader.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
#         tableHeader.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
#         tableHeader.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
#         tableHeader.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
#         afTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
#         return afTable

#     def loadAllProfiles(self):
#         if not self.sortedProfiles and not self.sortedNoteTypes:
#             profL = []
#             noteL = []
#             for prof in self.cA:
#                 profL.append(prof)
#                 for noteType in self.cA[prof]:
#                     noteL.append([noteType + " (Prof:" + prof + ")", prof + ":pN:" + noteType])
#             self.sortedProfiles = self.ciSort(profL)
#             self.sortedNoteTypes = sorted(noteL, key=itemgetter(0))
#         aP = self.profileAF
#         for prof in self.sortedProfiles:
#             aP.addItem(prof)
#             aP.setItemData(aP.count() - 1, prof, Qt.ToolTipRole)
#         self.loadAllNotes()

#     def loadAllNotes(self):
#         for noteType in self.sortedNoteTypes:
#             self.noteTypeAF.addItem(noteType[0])
#             self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, noteType[0], Qt.ToolTipRole)
#             self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, noteType[1])

#     def profileChange(self):
#         self.noteTypeAF.clear()
#         self.cardTypeAF.clear()
#         self.fieldAF.clear()
#         if self.profileAF.currentIndex() == 0:
#             self.loadAllNotes()
#         else:
#             prof = self.profileAF.currentText()
#             for noteType in self.ciSort(self.cA[prof]):
#                 self.noteTypeAF.addItem(noteType)
#                 self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, noteType + " (Prof:" + prof + ")", Qt.ToolTipRole)
#                 self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, prof + ":pN:" + noteType)
#         self.loadCardTypesFields()


SETTINGS_TABS: list[SettingsTab] = [ReadingOptions]
