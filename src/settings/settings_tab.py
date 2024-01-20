from aqt import mw
from aqt.qt import *
from aqt.utils import openLink


class SettingsTab(QWidget):
    TITLE = None
    SUBTITLE = None
    PIXMAP = None
    BOTTOM_STRETCH = True

    def __init__(self, parent=None, is_tutorial=False):
        super().__init__(parent)

        self.is_tutorial = is_tutorial

        self.lyt = QVBoxLayout()
        self.setLayout(self.lyt)
        self.init_ui()
        self.toggle_advanced(False)
        if self.BOTTOM_STRETCH:
            self.lyt.addStretch()

    def init_ui(self):
        pass

    def toggle_advanced(self, state: bool):
        pass

    def save(self):
        pass

    @classmethod
    def wizard_page(cls, parent=None, is_tutorial=True):
        _widget = cls(is_tutorial)
        return cls.WizardPage(_widget, parent, is_tutorial)

    @classmethod
    def make_label(cls, text: str):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        lbl.linkActivated.connect(openLink)
        return lbl

    def add_label(self, text: str):
        lbl = self.make_label(text)
        self.lyt.addWidget(lbl)
        return lbl

    def load_note_dict(self):
        all_models = mw.col.models.all()
        self.collection = {}
        self.fields = set()

        for note in all_models:
            self.collection[note["name"]] = {}
            self.collection[note["name"]]["card_types"] = [ct["name"] for ct in note["tmpls"]]
            self.collection[note["name"]]["fields"] = [f["name"] for f in note["flds"]]
            self.collection[note["name"]]["id"] = note["id"]

            self.fields.update(self.collection[note["name"]]["fields"])

        self.fields = sorted(list(self.fields))

    class WizardPage(QWizardPage):
        def __init__(self, widget: "SettingsTab", parent: QWidget = None, is_tutorial: bool = True):
            super().__init__(parent)
            self.widget = widget
            if self.widget.TITLE:
                self.setTitle(self.widget.TITLE)
            if self.widget.SUBTITLE:
                self.setSubTitle(self.widget.SUBTITLE)
            if self.widget.PIXMAP:
                if hasattr(QWizard, "WizardPixmap"):
                    QWizard_WatermarkPixmap = QWizard.WizardPixmap.WatermarkPixmap
                else:
                    QWizard_WatermarkPixmap = QWizard.WatermarkPixmap
                self.setPixmap(QWizard_WatermarkPixmap, QPixmap(self.widget.PIXMAP))
            self.lyt = QVBoxLayout()
            self.lyt.setContentsMargins(0, 0, 0, 0)
            self.lyt.addWidget(self.widget)
            self.setLayout(self.lyt)

        def save(self):
            self.widget.save()
