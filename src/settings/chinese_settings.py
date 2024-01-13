from ..utils import ICON_DIR, ReadingType
from ..user_messages import yes_no_window
from .. import config
from .tabs import SETTINGS_TABS

from aqt import mw
from aqt.qt import *


class ChineseSettings(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("Pinyin Generation Settings")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setWindowIcon(QIcon(str(ICON_DIR / "migaku.png")))
        self.define_main_layout()

    def define_main_layout(self):
        self.main_layout = QVBoxLayout()

        self.tab_widget = self.define_tabs()
        self.buttons_layout = self.define_buttons_layout()

        self.main_layout.addLayout(self.tab_widget)
        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

    def define_tabs(self):
        tab_bar = QTabBar()
        stack = QStackedWidget()
        tab_bar.currentChanged.connect(lambda index: stack.setCurrentIndex(index))

        self.tabs = []

        for tab_class in SETTINGS_TABS:
            _tab = tab_class()
            self.tabs.append(_tab)
            tab_bar.addTab(_tab.TITLE)
            stack.addWidget(_tab)

        layout = QVBoxLayout()
        layout.addWidget(tab_bar)
        layout.addWidget(stack)

        return layout

    def define_buttons_layout(self):
        self.resetButton = QPushButton("Restore Defaults")
        self.resetButton.clicked.connect(self.load_default_config)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)

        self.applyButton = QPushButton("Apply")
        self.applyButton.clicked.connect(self.save_config)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.resetButton)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancelButton)
        buttons_layout.addWidget(self.applyButton)

        return buttons_layout

    def save_config(self):
        for tab in self.tabs:
            tab.save()
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
