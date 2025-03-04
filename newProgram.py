from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox
import numpy as np


class newProgram:
    def __init__(self):
        self.statements = []
        self.variables = []
    def addStatement(self, statement):
        print("adding statement", statement)
        self.statements.append(statement)
    def addVariable(self, variable):
        self.variables.append(variable)
    def __str__(self):
        return "\n".join([str(s) for s in self.statements])
    

class createProgramGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.program = newProgram()
    
    def initUI(self):
        layout = QVBoxLayout()
        add_button = QPushButton("Add statement")
        add_button.clicked.connect(self.addStatement)
        variable_list = QLabel("Variables:")
        self.variable_list = variable_list
        add_variable = QPushButton("Add variable")
        add_variable.clicked.connect(self.addVariable)
        layout.addWidget(add_button)
        layout.addWidget(add_variable)
        layout.addWidget(variable_list)
        self.setMinimumHeight(300)
        self.setMinimumWidth(200)
        self.setLayout(layout)
        self.currentDetail = None

    def addVariable(self):
        self.add_variable_window = QWidget()
        self.variable_layout = QVBoxLayout()
        label = QLabel("Variable name")
        self.variable_layout.addWidget(label)
        # input box
        input_box = QTextEdit()
        self.variable_layout.addWidget(input_box)
        self.variable_box = input_box
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submitVariable)
        self.variable_layout.addWidget(submit_button)
        # open new window
        self.add_variable_window.setLayout(self.variable_layout)
        self.add_variable_window.setMinimumHeight(300)
        self.add_variable_window.setMinimumWidth(200)
        self.add_variable_window.show()
    
    def addStatement(self):
        self.add_statement_window = QWidget()
        self.statement_layout = QVBoxLayout()
        label = QLabel("select type")
        self.statement_layout.addWidget(label)
        # selectbox
        selectbox = QComboBox()
        selectbox.addItem("unitary")
        selectbox.addItem("while")
        selectbox.addItem("assignment")
        selectbox.addItem("if")
        selectbox.currentIndexChanged.connect(self.selectionChange)
        self.selectbox = selectbox
        self.statement_layout.addWidget(selectbox)
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submitStatement)
        self.statement_layout.addWidget(submit_button)
        # open new window
        self.add_statement_window.setLayout(self.statement_layout)
        self.add_statement_window.setMinimumHeight(300)
        self.add_statement_window.setMinimumWidth(200)
        self.add_statement_window.show()
        
    def selectionChange(self):
        t = self.selectbox.currentText()
        print(t)
        if self.currentDetail:
            for wid in self.currentDetail:
                wid.hide()
        if t == "unitary":
            self.statement_layout.addWidget(QLabel("unitary matrix"))
            
    
    def submitStatement(self):
        t = self.selectbox.currentText()
        self.program.addStatement(t)
        self.add_statement_window.close()
    
    def submitVariable(self):
        variable = self.variable_box.toPlainText()
        self.program.addVariable(variable)
        self.add_variable_window.close()
        self.variable_list.setText("Variables: " + ",".join(self.program.variables))