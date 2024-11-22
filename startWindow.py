import sys
from PyQt5 import QtCore, QtWidgets
from readCsv import *



class StartWindow(QtWidgets.QWidget):

    switch_window=QtCore.pyqtSignal()
    open3d_window=QtCore.pyqtSignal()
    transform=QtCore.pyqtSignal()

    def __init__(self):
        
        QtWidgets.QWidget.__init__(self)
        self.setGeometry(700,300,600,400)
        self.setWindowTitle('Blender Simulation')
        
        layout = QVBoxLayout()

        self.button = QtWidgets.QPushButton('Create simulation')
        
        self.button.setFixedWidth(1000)
       

        self.widgetOrizontal=QHBoxLayout()

        self.button.clicked.connect(self.choose_csv)
        self.button.setStyleSheet("background-color:blue;border-style: solid;width:20px;height:30px;color:white")

        self.open3D=QPushButton("Visualize 3D simulation")
        self.open3D.setStyleSheet("background-color:blue;border-style: solid;width:10px;height:30px;color:white")
        self.open3D.setFixedWidth(600)
        self.open3D.clicked.connect(self.opened_open)
        self.widgetOrizontal.addWidget(self.open3D,alignment=QtCore.Qt.AlignCenter)
        

        self.transofrm=QPushButton("Transform coordinates")
        self.transofrm.setStyleSheet("background-color:blue;border-style: solid;width:10px;height:30px;color:white")
        self.transofrm.setFixedWidth(600)
        self.transofrm.clicked.connect(self.transform_open)
        self.widgetOrizontal.addWidget(self.transofrm,alignment=QtCore.Qt.AlignCenter)

        centralLayout = QtWidgets.QHBoxLayout()
        centralLayout.addWidget(self.button, alignment=QtCore.Qt.AlignCenter)
        layout.addLayout(centralLayout)
        layout.addLayout(self.widgetOrizontal)


        self.setLayout(layout)

    def transform_open(self):
        self.transform.emit()    
    def choose_csv(self):
        
        self.switch_window.emit()

    def opened_open(self):
        self.open3d_window.emit()    




