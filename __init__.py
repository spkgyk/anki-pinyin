from .tokenizer import (
    ReadingType,
    strip_display_format,
    gen_display_format,
    BASE_DIR,
)

from aqt import mw
from aqt.qt import *
from aqt import gui_hooks
from typing import Sequence
from aqt.editor import Editor
from anki.notes import NoteId
from aqt.utils import showInfo
from aqt.browser import Browser


def info_window(text, parent=False, level="msg", day=True):
    if level == "wrn":
        title = "Warning"
    elif level == "not":
        title = "Notice"
    elif level == "err":
        title = "Error"
    else:
        title = "Info"
    if parent is False:
        parent = mw.app.activeWindow() or mw
    icon = QIcon(str(BASE_DIR / "icons" / "migaku.png"))
    mb = QMessageBox(parent)
    if not day:
        mb.setStyleSheet(" QMessageBox {background-color: #272828;}")
    mb.setText(text)
    mb.setWindowIcon(icon)
    mb.setWindowTitle(title)
    b = mb.addButton(QMessageBox.StandardButton.Ok)
    b.setFixedSize(100, 30)
    b.setDefault(True)

    return mb.exec()


def yes_no_window(text, parent=None, day=True):
    msg = QMessageBox(parent)
    msg.setWindowTitle("Select")
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


def get_progress_bar_widget(length: int):
    progressWidget = QWidget(None)
    progressWidget.setFixedSize(400, 70)
    progressWidget.setWindowModality(Qt.WindowModality.ApplicationModal)
    progressWidget.setWindowIcon(QIcon(str(BASE_DIR / "icons" / "migaku.png")))
    bar = QProgressBar(progressWidget)
    bar.setFixedSize(390, 50)
    bar.move(10, 10)
    per = QLabel(bar)
    per.setAlignment(Qt.AlignmentFlag.AlignCenter)
    progressWidget.show()
    bar.setMinimum(0)
    bar.setMaximum(length)
    return progressWidget, bar


def apply_output_mode(addType: str, dest: str, text: str):
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


def browser_mass_generate_readings(source: str, dest: str, output_mode: str, reading_type: str, notes: Sequence[NoteId], widget: QDialog):
    mw.checkpoint("Chinese Reading Generation")
    if not yes_no_window('Extract characters from the "' + source + '" field and use to generate readings in the "' + dest + '" field?'):
        return
    widget.close()
    progressWidget, bar = get_progress_bar_widget(len(notes))
    for i, nid in enumerate(notes):
        note = mw.col.get_note(nid)
        fields = mw.col.models.field_names(note.note_type())
        if source in fields and dest in fields:
            newText = gen_display_format(note[source], "cn", ReadingType(reading_type))
            note[dest] = apply_output_mode(output_mode, note[dest], newText)
            mw.col.update_note(note)
        bar.setValue(i)
        mw.app.processEvents()
    mw.progress.finish()


def browser_mass_strip_readings(source: str, notes: Sequence[NoteId], widget: QDialog):
    if not yes_no_window(
        f'Remove all readings from the "{source}" field from the {len(notes)} selected notes?\n\n'
        'Note: this action will remove all square brackets and the text beween ("ASDF[...]" -> "ASDF").'
    ):
        return
    widget.close()
    progressWidget, bar = get_progress_bar_widget(len(notes))
    for i, nid in enumerate(notes):
        note = mw.col.get_note(nid)
        fields = mw.col.models.field_names(note.note_type())
        if source in fields:
            note[source] = strip_display_format(note[source], "cn")
            mw.col.update_note(note)
        bar.setValue(i)
        mw.app.processEvents()
    mw.progress.finish()


def browser_menu(browser: Browser):
    notes = browser.selected_notes()

    if notes:
        fields = mw.col.field_names_for_note_ids(notes)
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
            lambda: browser_mass_generate_readings(
                source_cb.currentText(),
                dest_cb.currentText(),
                output_mode_cb.currentText(),
                reading_type_cb.currentText(),
                notes,
                generateWidget,
            )
        )
        remove_button = QPushButton("Remove Readings")
        remove_button.clicked.connect(lambda: browser_mass_strip_readings(source_cb.currentText(), notes, generateWidget))
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
        info_window("Please select some cards before attempting to mass generate.")


def setup_browser_menu(browser: Browser):
    a = QAction("Generate Chinese Readings", browser)
    a.triggered.connect(lambda: browser_menu(browser))
    menu_edit: QMenu = browser.form.menuEdit
    menu_edit.addSeparator()
    menu_edit.addAction(a)


def editor_generate_readings(editor: Editor):
    id = editor.currentField
    selected_text = editor.note.fields[id]
    modified_text = gen_display_format(selected_text, "cn", ReadingType.PINYIN)
    editor.note.fields[id] = modified_text
    editor.loadNoteKeepingFocus()  # Refresh the editor


def editor_strip_readings(editor: Editor):
    id = editor.currentField
    selected_text = editor.note.fields[id]
    modified_text = strip_display_format(selected_text, "cn")
    editor.note.fields[id] = modified_text
    editor.loadNoteKeepingFocus()  # Refresh the editor


def add_my_button(buttons: list[str], editor: Editor):
    editor._links["editor_generate_readings"] = lambda editor=editor: editor_generate_readings(editor)
    editor._links["editor_strip_readings"] = lambda editor=editor: editor_strip_readings(editor)
    buttons.append(
        editor.addButton(
            icon=str(BASE_DIR / "icons" / "simpDu.svg"),
            cmd="to_migaku",
            func=editor._links["editor_generate_readings"],
            tip="Generate pinyin in the Migaku format",
            keys="f9",
        )
    )
    buttons.append(
        editor.addButton(
            icon=str(BASE_DIR / "icons" / "simpShan.svg"),
            cmd="strip_migaku",
            func=editor._links["editor_strip_readings"],
            tip="Strip the Migaku format from the text",
            keys="f10",
        )
    )
    return buttons


gui_hooks.editor_did_init_buttons.append(add_my_button)
gui_hooks.browser_menus_did_init.append(setup_browser_menu)
