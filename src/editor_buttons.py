from . import (
    ReadingType,
    strip_display_format,
    gen_display_format,
    DATA_DIR,
)

from aqt.qt import *
from aqt.editor import Editor


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
            icon=str(DATA_DIR / "icons" / "simpDu.svg"),
            cmd="to_migaku",
            func=editor._links["editor_generate_readings"],
            tip="Generate pinyin in the Migaku format",
            keys="f9",
        )
    )
    buttons.append(
        editor.addButton(
            icon=str(DATA_DIR / "icons" / "simpShan.svg"),
            cmd="strip_migaku",
            func=editor._links["editor_strip_readings"],
            tip="Strip the Migaku format from the text",
            keys="f10",
        )
    )
    return buttons
