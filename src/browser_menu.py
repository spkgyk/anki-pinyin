from . import (
    ReadingType,
    strip_display_format,
    gen_display_format,
    DATA_DIR,
)

from aqt import mw
from aqt.qt import *
from typing import Sequence
from anki.notes import NoteId
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
    icon = QIcon(str(DATA_DIR / "icons" / "migaku.png"))
    message_box = QMessageBox(parent)
    if not day:
        message_box.setStyleSheet(" QMessageBox {background-color: #272828;}")
    message_box.setText(text)
    message_box.setWindowIcon(icon)
    message_box.setWindowTitle(title)
    button = message_box.addButton(QMessageBox.StandardButton.Ok)
    button.setFixedSize(100, 30)
    button.setDefault(True)

    return message_box.exec()


def yes_no_window(text, parent=None, day=True):
    message_box = QMessageBox(parent)
    message_box.setWindowTitle("Select")
    message_box.setText(text)
    icon = QIcon(str(DATA_DIR / "icons" / "migaku.png"))
    yes_button = message_box.addButton(QMessageBox.StandardButton.Yes)
    yes_button.setFixedSize(100, 30)
    yes_button.setDefault(True)
    no_button = message_box.addButton(QMessageBox.StandardButton.No)
    no_button.setFixedSize(100, 30)
    if not day:
        message_box.setStyleSheet(" QMessageBox {background-color: #272828;}")
    message_box.setWindowIcon(icon)
    message_box.exec()
    if message_box.clickedButton() == yes_button:
        return True
    else:
        return False


def get_progress_bar_widget(length: int):
    progress_widget = QWidget(None)
    progress_widget.setFixedSize(400, 70)
    progress_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress_widget.setWindowIcon(QIcon(str(DATA_DIR / "icons" / "migaku.png")))
    bar = QProgressBar(progress_widget)
    bar.setFixedSize(390, 50)
    bar.move(10, 10)
    bar_label = QLabel(bar)
    bar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    progress_widget.show()
    bar.setMinimum(0)
    bar.setMaximum(length)
    return progress_widget, bar


def apply_output_mode(addType: str, dest: str, text: str):
    if text:
        if addType == "If Empty":
            if dest == "":
                dest = text
        elif addType == "Append":
            if dest == "":
                dest = text
            else:
                dest += "<br>" + text
        else:
            dest = text
    return dest


def browser_mass_generate_readings(source: str, dest: str, output_mode: str, reading_type: str, notes: Sequence[NoteId], widget: QDialog):
    mw.checkpoint("Chinese Reading Generation")
    if not yes_no_window('Extract characters from the "' + source + '" field\nand use to generate readings in the "' + dest + '" field?'):
        return
    widget.close()
    progress_widget, bar = get_progress_bar_widget(len(notes))
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
    progress_widget, bar = get_progress_bar_widget(len(notes))
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
        source_label = QLabel("Source:")
        source_cb = QComboBox()
        source_cb.addItems(fields)
        dest_label = QLabel("Destination:")
        dest_cb = QComboBox()
        dest_cb.addItems(fields)
        output_mode_label = QLabel("Output Mode:")
        output_mode_cb = QComboBox()
        output_mode_cb.addItems(["Append", "Overwrite", "If Empty"])
        reading_type_label = QLabel("Reading Type:")
        reading_type_cb = QComboBox()
        reading_type_cb.addItems(["Pinyin", "Zhuyin", "Jyutping"])
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
        layout.addWidget(source_label)
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
        generateWidget.setWindowIcon(QIcon(str(DATA_DIR / "icons" / "migaku.png")))
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