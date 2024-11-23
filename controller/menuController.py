
import os
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt, transforms
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import PolyCollection
import numpy as np
import matplotlib.image as mpimg
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from sensor_trajectory_3d.sensorDispaly import Sensor_controller, Setting_Sensor



#classe che rappresenta le funzionalità per il sensore e veicoli come aggiungere ecc
class initial_tool(QMainWindow):
    def __init__(self,view_trajectory, *args, **kwargs):
        super().__init__(*args, **kwargs) 



        self.view_trajectory = view_trajectory
        self.sensorController=Sensor_controller(self,view_trajectory)
        self.tabwidget = QTabWidget()
        self.setCentralWidget(self.tabwidget)

        #lista che divide funzionalità sensori e veicolo
        self.list_widget={"sensor":[],"vehicles":[]}
        
        # permette di sceglier un file sensori e importare sensori
        #sensor_icon=QAction(QIcon('./assets/addfile.png'), '&New', self)
        #sensor_icon.setIconText("Import Sensor")
        #sensor_icon.triggered.connect( self.sensorController.sensor_import)
        #self.list_widget["sensor"].append(sensor_icon)

        self.new_sensorIcon=QAction(QIcon('./assets/add.png'), '&addSensor', self)
        self.new_sensorIcon.setIconText("Add new sensor")
        self.new_sensorIcon.setCheckable(True)  
        self.new_sensorIcon.setChecked(False)
        self.list_widget["sensor"].append(self.new_sensorIcon)
        
      

        self.modify_sensorIcon=QAction(QIcon('./assets/move.png'), '&start', self)
        self.modify_sensorIcon.setIconText("Move Sensor")
        self.modify_sensorIcon.setCheckable(True)  
        self.modify_sensorIcon.setChecked(False)
        self.list_widget["sensor"].append(self.modify_sensorIcon)


        self.rotate_sensorIcon=QAction(QIcon('./assets/rotation.png'), '&start', self)
        self.rotate_sensorIcon.setCheckable(True)  
        self.rotate_sensorIcon.setChecked(False)
        self.list_widget["sensor"].append( self.rotate_sensorIcon)

        self.remove_sensor=QAction(QIcon('./assets/remove.png'), '&delete sensor', self)
        self.remove_sensor.setCheckable(True)  
        self.remove_sensor.setChecked(False)
        self.list_widget["sensor"].append( self.remove_sensor)

        self.setting_icon=QAction(QIcon('./assets/setting.png'), '&sensor', self)
        self.setting_icon.setCheckable(True)  
        self.setting_icon.setChecked(False)
        self.setting_icon.triggered.connect(self.view_trajectory.show_scroll)
        self.list_widget["sensor"].append( self.setting_icon)


        self.vehicle_list=[]

        # permette di importare veicoli nelle traiettorie
        #self.import_vehicle=QAction(QIcon('./assets/addfile.png'), '&importVehicle', self)
        #self.import_vehicle.setIconText("import vehicle")
        #self.import_vehicle.triggered.connect(lambda: self.view_trajectory.vehicle_controller(self.import_vehicle))
        #self.import_vehicle.setCheckable(True)  # 
        #self.import_vehicle.setChecked(False)
        #self.list_widget["vehicles"].append(self.import_vehicle)
        #self.vehicle_list.append(self.import_vehicle)

        self.veicle_icon=QAction(QIcon('./assets/vehicle.png'), 'vehicle', self)
        self.veicle_icon.setIconText("Set veicle")
        self.veicle_icon.triggered.connect(lambda: self.view_trajectory.vehicle_controller(self.veicle_icon))
        self.veicle_icon.setCheckable(True) 
        self.veicle_icon.setChecked(False)
        self.list_widget["vehicles"].append(self.veicle_icon)


        self.bus_icon=QAction(QIcon('./assets/bus.png'), 'bus', self)
        self.bus_icon.setIconText("Set veicle")
        self.bus_icon.triggered.connect(lambda: self.view_trajectory.vehicle_controller(self.bus_icon))
        self.list_widget["vehicles"].append(self.bus_icon)
        self.bus_icon.setCheckable(True)  
        self.bus_icon.setChecked(False)
        self.vehicle_list.append(self.bus_icon)

        self.moto=QAction(QIcon('./assets/motorcycle.png'), 'motorcycle', self)
        self.moto.setIconText("Set veicle")
        self.moto.triggered.connect(lambda: self.view_trajectory.vehicle_controller(self.moto))
        self.list_widget["vehicles"].append(self.moto)
        self.moto.setCheckable(True)  
        self.moto.setChecked(False)
        self.vehicle_list.append(self.moto)

        self.remove_vehicle=QAction(QIcon('./assets/remove.png'), '&delete vehicle', self)
        self.remove_vehicle.setCheckable(True) 
        self.remove_vehicle.setChecked(False)
        self.list_widget["vehicles"].append( self.remove_vehicle)


        self.start_simulation=QAction(QIcon('./assets/start.png'), '&start', self)
        self.start_simulation.setIconText("Start Simulation")
        self.start_simulation.triggered.connect(lambda: self.view_trajectory.start_simulation())
        
        
       
        #per creare le icome
        for name in ("sensor", "vehicles"):
            self.create_widgets(name,self.list_widget)
  
   
    def prova(self):
    
        setting_sensor2=Setting_Sensor()
        self.view_trajectory.setting_sensor.addWidget(setting_sensor2)
        self.view_trajectory.update_window()


    #crea un widget  
    def create_widgets(self, name,list_widget):


        w = QMainWindow()
        self.tabwidget.addTab(w, name)
        self.basicToolBar = w.addToolBar('Basic')

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.spaceAction=self.basicToolBar.addWidget(self.spacer)

        self.add_Action(name,list_widget)
      
        self.basicToolBar.addAction(self.start_simulation)            

    #aggiunge compito al icona
    def add_Action(self,name,list_widget):
         for key, value in list_widget.items():
             if key is name:
                for v in value:
                    self.basicToolBar.insertAction(self.spaceAction,v)




class MenuTop(QMainWindow):

    def __init__(self,trajectory,initial, *args, **kwargs):
        super().__init__(*args, **kwargs) 


        
        self.trjaectory=trajectory
        self.initial=initial
        menu = self.menuBar()
        


        self.campionamento = QDoubleSpinBox()
        self.campionamento.setRange(-100.0, 1000.0)
        self.campionamento.setValue(0)

     
        
        
        settings = menu.addMenu("&Scene Settings")
        settings_scene = menu.addMenu("&Road Options")


        
       

        add_car = QAction(QIcon("./assets/start.png"), "Insert Icon Car", self)
        add_car.setStatusTip("insert car")
        add_car.triggered.connect(self.insert_car)

        insert_campionamento = QAction(QIcon("./assets/start.png"), "Set Campionamento", self)
        insert_campionamento.setStatusTip("Set campionamento")
        insert_campionamento.triggered.connect(self.set_campionamento)

        set_center = QAction(QIcon("./assets/start.png"), "Set Center Simulation", self)
        set_center.triggered.connect(self.dialog_center)
        set_center.setStatusTip("center simulation")


        back = QAction(QIcon("./assets/start.png"), "New Trajectory", self)
        back.triggered.connect(lambda: self.trjaectory.goBack())
        back.setStatusTip("go back")

        #self.filter_paviment = QAction( "Filter Paviment",self,checkable=True)
        #self.filter_paviment.setChecked(False)
        #self.filter_paviment.setStatusTip("Filter Paviment")
        #self.filter_paviment.triggered.connect(self.filter_paviment_active)
       

        settings.addAction(add_car)
        settings.addSeparator()
        settings.addAction(set_center)
        settings.addSeparator()
        settings.addAction(insert_campionamento) 
        settings.addSeparator()
        settings.addAction(back) 
        #settings.addAction(self.filter_paviment) 


        self.insert_min_distance = QAction(QIcon("./assets/start.png"), "Set min length road", self)
        self.insert_min_distance.setStatusTip("Set min road")
        self.insert_min_distance.triggered.connect(self.dialog_set_min_road)

        #self.vehicle_satic = QAction( "Vehicle static",self,checkable=True)
        #self.vehicle_satic.setChecked(False)
        #self.vehicle_satic.setStatusTip("Filter Paviment")
        #self.vehicle_satic.triggered.connect(self.show_static_vehicle)

        self.road_prediction = QAction( "Show road prediction",self,checkable=True)
        self.road_prediction.setChecked(True)
        self.road_prediction.setStatusTip("Show road prediction")
        self.road_prediction.triggered.connect(self.show_prediction)


        settings_scene.addAction(self.insert_min_distance)
#        settings_scene.addAction(self.vehicle_satic)
        settings_scene.addAction(self.road_prediction)
     

        self.layout

    #per mostrare le strade simulate
    def show_prediction(self):
        self.trjaectory.filter_road(15,self.trjaectory.trajectory_data)  

    #per mostrare i veicoli statici     
    #def show_static_vehicle(self):
        #self.trjaectory.filter_road(20,self.trjaectory.trajectory_data)
        

   
    def set_campionamento(self):
        self.campionameno_dialog=QDialog(self)
        self.campionameno_dialog.setFixedHeight(200)
        self.campionameno_dialog.setFixedWidth(300)
        self.campionameno_dialog.setWindowTitle("Sampling")
        form_layout = QFormLayout()

        self.c = QDoubleSpinBox()
        self.c.setRange(-100.0, 1000.0)
        self.c.setValue(self.campionamento.value())

       
        form_layout.addRow("Sampling:", self.c)
        dialog_layout = QVBoxLayout()
        button_save=QPushButton("Save")
        button_save.clicked.connect(self.save_campionamento)

        dialog_layout.addLayout(form_layout)
        dialog_layout.addWidget(button_save,Qt.AlignRight)
        self.campionameno_dialog.setLayout(dialog_layout)
        
        self.campionameno_dialog.exec_()
   



    def save_campionamento(self):
        self.campionamento.setValue(self.c.value())
        self.trjaectory.save_index_sample(self.c.value())
        self.campionameno_dialog.close()

    def dialog_set_min_road(self):

        self.center_dialog=QDialog(self)
        self.center_dialog.setFixedHeight(200)
        self.center_dialog.setFixedWidth(300)
        self.center_dialog.setWindowTitle("Road length ")

        center=QLabel("Road length: ")
        form_layout = QFormLayout()
        self.lenRoad = QDoubleSpinBox()
        
     
        orizontal = QHBoxLayout()

        self.lenRoad.setRange(-100.0, 1000.0)
        form_layout.addRow("Set length:", self.lenRoad)

        orizontal.addLayout(form_layout)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(center)
        dialog_layout.addLayout(orizontal)

        button_save=QPushButton("Save")
        button_save.clicked.connect(self.change_trajectory)
        dialog_layout.addWidget(button_save,Qt.AlignRight)

        self.center_dialog.setLayout(dialog_layout)

        self.center_dialog.exec_()


    def change_trajectory(self):
        self.trjaectory.filter_road(self.lenRoad.value(),self.trjaectory.trajectory_data)
        self.center_dialog.close()

    #per inserire centro di simulazione
    def dialog_center(self):
        print(self.trjaectory.simulation_center.text())
        self.center_dialog=QDialog(self)
        self.center_dialog.setFixedHeight(200)
        self.center_dialog.setFixedWidth(300)
        self.center_dialog.setWindowTitle("Center Simulation")

        center=QLabel("The center of simulation is: ")
        form_layout = QFormLayout()
        self.x = QDoubleSpinBox()
        self.y = QDoubleSpinBox()
        orizontal = QHBoxLayout()


        self.x.setRange(-100.0, 1000.0)
        self.y.setRange(-100.0, 1000.0)
        form_layout.addRow("x_center:", self.x)
        form_layout.addRow("y_centr:", self.y)

        orizontal.addLayout(form_layout)

        dialog_layout = QVBoxLayout()
        dialog_layout.addWidget(center)
        dialog_layout.addLayout(orizontal)

        button_save=QPushButton("Save")
        button_save.clicked.connect(self.save_center)
        dialog_layout.addWidget(button_save,Qt.AlignRight)

        self.center_dialog.setLayout(dialog_layout)

        self.center_dialog.exec_()

    def save_center(self):
        self.trjaectory.simulation_center.setText("Center Simulation: "+ str(self.x.value()) +" "+ str(self.y.value()))
        self.trjaectory.save_center_simulation(self.x.value(),self.y.value())
        self.center_dialog.close()

    #per inserire un nuovo veicolo 
    def insert_car(self):
        self.file_dialog = QFileDialog.Options()
        self.file_dialog = QFileDialog.ReadOnly
        self.file_name, _= QFileDialog.getOpenFileName(self, "Open File", "", "PNG Files (*.png);;JPG Files ( *.jpg);;", options=self.file_dialog)
        new_car=QAction(QIcon(self.file_name), os.path.splitext(os.path.basename(self.file_name))[0] ,self)
        list_widget={"sensor":[],"vehicles":[]}
        new_car.triggered.connect(lambda: self.trjaectory.vehicle_controller(new_car))
        list_widget["vehicles"].append(new_car)
        new_car.setCheckable(True)  
        new_car.setChecked(False)

        self.initial.add_Action("vehicles",list_widget)
