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


def generate_migaku_editor(editor: Editor):
    id = editor.currentField
    selected_text = editor.note.fields[id]
    modified_text = to_migaku(selected_text, "cn")
    editor.note.fields[id] = modified_text
    editor.loadNoteKeepingFocus()  # Refresh the editor


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
            icon=str(BASE_DIR / "icons/simpDu.svg"),  # Path to an icon if you have one
            cmd="to_migaku",
            func=editor._links["generate_migaku_editor"],
            tip="Generate pinyin in the Migaku format",  # Hover tooltip
            keys="f9",  # Shortcut (optional)
        )
    )
    buttons.append(
        editor.addButton(
            icon=str(BASE_DIR / "icons/simpShan.svg"),  # Path to an icon if you have one
            cmd="strip_migaku",
            func=editor._links["strip_migaku_editor"],
            tip="Strip the Migaku format from the text",  # Hover tooltip
            keys="f10",  # Shortcut (optional)
        )
    )
    return buttons


gui_hooks.editor_did_init_buttons.append(add_my_button)
