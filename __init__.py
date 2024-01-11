from .src import (
    setup_browser_menu,
    add_my_button,
)

from aqt import gui_hooks


gui_hooks.editor_did_init_buttons.append(add_my_button)
gui_hooks.browser_menus_did_init.append(setup_browser_menu)
