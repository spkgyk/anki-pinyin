from ..utils import ICON_DIR, ReadingType
from ..user_messages import yes_no_window
from .settings_tab import SettingsTab
from .. import config

from aqt import mw
from aqt.qt import *


class ChineseSettings(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Pinyin Generation Settings")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setWindowIcon(QIcon(str(ICON_DIR / "migaku.png")))
        self.main_layout = self.define_main_layout()
        self.define_signals()
        self.setLayout(self.main_layout)
        self.setFocus()

    def define_main_layout(self):
        main_layout = QVBoxLayout()

        options_layout = self.define_options_layout()
        buttons_layout = self.define_buttons_layout()

        main_layout.addLayout(options_layout)
        main_layout.addLayout(buttons_layout)

        return main_layout

    def define_options_layout(self):
        options_layout = QVBoxLayout()

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

        options_layout.addLayout(reading_layout)
        options_layout.addLayout(trad_icons_layout)

        return options_layout

    def define_buttons_layout(self):
        self.applyButton = QPushButton("Apply")
        self.cancelButton = QPushButton("Cancel")
        self.resetButton = QPushButton("Restore Defaults")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.resetButton)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancelButton)
        buttons_layout.addWidget(self.applyButton)

        return buttons_layout

    def define_signals(self):
        self.cancelButton.clicked.connect(self.close)
        self.applyButton.clicked.connect(self.save_config)
        self.resetButton.clicked.connect(self.load_default_config)

    def save_config(self):
        config.set("reading_type", self.reading_type_cb.currentText())
        config.set("traditional_icons", self.trad_icons_tb.isChecked())
        config.set("simp_fields", [])
        config.set("trad_fields", [])
        config.set("variant_fields", [])
        config.write()
        self.close()

    def load_default_config(self):
        if yes_no_window("Are you sure you would like to restore the default settings? This cannot be undone."):
            config.set("reading_type", ReadingType.PINYIN_TONES.value)
            config.set("traditional_icons", False)
            config.set("simp_fields", ["Simplified", "Simp"])
            config.set("trad_fields", ["Traditional", "Trad"])
            config.set("variant_fields", ["Variant", "Var"])
            config.write()
            self.close()

    @classmethod
    def show_modal(cls):
        settings_window = cls(mw)
        settings_window.exec()


def setup_menu():
    open_chinese_settings_action = QAction("Anki Pinyin Settings", mw)
    open_chinese_settings_action.triggered.connect(ChineseSettings.show_modal)
    mw.form.menuTools.addAction(open_chinese_settings_action)
