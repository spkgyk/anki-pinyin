from aqt import mw
from aqt.qt import *


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


def get_progress_bar_widget(length: int):
    progress_widget = QWidget()
    progress_widget.setFixedSize(400, 50)
    progress_widget.setWindowModality(Qt.WindowModality.ApplicationModal)

    layout = QVBoxLayout()
    progress_widget.setLayout(layout)

    bar = QProgressBar()
    bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    bar.setFixedHeight(30)
    bar.setMinimum(0)
    bar.setMaximum(length)

    bar_label = QLabel()
    bar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    bar_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    bar_label.setFixedHeight(20)

    layout.addWidget(bar)
    layout.addWidget(bar_label)

    progress_widget.show()

    return progress_widget, bar
