from .tokenizer import strip_display_format, gen_display_format
from .utils import ReadingType, DATA_DIR
from . import config

from aqt.editor import Editor


def editor_generate_readings(editor: Editor):
    current_field_id = editor.currentField
    if current_field_id is not None:
        selected_text = editor.note.fields[current_field_id]
        reading_type = ReadingType(config.get("ReadingType", ReadingType.PINYIN_TONES))
        editor.note.fields[current_field_id] = gen_display_format(selected_text, "cn", reading_type)
        editor.loadNoteKeepingFocus()


def editor_strip_readings(editor: Editor):
    current_field_id = editor.currentField
    if current_field_id is not None:
        selected_text = editor.note.fields[current_field_id]
        editor.note.fields[current_field_id] = strip_display_format(selected_text, "cn")
        editor.loadNoteKeepingFocus()


def add_editor_buttons(buttons: list[str], editor: Editor):
    du_icon = str(DATA_DIR / "icons" / "simpDu.svg")
    shan_icon = str(DATA_DIR / "icons" / "simpShan.svg")
    if config.get("traditionalIcons", False):
        du_icon = str(DATA_DIR / "icons" / "tradDu.svg")
        shan_icon = str(DATA_DIR / "icons" / "tradShan.svg")

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
