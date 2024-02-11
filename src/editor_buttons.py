import os
import shutil

from aqt import mw
from pathlib import Path
from aqt.editor import Editor

from .config import Config
from .tts import TTSDownloader
from .utils import apply_output_mode, ICON_DIR, AUDIO_DIR
from .tokenizer import strip_display_format, gen_display_format


def editor_generate_readings(editor: Editor):
    current_field_id = editor.currentField
    if current_field_id is not None:
        selected_text = editor.note.fields[current_field_id]
        tokenization_result = gen_display_format(selected_text, "cn", Config.reading_type)

        for i, (field_name, content) in enumerate(editor.note.items()):
            if i == current_field_id:
                editor.note.fields[i] = tokenization_result.display_format
            elif field_name in Config.simp_fields:
                editor.note[field_name] = apply_output_mode(Config.simp_fields[field_name], content, tokenization_result.simplified)
            elif field_name in Config.trad_fields:
                editor.note[field_name] = apply_output_mode(Config.trad_fields[field_name], content, tokenization_result.traditional)
            # elif field_name in Config.variant_fields:
            #     editor.note[field_name] = apply_output_mode(Config.variant_fields[field_name], content, tokenization_result.variant)

        editor.loadNoteKeepingFocus()


def editor_strip_readings(editor: Editor):
    current_field_id = editor.currentField
    if current_field_id is not None:
        selected_text = editor.note.fields[current_field_id]
        editor.note.fields[current_field_id] = strip_display_format(selected_text, "cn")
        editor.loadNoteKeepingFocus()


def editor_generate_audio(editor: Editor):
    current_field_id = editor.currentField
    if current_field_id is not None:
        mw.downloader = TTSDownloader("no_worker", Path(mw.col.media.dir()))
        selected_text = strip_display_format(editor.note.fields[current_field_id], "cn")
        filename = mw.downloader.tts_download(selected_text, True)

        for field_name in editor.note.keys():
            if field_name in Config.audio_fields:
                editor.note[field_name] = apply_output_mode(Config.audio_fields[field_name], editor.note.fields[current_field_id], filename)

        shutil.rmtree(AUDIO_DIR, ignore_errors=True)
        os.makedirs(AUDIO_DIR, exist_ok=True)

        editor.loadNoteKeepingFocus()


def add_editor_buttons(buttons: list[str], editor: Editor):
    du_icon = str(ICON_DIR / "simpDu.svg")
    shan_icon = str(ICON_DIR / "simpShan.svg")
    if Config.traditional_icons:
        du_icon = str(ICON_DIR / "tradDu.svg")
        shan_icon = str(ICON_DIR / "tradShan.svg")
    audio_icon = str(ICON_DIR / "audio.svg")

    buttons.append(
        editor.addButton(
            icon=du_icon,
            cmd="editor_generate_readings",
            func=lambda editor=editor: editor_generate_readings(editor),
            tip="Generate pinyin for the selected field",
            keys="f9",
        )
    )
    buttons.append(
        editor.addButton(
            icon=shan_icon,
            cmd="editor_strip_readings",
            func=lambda editor=editor: editor_strip_readings(editor),
            tip="Strip readings from the selected field",
            keys="f10",
        )
    )
    buttons.append(
        editor.addButton(
            icon=audio_icon,
            cmd="editor_generate_audio",
            func=lambda editor=editor: editor_generate_audio(editor),
            tip="Generate audio for the selected field",
            keys="",
        )
    )
