from .src import (
    add_browser_menu,
    add_editor_buttons,
    setup_menu,
)

from aqt import gui_hooks


setup_menu()
gui_hooks.browser_menus_did_init.append(add_browser_menu)
gui_hooks.editor_did_init_buttons.append(add_editor_buttons)
