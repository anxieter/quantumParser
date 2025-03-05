from PyQt6.QtWidgets import QWidget, QMessageBox


class errorMessage(QWidget):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.initUI()
        
    def initUI(self):
        msg_box = QMessageBox()
        msg_box.setText(self.message)
        msg_box.setInformativeText("please try again")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()