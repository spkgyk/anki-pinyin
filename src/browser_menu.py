from .utils import ReadingType, OutputMode, ICON_DIR
from .user_messages import yes_no_window, info_window
from .tokenizer import strip_display_format, gen_display_format

from aqt import mw
from typing import Sequence
from anki.notes import NoteId
from aqt.browser import Browser
from aqt.qt import QWidget, Qt, QIcon, QProgressBar, QLabel, QDialog, QHBoxLayout, QComboBox, QPushButton, QAction, QMenu


def get_progress_bar_widget(length: int):
    progress_widget = QWidget(None)
    progress_widget.setFixedSize(400, 70)
    progress_widget.setWindowModality(Qt.WindowModality.ApplicationModal)
    progress_widget.setWindowIcon(QIcon(str(ICON_DIR / "migaku.png")))
    bar = QProgressBar(progress_widget)
    bar.setFixedSize(390, 50)
    bar.move(10, 10)
    bar_label = QLabel(bar)
    bar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    progress_widget.show()
    bar.setMinimum(0)
    bar.setMaximum(length)
    return progress_widget, bar


def apply_output_mode(output_mode: OutputMode, dest: str, text: str):
    if text:
        if output_mode == OutputMode.IF_EMPTY:
            if dest == "":
                dest = text
        elif output_mode == OutputMode.APPEND:
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
            note[dest] = apply_output_mode(OutputMode(output_mode), note[dest], newText)
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
        output_mode_cb.addItems(sorted([m.value for m in OutputMode]))
        reading_type_label = QLabel("Reading Type:")
        reading_type_cb = QComboBox()
        reading_type_cb.addItems(sorted([t.value for t in ReadingType]))
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
        generateWidget.setWindowIcon(QIcon(str(ICON_DIR / "migaku.png")))
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
