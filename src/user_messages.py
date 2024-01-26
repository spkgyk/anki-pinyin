from aqt import mw
from aqt.qt import QMessageBox, QWidget


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
    message_box = QMessageBox(parent)
    if not day:
        message_box.setStyleSheet(" QMessageBox {background-color: #272828;}")
    message_box.setText(text)
    message_box.setWindowTitle(title)
    button = message_box.addButton(QMessageBox.StandardButton.Ok)
    button.setFixedSize(100, 30)
    button.setDefault(True)

    return message_box.exec()


def yes_no_window(text: str, parent: QWidget = None, day: bool = True):
    message_box = QMessageBox(parent)
    message_box.setWindowTitle("Select")
    message_box.setText(text)
    yes_button = message_box.addButton(QMessageBox.StandardButton.Yes)
    yes_button.setFixedSize(100, 30)
    yes_button.setDefault(True)
    no_button = message_box.addButton(QMessageBox.StandardButton.No)
    no_button.setFixedSize(100, 30)
    if not day:
        message_box.setStyleSheet(" QMessageBox {background-color: #272828;}")
    message_box.exec()
    if message_box.clickedButton() == yes_button:
        return True
    else:
        return False
