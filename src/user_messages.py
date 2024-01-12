from . import DATA_DIR

from aqt import mw
from aqt.qt import QIcon, QMessageBox, QWidget


def info_window(text: str, parent: QWidget = None, level: str = "msg", day: bool = True):
    if level == "wrn":
        title = "Warning"
    elif level == "not":
        title = "Notice"
    elif level == "err":
        title = "Error"
    else:
        title = "Info"
    if parent is None:
        parent = mw.app.activeWindow() or mw
    icon = QIcon(str(DATA_DIR / "icons" / "migaku.png"))
    message_box = QMessageBox(parent)
    if not day:
        message_box.setStyleSheet(" QMessageBox {background-color: #272828;}")
    message_box.setText(text)
    message_box.setWindowIcon(icon)
    message_box.setWindowTitle(title)
    button = message_box.addButton(QMessageBox.StandardButton.Ok)
    button.setFixedSize(100, 30)
    button.setDefault(True)

    return message_box.exec()


def yes_no_window(text: str, parent: QWidget = None, day: bool = True):
    message_box = QMessageBox(parent)
    message_box.setWindowTitle("Select")
    message_box.setText(text)
    icon = QIcon(str(DATA_DIR / "icons" / "migaku.png"))
    yes_button = message_box.addButton(QMessageBox.StandardButton.Yes)
    yes_button.setFixedSize(100, 30)
    yes_button.setDefault(True)
    no_button = message_box.addButton(QMessageBox.StandardButton.No)
    no_button.setFixedSize(100, 30)
    if not day:
        message_box.setStyleSheet(" QMessageBox {background-color: #272828;}")
    message_box.setWindowIcon(icon)
    message_box.exec()
    if message_box.clickedButton() == yes_button:
        return True
    else:
        return False
