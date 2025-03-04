from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
import numpy as np
from newProgram import newProgram, createProgramGUI
# 定义基本的量子操作矩阵
MATRICES = {
    "H": np.array([[1, 1], [1, -1]]) / np.sqrt(2),  # Hadamard 门
    "X": np.array([[0, 1], [1, 0]]),  # Pauli-X 门
    "Z": np.array([[1, 0], [0, -1]]),  # Pauli-Z 门
    "I": np.array([[1, 0], [0, 1]])  # 单位矩阵
}



class QuantumGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = createProgramGUI()
        self.setLayout(layout)

        # self.label = QLabel("输入量子程序:")
        # layout.addWidget(self.label)

        # self.textEdit = QTextEdit()
        # layout.addWidget(self.textEdit)

        # self.processButton = QPushButton("解析程序")
        # self.processButton.clicked.connect(self.processProgram)
        # layout.addWidget(self.processButton)

        # self.resultLabel = QLabel("解析结果:")
        # layout.addWidget(self.resultLabel)

        # self.resultText = QTextEdit()
        # self.resultText.setReadOnly(True)
        # layout.addWidget(self.resultText)

        # self.setLayout(layout)
        # self.setWindowTitle("量子程序解析器")

    def addStatement(self):
        pass        


    def processProgram(self):
        # program_text = self.textEdit.toPlainText()
        # result = parse_quantum_program(program_text)
        # self.resultText.setPlainText(result)
        pass
if __name__ == "__main__":
    app = QApplication([])
    gui = createProgramGUI()
    gui.show()
    app.exec()
