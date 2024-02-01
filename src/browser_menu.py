import shutil

from aqt import mw
from aqt.qt import *
from pathlib import Path
from typing import Sequence
from anki.notes import NoteId
from aqt.browser import Browser
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import Config
from .tts import TTSDownloader
from .tokenizer import strip_display_format, gen_display_format
from .utils import ReadingType, OutputMode, apply_output_mode, AUDIO_DIR
from .user_messages import yes_no_window, info_window, get_progress_bar_widget


WORKERS = 8


class WorkerSignals(QObject):
    progress = pyqtSignal(int)


def update_progress_bar(bar: QProgressBar, value: int):
    bar.setValue(bar.value() + value)
    mw.app.processEvents()


def browser_mass_generate_readings(
    source: str,
    dest: str,
    output_mode: OutputMode,
    reading_type: ReadingType,
    notes: Sequence[NoteId],
    widget: QDialog,
):
    if not yes_no_window('Extract characters from the "' + source + '" field\nand use to generate readings in the "' + dest + '" field?'):
        return
    mw.checkpoint("Chinese Reading Generation")
    widget.close()
    progress_widget, bar = get_progress_bar_widget(len(notes))

    for i, nid in enumerate(notes):
        note = mw.col.get_note(nid)
        fields = note.keys()
        if source in fields and dest in fields:
            tokenization_result = gen_display_format(note[source], "cn", reading_type)
            note[dest] = apply_output_mode(output_mode, note[dest], tokenization_result.display_format)

            for field_name, content in note.items():
                if field_name not in [source, dest]:
                    if field_name in Config.simp_fields:
                        note[field_name] = apply_output_mode(Config.simp_fields[field_name], content, tokenization_result.simplified)
                    elif field_name in Config.trad_fields:
                        note[field_name] = apply_output_mode(Config.trad_fields[field_name], content, tokenization_result.traditional)
                    # elif field_name in Config.variant_fields:
                    #     note[field_name] = apply_output_mode(Config.variant_fields[field_name], content, tokenization_result.variant)

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


def process_notes(worker: int, nid_dicts: dict[NoteId, str], signals: WorkerSignals, media_dir: Path):
    will_process = {}
    if nid_dicts:
        downloader = TTSDownloader(worker, media_dir)
        for nid, selected_text in nid_dicts.items():
            audio_tag = downloader.tts_download(selected_text)
            will_process[nid] = audio_tag
            signals.progress.emit(1)
        downloader.close()
    return will_process


def browser_mass_generate_audio(source: str, dest: str, output_mode: OutputMode, notes: Sequence[NoteId], widget: QDialog):
    if not yes_no_window(
        f'Generate audio using the "{source}" field for the {len(notes)} selected notes and place it in the "{dest}" field?'
    ):
        return
    mw.checkpoint("Chinese Audio Generation")
    widget.close()

    progress_widget, bar = get_progress_bar_widget(len(notes) + 4)
    signals = WorkerSignals()
    signals.progress.connect(lambda value: update_progress_bar(bar, value))

    note_groups = [{} for _ in range(WORKERS)]
    for i, nid in enumerate(notes):
        note = mw.col.get_note(nid)
        if source in note.keys() and dest in note.keys():
            note_groups[i % WORKERS][nid] = strip_display_format(note[source], "cn")
    signals.progress.emit(1)

    shutil.rmtree(AUDIO_DIR, ignore_errors=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    signals.progress.emit(1)

    processed = {}
    media_dir = Path(mw.col.media.dir())

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        future_to_nid = {
            executor.submit(process_notes, worker, nid_dicts, signals, media_dir): nid_dicts for worker, nid_dicts in enumerate(note_groups)
        }

        for future in as_completed(future_to_nid):
            nids = future_to_nid[future]
            try:
                processed_nids = future.result()
                processed.update(processed_nids)
            except:
                pass

    for nid, text in processed.items():
        note = mw.col.get_note(nid)
        note[dest] = apply_output_mode(output_mode, note[dest], text)
        mw.col.update_note(note)

    signals.progress.emit(1)

    shutil.rmtree(AUDIO_DIR, ignore_errors=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)
    signals.progress.emit(1)

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
        output_mode_cb.setCurrentIndex(2)
        reading_type_label = QLabel("Reading Type:")
        reading_type_cb = QComboBox()
        reading_type_cb.addItems(sorted([t.value for t in ReadingType]))
        reading_type_cb.setCurrentIndex(2)
        add_button = QPushButton("Add Readings")
        add_button.clicked.connect(
            lambda: browser_mass_generate_readings(
                source_cb.currentText(),
                dest_cb.currentText(),
                OutputMode(output_mode_cb.currentText()),
                ReadingType(reading_type_cb.currentText()),
                notes,
                generateWidget,
            )
        )
        remove_button = QPushButton("Remove Readings")
        remove_button.clicked.connect(lambda: browser_mass_strip_readings(source_cb.currentText(), notes, generateWidget))
        generate_audio_button = QPushButton("Generate Audio")
        generate_audio_button.clicked.connect(
            lambda: browser_mass_generate_audio(
                source_cb.currentText(),
                dest_cb.currentText(),
                OutputMode(output_mode_cb.currentText()),
                notes,
                generateWidget,
            )
        )
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
        layout.addWidget(generate_audio_button)
        generateWidget.setWindowTitle("Generate Chinese Readings")
        generateWidget.setLayout(layout)
        generateWidget.exec()
    else:
        info_window("Please select some cards before attempting to mass generate.")


def add_browser_menu(browser: Browser):
    a = QAction("Generate Chinese Readings", browser)
    a.triggered.connect(lambda: browser_menu(browser))
    menu_edit: QMenu = browser.form.menuEdit
    menu_edit.addSeparator()
    menu_edit.addAction(a)
