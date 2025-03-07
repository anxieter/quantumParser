from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox
import numpy as np
from messages import errorMessage
from statement import *
from typing import List
class programContainer:
    def __init__(self):
        self.program = None
        
    
class newProgram:
    def __init__(self):
        self.n = 0
        self.statements: List[statement]= []
        self.variables: List[var] = []
    def addStatement(self, statement:statement):
        print("adding statement", statement)
        self.statements.append(statement)
    def addVariable(self, variable):
        self.variables.append(var(variable))
    def setN(self, n):
        self.n = n
    def __str__(self):
        return "\n".join([str(s) for s in self.statements])
    

class createProgramGUI(QWidget):
    def __init__(self, pc: programContainer):
        super().__init__()
        self.initUI()
        self.program = newProgram()
        self.n = 0
        self.pc = pc
    
    def refresh(self):
        self.variable_list.setText("Variables: " + ",".join([str(v) for v in self.program.variables]))
        self.bits_box.setText(str(self.n))
    
    def initUI(self):
        layout = QVBoxLayout()
        label = QLabel("Qubits count")
        layout.addWidget(label)
        # input box
        input_box = QTextEdit("0")
        input_box.setMaximumHeight(30)
        layout.addWidget(input_box)
        self.bits_box = input_box
        set_bits_button = QPushButton("Set qubits count")
        set_bits_button.clicked.connect(self.setBits)
        add_button = QPushButton("Add statement")
        add_button.clicked.connect(self.addStatement)
        variable_list = QLabel("Variables:")
        self.variable_list = variable_list
        add_variable = QPushButton("Add variable")
        add_variable.clicked.connect(self.addVariable)
        layout.addWidget(set_bits_button)
        layout.addWidget(add_variable)
        layout.addWidget(variable_list)
        layout.addWidget(add_button)
        self.setMinimumHeight(300)
        self.setMinimumWidth(200)
        self.setLayout(layout)
        self.currentDetail = None
        confirm_button = QPushButton("Confirm")
        confirm_button.clicked.connect(self.confirm)
        layout.addWidget(confirm_button)
        
    def setBits(self):
        self.n = int(self.bits_box.toPlainText())
        self.program.setN(self.n)
        print("Qubits count set to", self.n)

    def addVariable(self):
        self.add_variable_window = QWidget()
        self.variable_layout = QVBoxLayout()
        label = QLabel("Variable name")
        self.variable_layout.addWidget(label)
        # input box
        input_box = QTextEdit()
        input_box.setMaximumHeight(30)
        self.variable_layout.addWidget(input_box)
        self.variable_box = input_box
        label2 = QLabel("Variable tuple of qubits(eg. 0,1,2)")
        self.variable_layout.addWidget(label2)
        input_box2 = QTextEdit()
        input_box2.setMaximumHeight(30)
        self.variable_layout.addWidget(input_box2)
        self.variable_tuple = input_box2
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submitVariable)
        self.variable_layout.addWidget(submit_button)
        # open new window
        self.add_variable_window.setLayout(self.variable_layout)
        self.add_variable_window.setMinimumHeight(300)
        self.add_variable_window.setMinimumWidth(200)
        self.add_variable_window.show()
    
    def addStatement(self):
        if not self.n:
            errorMessage("Set qubits count first")
            return
        self.add_statement_window = QWidget()
        self.statement_layout = QVBoxLayout()
        label = QLabel("select type")
        self.statement_layout.addWidget(label)
        # selectbox
        selectbox = QComboBox()
        selectbox.addItem("skip")
        selectbox.addItem("unitary")
        selectbox.addItem("while")
        selectbox.addItem("assignment")
        selectbox.addItem("if")
        selectbox.currentIndexChanged.connect(self.selectionChange)
        self.selectbox = selectbox
        self.statement_layout.addWidget(selectbox)
        submit_button = QPushButton("Submit")
        submit_button.clicked.connect(self.submitStatement)
        detail_layout = QVBoxLayout()
        self.currentDetail = detail_layout
        self.statement_layout.addLayout(detail_layout)
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
            for i in reversed(range(self.currentDetail.count())):
                self.currentDetail.itemAt(i).widget().setParent(None) # remove all widgets
        if t == "unitary": # p = Up
            self.currentDetail.addWidget(QLabel("variable to be transformed"))
            var_box = QComboBox()
            var_box.setMaximumHeight(30)
            for v in self.program.variables:
                var_box.addItem(str(v[0]))
            self.currentDetail.addWidget(var_box)
            self.unitary_var_box = var_box
            label = QLabel("unitary matrix(0,1,1,0 for example for 1 qubit flip)")
            self.currentDetail.addWidget(label)
            input_box = QTextEdit()
            input_box.setMaximumHeight(60)
            self.currentDetail.addWidget(input_box)
            self.unitary_box = input_box
            
        elif t == "while": # while M[q] = 1 do S od
            qubit_label = QLabel("qubit to measure")
            self.currentDetail.addWidget(qubit_label)
            qubit_box = QComboBox()
            qubit_box.setMaximumHeight(30)
            for v in self.program.variables:
                qubit_box.addItem(str(v[0]))
            self.currentDetail.addWidget(qubit_box)
            self.while_qubit_box = qubit_box
            label = QLabel("measurement for while loop continuation(a matrix)")
            self.currentDetail.addWidget(label)
            input_box = QTextEdit()
            input_box.setMaximumHeight(60)
            self.currentDetail.addWidget(input_box)
            self.while_box = input_box
            add_program_button = QPushButton("Add loop body")
            self.while_pc = programContainer()
            add_program_button.clicked.connect(self.getWhileBody)
            self.currentDetail.addWidget(add_program_button)
            
        elif t == "if":
            qubit_label = QLabel("qubit to measure")
            self.currentDetail.addWidget(qubit_label)
            qubit_box = QComboBox()
            qubit_box.setMaximumHeight(30)
            for v in self.program.variables:
                qubit_box.addItem(str(v[0]))
            self.currentDetail.addWidget(qubit_box)
            self.if_qubit_box = qubit_box
            label = QLabel("measurement for if condition(a matrix)")
            self.currentDetail.addWidget(label)
            input_box = QTextEdit()
            input_box.setMaximumHeight(60)
            self.currentDetail.addWidget(input_box)
            self.if_box = input_box
            self.if_pc = programContainer()
            self.else_pc = programContainer()
            add_program_button = QPushButton("Add if body")
            add_program_button.clicked.connect(getNewProgram(self, self.if_pc))
            add_program_button2 = QPushButton("Add else body")
            add_program_button2.clicked.connect(getNewProgram(self, self.else_pc))
            self.currentDetail.addWidget(add_program_button)
            self.currentDetail.addWidget(add_program_button2)
            
        elif t == "assignment":
            label = QLabel("variable to be assigned to 0")
            self.currentDetail.addWidget(label)
            var_box = QComboBox()
            var_box.setMaximumHeight(30)
            for v in self.program.variables:
                var_box.addItem(str(v[0]))
            self.currentDetail.addWidget(var_box)
            self.assignment_box = var_box
            
    
    def getWhileBody(self):
        self.while_pc = programContainer()
        getNewProgram(self, self.while_pc)
    
    def submitStatement(self):
        t = self.selectbox.currentText()
        if t == "unitary":
            n = self.n
            p = self.program.variables[self.unitary_var_box.currentIndex()]
            U = np.array([int(i) for i in self.unitary_box.toPlainText().split(",")]).reshape((n,n))
            self.program.addStatement(unitaryTransform(n, p, U))
        if t == "while":
            n = self.n
            M = np.array([int(i) for i in self.while_box.toPlainText().split(",")]).reshape((2**n, 2**n))
            q = self.program.variables[self.while_qubit_box.currentIndex()]
            S = self.while_pc.program
            self.program.addStatement(whileStatement(n, M, q, S))
        if t == "if":
            n = self.n
            M = np.array([int(i) for i in self.if_box.toPlainText().split(",")]).reshape((2**n, 2**n))
            q = self.program.variables[self.if_qubit_box.currentIndex()]
            S = self.if_pc.program
            E = self.else_pc.program
            self.program.addStatement(ifStatement(n, M, q, S, E))
        if t == "assignment":
            n = self.n
            p = self.program.variables[self.assignment_box.currentIndex()]
            self.program.addStatement(assignment(n, p, U))
            
        self.add_statement_window.close()
    
    def submitVariable(self):
        variable = self.variable_box.toPlainText()
        variable_tuple = self.variable_tuple.toPlainText()
        try:
            indices = [int(i) for i in variable_tuple.split(",")]
        except:
            errorMessage("Invalid variable tuple")
            return
        max_index = max(indices)
        if max_index >= self.n:
            errorMessage("Invalid qubit index")
            return
        variable = (variable, indices)
        self.program.addVariable(variable)
        self.add_variable_window.close()
        self.variable_list.setText("Variables: " + ",".join([str(v) for v in self.program.variables]))
        
    def confirm(self):
        print("Confirming program")
        print(self.program)
        self.pc.program = self.program


def getNewProgram(old_pg:createProgramGUI, pc:programContainer):
    gui = createProgramGUI(pc)
    gui.n = old_pg.n
    gui.program.variables = old_pg.program.variables
    gui.refresh()
    old_pg.new_gui = gui
    gui.show()
    