from aqt.editor import Editor

from .config import Config
from .utils import apply_output_mode, DATA_DIR
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


def add_editor_buttons(buttons: list[str], editor: Editor):
    du_icon = str(DATA_DIR / "icons" / "simpDu.svg")
    shan_icon = str(DATA_DIR / "icons" / "simpShan.svg")
    if Config.traditional_icons:
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
