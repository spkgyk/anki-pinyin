from .tokenizer import to_migaku, BASE_DIR

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki.hooks import addHook
from aqt.editor import Editor


def on_button_clicked(editor: Editor):
    id = editor.currentField
    selected_text = editor.note.fields[id]
    modified_text = to_migaku(selected_text, "cn")
    editor.note.fields[id] = modified_text
    editor.loadNoteKeepingFocus()  # Refresh the editor


def add_my_button(buttons, editor: Editor):
    editor._links["to_migaku"] = lambda editor=editor: on_button_clicked(editor)
    button = editor.addButton(
        icon=str(BASE_DIR / "icons/simpDu.svg"),  # Path to an icon if you have one
        cmd="to_migaku",
        func=lambda editor=editor: on_button_clicked(editor),
        tip="Generate pinyin in the Migaku format",  # Hover tooltip
        keys="f9",  # Shortcut (optional)
    )
    return buttons + [button]


addHook("setupEditorButtons", add_my_button)
