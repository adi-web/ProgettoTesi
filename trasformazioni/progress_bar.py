import os
import sys
from threading import Thread
import threading
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QProgressBar, QVBoxLayout, QApplication,QLabel

from trasformazioni.convert_csv_ply import convert_csv_ply
from trasformazioni.transform_coordinate import TransformCoordinates

from PyQt5.QtCore import *
from PyQt5.QtGui import *
 
class Progress_transform(QWidget):
    def __init__(self,open3d):
        super(Progress_transform, self).__init__()

        self.open3d=open3d

        #button per visualizzazione 3d
        self.btn_open3d=QPushButton("Visualize 3D simulation")
        self.btn_open3d.clicked.connect(self.call_open3d)
        self.btn_open3d.setVisible(False)

        self.title_label = QLabel("Coordinate Transformation", self)

        
        title_font = QFont("Arial", 24, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #333333;") 
        self.title_label.setAlignment(Qt.AlignCenter)  

        self.pbar = QProgressBar(self)
        self.pbar.setValue(0)
        self.resize(300, 100)
        self.vbox = QVBoxLayout()
    
        self.vbox.addWidget(self.title_label)
        self.vbox.addWidget(self.pbar)
        self.vbox.addWidget(self.btn_open3d)
        self.vbox.setAlignment(Qt.AlignCenter)
      
        self.i=0
        
        self.setLayout(self.vbox)
        
    def call_open3d(self):
        #viene mandato path dove leggere i file ply per visualizzazione 3d
        self.open3d.open3D_with_paht(os.path.join(os.getcwd(),self.basePath))  
        
    def fromController(self,pathBase):


        self.split = pathBase.split('/')
        #path dove verrano salvati i file ply
        self.basePath=self.pathCsvTrasformato= os.path.join(
            'raccolta_scenari', 
            self.split[len(self.split)-4], 
            self.split[len(self.split)-3], 
            "ply"
        )

        
        self.pathCsvTrasformato= os.path.join(
            'raccolta_scenari', 
            self.split[len(self.split)-4], 
            self.split[len(self.split)-3], 
            "blender",
            "csvtrasformato"
        )

        self.startThread(pathBase)
        
       
    def callFromtrajectory(self,path):
        #path da passare alla classe open3d per renderizzare i point cloud
        self.pathCsvTrasformato=os.path.join(path,"blender","csvTrasformato")
        self.basePath=os.path.join(path,"ply")

       
        self.startThread(path)

    def startThread(self,pathBase):
        #Thread che svolge la trasformazione in coordinate globali dei file csv
        self.thread = threading.Thread(target=self.start_transform(pathBase))
        
        #Thread che svolge trasformazione da csv a ply
        self.thread2=threading.Thread(target=self.start_convert(self.pathCsvTrasformato)
    )
        self.thread.start()
        self.thread.join()

    
        self.thread2.start()
        self.thread2.join()
        self.pbar.setValue(100)
        self.pbar.setVisible(False)
        self.title_label.setText("Tansformation completed")
        self.btn_open3d.setVisible(True)



    def start_convert(self,patht):
        convert_csv_ply(self,patht)
      
    def start_transform(self,pathBase):
        TransformCoordinates(self,pathBase)
        

    #funzione per aumentare il progress bar
    def signal_accept(self,i):
        
        self.i+=i
        self.pbar.setValue(int(self.i))

        if self.pbar.value() > 90:
            self.pbar.setVisible(False)
            self.title_label.setText("Tansformation completed")
            self.btn_open3d.setVisible(True)
    