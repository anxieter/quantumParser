from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
import numpy as np


class newProgram:
    def __init__(self):
        self.statements = []
    def addStatement(self, statement):
        self.statements.append(statement)
    def __str__(self):
        return "\n".join([str(s) for s in self.statements])

    

class createProgramGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI():
        
