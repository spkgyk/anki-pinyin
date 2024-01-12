from .settings_tab import SettingsTab
from ..utils import ReadingType
from .. import config

from aqt.qt import *


class PinyinOptions(SettingsTab):
    TITLE = "Pinyin Generation Options"

    def init_ui(self):
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

        self.add_label("Options for generating pinyin.")

    def save(self):
        config.set("reading_type", self.reading_type_cb.currentText())
        config.set("traditional_icons", self.trad_icons_tb.isChecked())
        config.write()


SETTINGS_TABS: list[SettingsTab] = [PinyinOptions]
