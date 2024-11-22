
from convert_csv_ply import convert_csv_ply
from view_trajectory import View_Trajectory
from progress_bar import Progress_transform
from startWindow import StartWindow
import sys
from PyQt5 import QtCore, QtWidgets

from readCsv import *


from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QEvent, QSize, Qt

from view3D import view3D


class MainWindow(QWidget):
    def __init__(self):

        super().__init__()


        self.stackedWidget = QStackedWidget()

        #pagina iniziale
        self.page1 = StartWindow()


        self.page2 = read_csv(self)
        self.page3=View_Trajectory()
        self.page4=view3D(self)


        self.page1.switch_window.connect(self.show_csv_choose)
        self.page1.open3d_window.connect(self.show_open_3d)
        self.page1.transform.connect(self.transformOpen)
        

        self.page5=Progress_transform(self)
        
    
        self.stackedWidget.addWidget(self.page1)
        self.stackedWidget.addWidget(self.page2)
        self.stackedWidget.addWidget(self.page3)
        self.stackedWidget.addWidget(self.page4)
        self.stackedWidget.addWidget(self.page5)

        # mostra la pagina iniziale
        self.stackedWidget.setCurrentIndex(0)
        #print(self.stackedWidget.setCurrentIndex(0))
        layout = QVBoxLayout()
        layout.addWidget(self.stackedWidget)

        self.setLayout(layout)

    

    def transformOpen(self):
        self.file_dialog = QFileDialog.Options()
        self.file_name = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=self.file_dialog)

        if self.file_name:
            print(f"Selected folder: {self.file_name}")
            self.stackedWidget.setCurrentIndex(4)
            self.page5.fromController(self.file_name)


    def show_start(self):
        self.start_window = StartWindow()
        self.start_window.switch_window.connect(self.show_csv_choose)
        self.start_window.show()

    def open3D_with_paht(self,path):
        self.stackedWidget.setCurrentIndex(3)
        self.page4.start(path)
        
    def show_open_3d(self):
        print("open3d")
        self.file_dialog = QFileDialog.Options()
        self.file_name = QFileDialog.getExistingDirectory(self, "Select Folder", "", options=self.file_dialog)
        if self.file_name:
            self.stackedWidget.setCurrentIndex(3)
            self.page4.start(self.file_name)
        

    def show_csv_choose(self):
        #self.choose_csv=read_csv()
        #self.start_window.hide()
        #self.choose_csv.switch_window.connect(self.show_trajectory)
        self.page2.switch_window.connect(self.show_trajectory)
        self.stackedWidget.setCurrentIndex(1)
        #self.choose_csv.show()

    def show_trajectory(self,trajectory_data):
        #self.trajectory=View_Trajectory()
        #self.choose_csv.hide()
        #self.trajectory.show()
        #self.trajectory.plot_trajectory(trajectory_data) 
        
        self.stackedWidget.setCurrentIndex(2)
        self.page3.plot_trajectory(trajectory_data,self,self.page5)

    


class Controller:

    def __init__(self):
        
        pass

    def show_start(self):
        self.start_window = StartWindow()
        self.start_window.switch_window.connect(self.show_csv_choose)
        self.start_window.show()

    def show_csv_choose(self):
        self.choose_csv=read_csv()
        self.start_window.hide()
        
        self.choose_csv.switch_window.connect(self.show_trajectory)
        self.choose_csv.show()

   


    def show_trajectory(self,trajectory_data):
        self.trajectory=View_Trajectory()
        #self.choose_csv.hide()
        self.trajectory.show()
        self.trajectory.plot_trajectory(trajectory_data)    


#main principale dell'applicazione
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(500,100,1200,800) # Set window size and position
    window.setWindowTitle('Blender Simulazioni')
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()