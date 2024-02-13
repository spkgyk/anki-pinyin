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


class ProgressBarWidget(QWidget):
    cancel_signal = pyqtSignal()

    def __init__(self, length: int, cancel_button: bool = False):
        super().__init__(None)
        # Set fixed size and modality of the widget
        self.setMinimumWidth(400)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create and set layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create and configure the progress bar
        self.bar = QProgressBar()
        self.bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.bar.setMinimumHeight(10)
        self.bar.setMinimum(0)
        self.bar.setMaximum(length)
        self.set_value(0)

        layout.addWidget(self.bar)

        # Create the cancel button
        if cancel_button:
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self.on_cancel)
            layout.addWidget(self.cancel_button)

        # Show the widget
        self.show()

    def cancel_connect(self, fn: Callable):
        self.cancel_signal.connect(fn)

    def set_value(self, value: int):
        self.bar.setValue(value)
        mw.app.processEvents()

    def increment_value(self, value: int):
        self.set_value(self.bar.value() + value)

    def on_cancel(self):
        self.cancel_signal.emit()
        self.close()
