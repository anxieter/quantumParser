from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
import numpy as np
from newProgram import newProgram, createProgramGUI, programContainer
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
        layout = QVBoxLayout()
        add_program_button = QPushButton("Add program")
        add_program_button.clicked.connect(self.addProgram)
        layout.addWidget(add_program_button)
        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.processProgram)
        layout.addWidget(calculate_button)
        self.setLayout(layout)

    def addProgram(self):
        self.mainProgram = programContainer()
        gui = createProgramGUI(self.mainProgram)
        self.newgui = gui
        gui.show()

    def processProgram(self):
        # program_text = self.textEdit.toPlainText()
        # result = parse_quantum_program(program_text)
        # self.resultText.setPlainText(result)
        pass
if __name__ == "__main__":
    app = QApplication([])
    pc = programContainer()
    gui = QuantumGUI()
    gui.show()
    app.exec()
