from .tokenizer import (
    strip_migaku,
    to_migaku,
    BASE_DIR,
)

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from aqt import gui_hooks
from aqt.editor import Editor
from aqt.browser import Browser
from anki.find import fieldNamesForNotes
from anki.notes import NoteId
from typing import Sequence


def miInfo(text, parent=False, level="msg", day=True):
    if level == "wrn":
        title = "Migaku Chinese Warning"
    elif level == "not":
        title = "Migaku Chinese Notice"
    elif level == "err":
        title = "Migaku Chinese Error"
    else:
        title = "Migaku Chinese"
    if parent is False:
        parent = mw.app.activeWindow() or mw
    icon = QIcon(str(BASE_DIR / "icons" / "migaku.png"))
    mb = QMessageBox(parent)
    if not day:
        mb.setStyleSheet(" QMessageBox {background-color: #272828;}")
    mb.setText(text)
    mb.setWindowIcon(icon)
    mb.setWindowTitle(title)
    b = mb.addButton(QMessageBox.Ok)
    b.setFixedSize(100, 30)
    b.setDefault(True)

    return mb.exec()


def miAsk(text, parent=None, day=True):
    msg = QMessageBox(parent)
    msg.setWindowTitle("Migaku Chinese")
    msg.setText(text)
    icon = QIcon(str(BASE_DIR / "icons" / "migaku.png"))
    b = msg.addButton(QMessageBox.StandardButton.Yes)
    b.setFixedSize(100, 30)
    b.setDefault(True)
    c = msg.addButton(QMessageBox.StandardButton.No)
    c.setFixedSize(100, 30)
    if not day:
        msg.setStyleSheet(" QMessageBox {background-color: #272828;}")
    msg.setWindowIcon(icon)
    msg.exec()
    if msg.clickedButton() == b:
        return True
    else:
        return False


def getProgressWidget():
    progressWidget = QWidget(None)
    progressWidget.setFixedSize(400, 70)
    progressWidget.setWindowModality(Qt.WindowModality.ApplicationModal)
    progressWidget.setWindowIcon(QIcon(str(BASE_DIR, "icons", "migaku.png")))
    bar = QProgressBar(progressWidget)
    bar.setFixedSize(390, 50)
    bar.move(10, 10)
    per = QLabel(bar)
    per.setAlignment(Qt.AlignmentFlag.AlignCenter)
    progressWidget.show()
    return bar


def applyOM(self, addType: str, dest: str, text: str):
    if text:
        if addType == "If Empty":
            if dest == "":
                dest = text
        elif addType == "Add":
            if dest == "":
                dest = text
            else:
                dest += "<br>" + text
        else:
            dest = text
    return dest


def generate_migaku_editor(editor: Editor):
    id = editor.currentField
    selected_text = editor.note.fields[id]
    modified_text = to_migaku(selected_text, "cn")
    editor.note.fields[id] = modified_text
    editor.loadNoteKeepingFocus()  # Refresh the editor


def mass_generate_migaku_browser(source: str, dest: str, output_mode: str, reading_type: str, notes: Sequence[NoteId], widget: QDialog):
    mw.checkpoint("Chinese Reading Generation")
    if not miAsk('Are you sure you want to generate from the "' + source + '" field into  the "' + dest + '" field?.'):
        return
    widget.close()
    bar = getProgressWidget()
    bar.setMinimum(0)
    bar.setMaximum(len(notes))
    val = 0
    for nid in notes:
        note = mw.col.get_note(nid)
        fields = note.fields
        if source in fields and dest in fields:
            text = note[source]
            newText = to_migaku(text, "cn", reading_type)
            note[dest] = applyOM(output_mode, note[dest], newText)
            mw.col.update_note(note)
        val += 1
        bar.setValue(val)
        mw.app.processEvents()
    mw.progress.finish()
    mw.reset()


def mass_remove_migaku_browser(source: str, notes: Sequence[NoteId], widget: QDialog):
    if not miAsk(
        f'WARNING\nAre you sure you want to mass remove readings from the "{source}" field?'
        'Please make sure you have selected the correct field as this will remove all "[" and "]" and text in between from a field.'
    ):
        return
    widget.close()
    bar = getProgressWidget()
    bar.setMinimum(0)
    bar.setMaximum(len(notes))
    val = 0
    for nid in notes:
        note = mw.col.get_note(nid)
        fields = note.fields
        if source in fields:
            text = note[source]
            text = strip_migaku(text)
            note[source] = text
            mw.col.update_note(note)
        val += 1
        bar.setValue(val)
        mw.app.processEvents()
    mw.progress.finish()
    mw.reset()


def browser_menu(browser: Browser):
    notes = browser.selectedNotes()

    if notes:
        fields = fieldNamesForNotes(mw.col, notes)
        generateWidget = QDialog(None, Qt.WindowType.Window)
        layout = QHBoxLayout()
        origin_label = QLabel("Origin:")
        source_cb = QComboBox()
        source_cb.addItems(fields)
        dest_label = QLabel("Destination:")
        dest_cb = QComboBox()
        dest_cb.addItems(fields)
        output_mode_label = QLabel("Output Mode:")
        output_mode_cb = QComboBox()
        output_mode_cb.addItems(["Add", "Overwrite", "If Empty"])
        reading_type_label = QLabel("Reading Type:")
        reading_type_cb = QComboBox()
        reading_type_cb.addItems(["Pinyin", "Bopomofo", "Jyutping"])
        add_button = QPushButton("Add Readings")
        add_button.clicked.connect(
            lambda: mass_generate_migaku_browser(
                source_cb.currentText(),
                dest_cb.currentText(),
                output_mode_cb.currentText(),
                reading_type_cb.currentText().lower(),
                notes,
                generateWidget,
            )
        )
        remove_button = QPushButton("Remove Readings")
        remove_button.clicked.connect(lambda: mass_remove_migaku_browser(source_cb.currentText(), notes, generateWidget))
        layout.addWidget(origin_label)
        layout.addWidget(source_cb)
        layout.addWidget(dest_label)
        layout.addWidget(dest_cb)
        layout.addWidget(output_mode_label)
        layout.addWidget(output_mode_cb)
        layout.addWidget(reading_type_label)
        layout.addWidget(reading_type_cb)
        layout.addWidget(add_button)
        layout.addWidget(remove_button)
        generateWidget.setWindowTitle("Generate Chinese Readings")
        generateWidget.setWindowIcon(QIcon(str(BASE_DIR / "icons" / "migaku.png")))
        generateWidget.setLayout(layout)
        generateWidget.exec()
    else:
        miInfo("Please select some cards before attempting to mass generate.")


def strip_migaku_editor(editor: Editor):
    id = editor.currentField
    selected_text = editor.note.fields[id]
    modified_text = strip_migaku(selected_text, "cn")
    editor.note.fields[id] = modified_text
    editor.loadNoteKeepingFocus()  # Refresh the editor


def add_my_button(buttons: list[str], editor: Editor):
    editor._links["generate_migaku_editor"] = lambda editor=editor: generate_migaku_editor(editor)
    editor._links["strip_migaku_editor"] = lambda editor=editor: strip_migaku_editor(editor)
    buttons.append(
        editor.addButton(
            icon=str(BASE_DIR / "icons" / "simpDu.svg"),  # Path to an icon if you have one
            cmd="to_migaku",
            func=editor._links["generate_migaku_editor"],
            tip="Generate pinyin in the Migaku format",  # Hover tooltip
            keys="f9",  # Shortcut (optional)
        )
    )
    buttons.append(
        editor.addButton(
            icon=str(BASE_DIR / "icons" / "simpShan.svg"),  # Path to an icon if you have one
            cmd="strip_migaku",
            func=editor._links["strip_migaku_editor"],
            tip="Strip the Migaku format from the text",  # Hover tooltip
            keys="f10",  # Shortcut (optional)
        )
    )
    return buttons


def setup_browser_menu(browser: Browser):
    a = QAction("Generate Chinese Readings", browser)
    a.triggered.connect(lambda: browser_menu(browser))
    menu_edit: QMenu = browser.form.menuEdit
    menu_edit.addSeparator()
    menu_edit.addAction(a)


gui_hooks.editor_did_init_buttons.append(add_my_button)
gui_hooks.browser_menus_did_init.append(setup_browser_menu)
