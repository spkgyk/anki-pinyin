from aqt.utils import showInfo
from aqt.editor import Editor
from .tokenizer import to_migaku


def onHotkeyPressed(editor: Editor):
    currentField = editor.currentField
    if currentField is not None:
        original_text = editor.note.fields[currentField]
        editor.note.fields[currentField] = to_migaku(original_text)
        editor.loadNote()
    else:
        showInfo("No field selected")


def setupEditorButtonsFilter(editor: Editor, buttons, *args):
    showInfo("myHotkeyButton added")
    editor.addButton("myHotkeyButton", lambda editor=editor: onHotkeyPressed(editor), "F10", tip="Activate my_func (F10)", keys="F10")
    return buttons


def addHook(editor: Editor):
    editor._links["myHotkeyButton"] = onHotkeyPressed


# Hook into the editor
from aqt.gui_hooks import editor_did_init_shortcuts, editor_did_init_buttons

editor_did_init_shortcuts.append(addHook)
editor_did_init_buttons.append(setupEditorButtonsFilter)
