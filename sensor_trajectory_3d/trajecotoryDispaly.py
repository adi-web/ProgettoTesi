from functools import partial
import glob
import math
import multiprocessing
import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt, transforms
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import PolyCollection
import numpy as np
import matplotlib.image as mpimg
from PyQt5 import QtWidgets
from PIL import Image
import pandas as pd
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt,QObject
import random
from trasformazioni.progress_bar import Progress_transform
import subprocess 
from sensor_trajectory_3d.sensorDispaly import Sensor_controller, Setting_Sensor
from controller.menuController import MenuTop, initial_tool
from PyQt5.QtGui import QPalette
class View_Trajectory(QMainWindow):

    def __init__(self, parent=None):
        super(View_Trajectory,self).__init__(parent)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
    
      
        self.verticale=QVBoxLayout(self.central_widget)
        self.info_sensori=QVBoxLayout()
        self.layout_or = QHBoxLayout()
        self.setting_sensor=QVBoxLayout()
        self.setGeometry(500,100,1000,800)

    
        self.figure= plt.figure()
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.canavas= FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot()

        
        self.canavas.mpl_connect('scroll_event', self.setView)
        self.canavas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canavas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canavas.mpl_connect('button_release_event', self.on_mouse_release)

       
        self.panning = False
        self.pan_start_x = None
        self.pan_start_y = None

        self.simulation_center=QLabel()
        self.initialTool=initial_tool(self)
        
        self.menuTool=MenuTop(self,self.initialTool)
        self.menuTool.setMaximumHeight(25)

        self.verticale.addWidget(self.menuTool)


        toolBar = QToolBar()

        
        self.simulation_center.setMaximumHeight(10)
        self.simulation_center.setAlignment(Qt.AlignRight)
        self.simulation_center.setFixedHeight(14)
        
        self.verticale.addWidget(self.simulation_center,alignment=Qt.AlignRight)
        self.verticale.addWidget(toolBar)
        self.verticale.addLayout(self.layout_or)
        
    
        self.lines=[]
        self.whites=[]
        self.firstEnter=True
        self.sensor_vehicle=[]
        
        #variabile di controllo per update_window
        self.enter=False

        #variabile di controllo per lo zoom
        self.enterS=False
        
        #path di tutti i scenari
        self.output_dir = os.path.join(os.getcwd(), "raccolta_scenari")

        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

       
        toolBar.addWidget(self.initialTool)
        #self.selected_sensor=None

        

       # self.mouse_pressed = False 

        self.vehicle_choose=QAction()

        self.layout_or.addWidget(self.canavas,75)
       
        #index per non permettere campionamento di 0 
        self.index=1

        #path sensore per simulazione in blender
        self.pathSensor=None

        #permette di visualizzare i Log di blender
        self.add_dockable_widget()
   
        self.setLayout(self.verticale)


    def vehicle_controller(self,vehicle_pick):
        print(self.initialTool.vehicle_list) 
        self.vehicle_choose=vehicle_pick
     


    def add_dockable_widget(self):

        self.result_timer = QtCore.QTimer(self)
        self.result_timer.timeout.connect(self.check_queue)
    
       
        self.dock = QDockWidget("Process simulation", self)
        self.dock_widget = QWidget()
        self.dock_layout = QVBoxLayout(self.dock_widget)
        self.dock.setWidget(self.dock_widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock)

        # Conterrà la lista di Log
        self.listWidget = QListWidget()
        self.dock_layout.addWidget(self.listWidget)

    
        
        self.dock.setVisible(False)


    #nasconde le tabelle di info dei sensori
    def scroll_sensor(self):

        self.scroll.hide()
        self.remove_sensor.hide()
        self.initialTool.setting_icon.setChecked(False)
      
        
    # mostra tabella di info dei sensori    
    def show_scroll(self):
        self.scroll.show()
        self.remove_sensor.show()
     
    #in ingresso avrà info del sensore settingSensor
    def updateTableInfoSensor(self,settingSensor):

        #controllo per creare solo una Scroll
        if self.enter is False:
            
            self.remove_sensor=QPushButton("Close")
            self.scroll = QScrollArea(self)

            self.remove_sensor.setCheckable(True) 
            self.remove_sensor.setChecked(False)
            self.remove_sensor.clicked.connect(self.scroll_sensor)
            self.remove_sensor.setFixedWidth(100)

            self.setting_sensor.addWidget(self.remove_sensor)
            self.setGeometry(470,100,1200,800)
            
            
            self.setting_sensor.addWidget(self.scroll)
            self.scrollContent = QWidget(self.scroll)

            self.scrollLayout = QVBoxLayout(self.scrollContent)
            self.scrollContent.setLayout(self.scrollLayout)
        else:
            self.show_scroll()    
            
           
        self.initialTool.setting_icon.setChecked(True)
        
        self.scrollLayout.addWidget(settingSensor)
      
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(700)
        
        self.scroll.setWidget(self.scrollContent)
       

        spacer = QSpacerItem(1, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.setting_sensor.addSpacerItem(spacer) 
        self.layout_or.setAlignment(Qt.AlignTop)

        self.enter=True
        self.layout_or.addLayout(self.setting_sensor)
      
        self.update()

    #permette di eliminare sensore dalla tabella passando il nome del sensore
    def remove_widgetScroll(self,name):

        if self.scrollLayout.count() == 1:
            self.scroll_sensor()

        for i in range(self.scrollLayout.count()):
            widget = self.scrollLayout.itemAt(i).widget()
            print(widget.title.text())

            if widget.title.text() == name:
                widget.title.clear()
                widget.deleteLater()
        
                break



    # open3d è istanza della classe startApplicatio utilizzato per avviare open3d
    #page5 istanza che permette di fare trasformate csv->ply
    def displayTrajectory(self,trajectory_data,open3d,page5):

        self.open3d=open3d
        self.page5=page5

        self.trajectory_data=trajectory_data

        
        self.scenario_id = str(self.trajectory_data['scenario_id'][0])  
        scenario_id_new=self.scenario_id.split("_")
        if len(scenario_id_new)!=1:

            #path in base all'id scenario
            self.scenario_id =self.scenario_id[:-2]
            self.file_count=scenario_id_new[len(scenario_id_new)-1]
            self.trajectoryExist=True
            
            self.createPath()


            self.filter_road(20, self.trajectory_data)

            


        else:    
            #elimina tutte le traiettorie che non sono di veicoli
            self.trajectory_data = self.trajectory_data[self.trajectory_data['object_type']=="vehicle"]
            
            self.trajectory_data["object_type"] = "None"

        

            self.scenario_id = self.scenario_id.replace("-", "_")
            self.trajectoryExist=False
            self.createPath()

            
            self.filter_road(20, self.trajectory_data)

       
       
        
    def createPath(self):

        #path in base all'id scenario
        self.scenario_path = os.path.join(self.output_dir, self.scenario_id)
        

        if not os.path.exists(self.scenario_path):
            os.makedirs(self.scenario_path)
            
        if self.trajectoryExist==False: 
            # conta il numero di dir per assegnare un nuovo indice al dir nuovo di un determinato scenario
            self.file_count=sum(os.path.isdir(os.path.join(self.scenario_path, item)) for item in os.listdir(self.scenario_path))
                   

        if not os.path.exists(os.path.join(self.scenario_path, self.scenario_id+"_"+str(self.file_count))): 
                self.name_sensor=self.scenario_id+"_"+str(self.file_count)
                self.pathTrajectory=os.path.join(self.scenario_path, self.scenario_id+"_"+str(self.file_count))
                self.pathBase=self.pathTrajectory
                if not os.path.exists(self.pathTrajectory):
                    os.makedirs(self.pathTrajectory)
                    self.name_sensor=[self.pathTrajectory,str(self.file_count)]
                    
                    self.pathTrajectory=os.path.join(self.pathTrajectory, "scenario"+"_"+str(self.file_count)+".csv")

                self.trajectory_data["scenario_id"]=self.scenario_id+"_"+str(self.file_count)
                self.trajectory_data.to_csv(self.pathTrajectory, index=False)
        else:
            self.name_sensor=[os.path.join(self.scenario_path, self.scenario_id+"_"+str(self.file_count)),str(self.file_count)]
            self.pathTrajectory=os.path.join(self.scenario_path, self.scenario_id+"_"+str(self.file_count),
                                             "scenario"+"_"+str(self.file_count)+".csv")
            
            





    

    def filter_road(self,lenRoad,trajectory):

        #♣self.ax.clear()
        
       

        #permette di visualizzare le strade non reali
        if not self.menuTool.road_prediction.isChecked():
             self.trajectory_data2 = self.trajectory_data[self.trajectory_data['observed']==True]
             for line in self.lines:
                 line.remove()
                 self.lines.remove(line)
                 
             for whiteLine in self.whites:
                    whiteLine.remove()
                    self.whites.remove(whiteLine)
             self.canavas.draw()       
             
        else:
            if len(self.lines) != 0:
                self.ax.autoscale_view()
                for line in self.lines:
                    line.remove()
                    self.lines.remove(line)
                for whiteLine in self.whites:
                    whiteLine.remove()
                    self.whites.remove(whiteLine)
                self.canavas.draw()    
            else:
                self.valoreZoom=8            
            self.trajectory_data2=self.trajectory_data


        self.data_to_plot=self.getIdTrajectory(self.trajectory_data2)

        
        
        self.vehicle_put=[]
        self.white_line=[]
        self.trajectory_means=[]
        self_list_pd=[]
      
        # ciclo per ogni traiettoria
        for label in self.data_to_plot:
            
                trajectory = self.data_to_plot[label]
           
                #utilizzato per calcolare il centro di simulazione
                self.trajectory_means.append(self.center_simulation(trajectory))

                #lunghezza traiettoria
                lenx=len(trajectory["x"])
                leny=len(trajectory["y"])

                distancex=int(trajectory["x"][0]-trajectory["x"][lenx-1])
                distancey=int(trajectory["y"][0]-trajectory["y"][leny-1])

                #distanza calcolata per filtrare in base alla lunghezza della strada
                distance = math.sqrt(distancex**2 + distancey**2)
                if distancex!=0 and distancey!=0 and distance>lenRoad:
                    self.line, =self.ax.plot(trajectory["x"], trajectory["y"],label=trajectory["label"][0],linewidth=self.valoreZoom, color='grey', solid_capstyle='projecting', picker=True,zorder=10)
                    
                    if self.trajectoryExist==False:
        
                        #aggiunge freccia all'inizio della strada
                        self.ax.annotate(
                        "",
                        xy=(trajectory["x"][3], trajectory["y"][3]),  
                        xytext=(trajectory["x"][0], trajectory["y"][0]),zorder=29, 
                        arrowprops=dict(arrowstyle='->', color='red', lw=1)
                            )  

                    #aggiunge strisce trattegiate   
                    self.white_line, =self.ax.plot(trajectory["x"], trajectory["y"], linestyle='--', color='white', linewidth=0.7, dash_capstyle='round',zorder=20)
                    


                    #salvo traiettoria letta
                    self.lines.append(self.line)
                    self.whites.append(self.white_line)

                    #caso di veicoli fermi
                #elif distance<1 and self.menuTool.vehicle_satic.isChecked():    
                   
                 #   sensor_icon = Image.open('./assets/vehicle.png')
                  #  heading_degrees = math.degrees(trajectory["heading"][0])

                   # sensor_icon=sensor_icon.rotate(heading_degrees)
    
                    #self.sensor_vehicle.append(self.ax.imshow(sensor_icon, extent=[trajectory["x"][0]-1.3,trajectory["x"][0]+1.3,trajectory["y"][1]-1.3,trajectory["y"][1]+1.3], label=trajectory["label"][0],interpolation='antialiased',picker=False,aspect="auto",zorder=20))
                    
                    #pass
                else:
                    l=trajectory["label"][0]
                    trajectory = trajectory[trajectory['label'] != l]
        

                
                #dataframe per salvare traiettoria su file csv
                self.df_index=pd.DataFrame(trajectory)
                self_list_pd.append( self.df_index)

    

                #concatena le traiettorie 
                self.df = pd.concat(self_list_pd)

        mean_array = np.mean(self.trajectory_means, axis=0)

        self.simulation_center.setText("Center Simulation:  x: "+ str(round(mean_array[0])) +" y: "+ str(round(mean_array[1])))
        self.center_scene=[round(mean_array[0]),round(mean_array[1])]

        if self.firstEnter:
            #valori per definire dimensione veicolo 
            xcar = self.ax.get_xlim()
            ycar=self.ax.get_ylim()
            self.valorecarx=abs(abs(xcar[0])-abs(xcar[1]))/200
            self.valorecary=abs(abs(ycar[0])-abs(ycar[1]))/200

        self.firstEnter=False
        if self.trajectoryExist:    
            self.addCarTrajectoryExist()

        

        self.canavas.mpl_connect('pick_event',self.vehicleTrajectory)

        self.canavas.draw()

    def addCarTrajectoryExist(self):
         for label in self.data_to_plot:
                trajectory = self.data_to_plot[label]
                if self.trajectoryExist:
                        car_icon = Image.open(f'./assets/{trajectory["object_type"][0]}.png')
                        heading_degrees = math.degrees(trajectory["heading"][0])
                        car_icon=car_icon.rotate(heading_degrees)
                        self.ax.autoscale(False)
                        self.sensor_vehicle.append(self.ax.imshow(car_icon, extent=[trajectory["x"][0]-self.valorecarx,trajectory["x"][0]+self.valorecarx,trajectory["y"][0]-self.valorecary,trajectory["y"][0]+self.valorecary],label=random.random() ,interpolation='antialiased',picker=True,aspect="auto",zorder=25))
                else:
                    break
         self.trajectory_data["object_type"] = "None"



    def center_simulation(self,trajectory_data):
        center_traj=trajectory_data[["x", "y"]].mean().values
        return center_traj


    #funzione che rende l'identificazione di ogni traiettoria
    def getIdTrajectory(self,trajectory_data):

        data_to_filter=trajectory_data
        label_to_filter=data_to_filter['label'].unique()
        print(label_to_filter)
        filter_result={}
        for label in label_to_filter:
            filter_result[label]=data_to_filter[data_to_filter['label']==label].reset_index(drop=True)
           

        return filter_result     
    

    #funzione che aggiunge o rimuove veicolo ad una traiettoria
    def vehicleTrajectory(self,event):
        

        if event.artist in self.lines and self.vehicle_choose.isChecked():
            
            car_icon = Image.open('./assets/'+self.vehicle_choose.text()+'.png')

            print(self.df['heading'])

            print(self.df.columns)
            print(self.df['label'] == 147036) 

  

            print(event.artist.get_label())
           # print(self.df)
            self.df['label'] = self.df['label'].astype(str)

            angle= self.df['heading'].loc[self.df['label'] == event.artist.get_label()]

            print()
            
            print("angle")
            print(angle)
        
      
            heading_degrees = math.degrees(angle[0])
            
            car_icon=car_icon.rotate(heading_degrees,expand=True)

            self.ax.autoscale(False)
           
            self.sensor_vehicle.append(self.ax.imshow(car_icon, extent=[event.artist.get_xydata()[0][0]-self.valorecarx,event.artist.get_xydata()[0][0]+self.valorecarx,event.artist.get_xydata()[0][1]-self.valorecary,event.artist.get_xydata()[0][1]+self.valorecary],label=random.random() ,interpolation='antialiased',picker=True,aspect="auto",zorder=25))
            self.df.loc[self.df['label'] == event.artist.get_label(), "object_type"] = self.vehicle_choose.text()
      
           
                

            #if os.path.exists(os.path.join(self.scenario_path, f"{self.scenario_id}.csv")):
             #   self.df.to_csv(os.path.join(self.scenario_path, self.scenario_id+".csv"), index=False)    

            #else:
               # self.df.to_csv(self.pathTrajectory, index=False)


            self.save_csv_sample()
            
            self.canavas.draw()


        if event.artist in self.sensor_vehicle and self.initialTool.remove_vehicle.isChecked():

            #self.trajectory_data=self.trajectory_data.loc[self.trajectory_data['label'] != event.artist.get_label()]

            

            #self.trajectory_data.to_csv(self.pathTrajectory, index=False)  

            self.trajectory_data=self.trajectory_data.loc[self.trajectory_data['label'] != event.artist.get_label()]
            self.trajectory_data["object_type"] = "None"
            self.trajectory_data.to_csv(self.pathTrajectory, index=False) 

            #self.trajectory_data.loc[self.trajectory_data['label'] == event.artist.get_label(), 'object_type'] = "None"
            #self.df=self.df.loc[self.df['label'] != event.artist.get_label()]


            #self.save_csv_sample()

            event.artist.remove()
            self.canavas.draw()
    

    

    #funzione che gestisce lo zoom-in/out
    def setView(self, event):
        
        self.ax = self.ax  
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

  
       
        if self.enterS==False:
            self.enterS=True
            self.valoreZoom=6


        if event.button == 'up'and self.valoreZoom<30:  # Zoom in
            scale_factor = 1 / 1.7
            self.valoreZoom *= 1.58
          
            
            
        elif event.button == 'down' and self.valoreZoom>5.36:  # Zoom out
            scale_factor = 1.7
            self.valoreZoom /= 1.58
           
         
        else:
            return  #uscire se non è un evento wheel

        # Calcolo i nuovi limiti del grafico
        new_xlim = [event.xdata - (event.xdata - xlim[0]) * scale_factor,
                    event.xdata + (xlim[1] - event.xdata) * scale_factor]
        new_ylim = [event.ydata - (event.ydata - ylim[0]) * scale_factor,
                    event.ydata + (ylim[1] - event.ydata) * scale_factor]
        
        #permette di dimensionare le traiettorie
        for line in self.lines:
            line.set_linewidth(self.valoreZoom)

          

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        self.canavas.draw()

    def on_mouse_move(self, event):

        if self.panning and event.xdata is not None and event.ydata is not None:
            ax = self.ax  
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            dx = self.pan_start_x - event.xdata
            dy = self.pan_start_y - event.ydata

            ax.set_xlim([x + dx for x in xlim])
            ax.set_ylim([y + dy for y in ylim])

        
            self.canavas.draw()

    #non fare piu panning quando il button in mezzo non è pigiato
    def on_mouse_release(self, event):
   
        if event.button == 2:  
            self.panning = False
            self.pan_start_x = None
            self.pan_start_y = None 

    # rileva buttone in mezzo pigiato
    def on_mouse_press(self, event):
     
        if event.button == 2:
            # set a true per permetter il panning
            self.panning = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata


    #funzione che avvia simulazione in blender
    def start_simulation(self):
        try:
            self.save_csv_sample()


            #utilizzo di multiprocessing per fare la simulazione
            self.queue =multiprocessing.Queue()
            self.worker_process = multiprocessing.Process(target=worker_function, args=(self.pathTrajectory,self.name_sensor[0]+"/sensor_scenario"+"_"+self.name_sensor[1]+".csv", str(self.center_scene[0]), str(self.center_scene[1]),self.queue))
            self.worker_process.start()
            
            self.result_timer.start(100)
            self.dock.setVisible(True)

            #button di start simulation 
            self.initialTool.start_simulation.setEnabled(False)
            self.initialTool.start_simulation.setIcon(QIcon("./assets/blender.png"))
            self.initialTool.start_simulation.setText("Simulazione in corso")
           
        except Exception as e:
        
            print(f"An error occurred while running the simulation: {e}")

    #funzione richiamata da workProccessorBlender
    def check_queue(self):
        
        while not self.queue.empty():
           
           #visualizza i Log di Blender
            self.updateDock(self.queue.get())


        #avvia simulazione 3d quando blender finisce
        if not self.worker_process.is_alive():   
            self.initialTool.start_simulation.setText("Visualizza 3D")
            self.initialTool.start_simulation.setEnabled(True)
            self.initialTool.start_simulation.setIcon(QIcon("./assets/view3d.png"))
            self.initialTool.start_simulation.triggered.connect(lambda:self.trasformCoordinate())
            self.result_timer.stop()



    # trasforma i dati ricevuti da blender
    def trasformCoordinate(self):
        self.open3d.stackedWidget.setCurrentIndex(4)
        self.page5.callFromtrajectory(self.pathBase)


          

    def updateDock(self,item):
        self.listWidget.addItem(str(item))

    def save_center_simulation(self,x,y):
        self.center_scene=[x,y]
        

    def save_index_sample(self,index):
        self.index=int(index)
        self.save_csv_sample()
      

    def save_csv_sample(self):
    

        df_sample = self.df[self.df['object_type'] != "None" ].iloc[::self.index]
        df_sample = df_sample.reset_index(drop=True)
        df_sample.to_csv(self.pathTrajectory, index=False)




#metodo chiamato dal processo
def worker_function(pathTrajectory,pathSensor,x,y,queue):
            worker=workProcessBlender(pathTrajectory,pathSensor,x,y,queue)
            worker.startProcess()
            queue=queue




class workProcessBlender(QObject):
    def __init__(self,pathTrajectory,pathSensor,x,y,queue):
        super().__init__()
        self.pathTrajectory=pathTrajectory
        self.pathSensor=pathSensor
        self.x=x
        self.y=y
        self.queue=queue
    

    def startProcess(self):
            process = subprocess.Popen(
                ["blender", "-b", "-P",  r"C:\Users\mucaj\Desktop\universita\tesi\blensor_lidar_simulation\run_simulation.py", "--",self.pathTrajectory,
                self.pathSensor,
                self.x,self.y],
                stdout=subprocess.PIPE,  # Cattura output 
                stderr=subprocess.PIPE,  # Cattura errore output
                text=True  
            )

         
            while True:
                output = process.stdout.readline()
            
                if output == '' and process.poll() is not None:
                    break
                if output:
                    
                    self.queue.put(output.strip())    
                

            exit_code = process.returncode
            self.queue.put(exit_code)  


             

def main():
    app = QtWidgets.QApplication(sys.argv)

    window = View_Trajectory()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

  
  