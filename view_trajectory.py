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
from progress_bar import Progress_transform
import subprocess 
from sensor_controller import Sensor_controller, Setting_Sensor
from tool_Controller import MenuTop, initial_tool
from PyQt5.QtGui import QPalette
class View_Trajectory(QMainWindow):

    def __init__(self, parent=None):
        super(View_Trajectory,self).__init__(parent)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        palette = self.palette()
        window_color = palette.color(QPalette.Window)
      

        



        self.verticale=QVBoxLayout(self.central_widget)
        self.info_sensori=QVBoxLayout()
        self.layout_or = QHBoxLayout()
    
        self.setting_sensor=QVBoxLayout()
       
        self.setGeometry(500,100,1000,800)

    
        self.figure= plt.figure()

        self.queue =multiprocessing.Queue()
        
        
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.canavas= FigureCanvas(self.figure)
        #self.canavas.setFixedSize(1000, 600) 
        self.ax = self.figure.add_subplot()

        
        self.canavas.mpl_connect('scroll_event', self.on_scroll)
        self.canavas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canavas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canavas.mpl_connect('button_release_event', self.on_mouse_release)

        # To track mouse state for panning
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
        
    
        
        

        self.enter=False
        self.enterS=False
        
        self.output_dir = os.path.join(os.getcwd(), "raccolta_scenari")

        # Create the directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

       
        toolBar.addWidget(self.initialTool)
        self.selected_sensor=None

        #dqa eliminare alla fine
        #self.plot_trajectory()

        self.mouse_pressed = False 
        self.vehicle_choose=QAction()

        self.layout_or.addWidget(self.canavas,75)
       
        self.index=1

        self.pathSensor=None
        self.add_dockable_widget()
   
        self.setLayout(self.verticale)




    def add_dockable_widget(self):

        self.result_timer = QtCore.QTimer(self)
        self.result_timer.timeout.connect(self.check_queue)
        #self.result_timer.start(500)  # Check queue every 500ms

        # Set up dock
        self.dock = QDockWidget("Processo simulazione", self)
        self.dock_widget = QWidget()
        self.dock_layout = QVBoxLayout(self.dock_widget)
        self.dock.setWidget(self.dock_widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock)

        # Add QListWidget to the dock layout
        self.listWidget = QListWidget()
        self.dock_layout.addWidget(self.listWidget)

        #♦self.listWidget.addItem("item")

        self.dock.setVisible(False)


    def scroll_sensor(self):

        self.scroll.hide()
        self.remove_sensor.hide()
        self.initialTool.setting_icon.setChecked(False)
      
        
        
    def show_scroll(self):
        self.scroll.show()
        self.remove_sensor.show()
     

    def update_window(self,setting_sensor2):
        
        if self.enter is False:
            
            self.remove_sensor=QPushButton("Close")
            self.scroll = QScrollArea(self)
            self.remove_sensor.setCheckable(True)  # Rendi l'azione selezionabile
            self.remove_sensor.setChecked(False)
            self.remove_sensor.clicked.connect(self.scroll_sensor)
            self.remove_sensor.setFixedWidth(100)
            self.setting_sensor.addWidget(self.remove_sensor)
            self.setGeometry(470,100,1200,800)
            #self.setFixedHeight(800)
            
            
            self.setting_sensor.addWidget(self.scroll)
            self.scrollContent = QWidget(self.scroll)
            

            self.scrollLayout = QVBoxLayout(self.scrollContent)
            self.scrollContent.setLayout(self.scrollLayout)
        else:
            self.show_scroll()    
            
           
        self.initialTool.setting_icon.setChecked(True)
        
        #self.scroll.setWidget(setting_sensor2)
        self.scrollLayout.addWidget(setting_sensor2)
       # print("Scroll")
        #print(self.scrollLayout.removeWidget(setting_sensor2))
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(700)
        
        self.scroll.setWidget(self.scrollContent)
       

        spacer = QSpacerItem(1, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.setting_sensor.addSpacerItem(spacer) 
        self.layout_or.setAlignment(Qt.AlignTop)

        self.enter=True
        self.layout_or.addLayout(self.setting_sensor)
      #  print(self.layout_or.itemAt(1).itemAt(1).title())

        self.update()

    
    def remove_widgetScroll(self,name):


        if self.scrollLayout.count() == 1:
            self.scroll_sensor()

        for i in range(self.scrollLayout.count()):
            widget = self.scrollLayout.itemAt(i).widget()
            print(widget.title.text())

            if widget.title.text() == name:
                widget.title.clear()
                widget.deleteLater()
                #self.scrollLayout.removeWidget(widget)
                #self.scroll.show()
                break




    def plot_trajectory(self,trajectory_data,open3d,page5):

        #Questo serve dopo per chiamare direttamente open 3d da controller per avvviare 
        #devo passare dalla funzione il self di
        self.open3d=open3d
        self.page5=page5
    #def plot_trajectory(self):
        #self.trajectory_data = pd.read_csv('./scenari/s2.csv')
        self.trajectory_data=trajectory_data
        #trajectory_data = pd.read_csv('./scenari/s2.csv')
        #trajectory_data = trajectory_data[trajectory_data['observed'] != False  ]
        
        self.trajectory_data = self.trajectory_data[self.trajectory_data['object_type']=="vehicle"]
        self.trajectory_data["object_type"] = "None"

        #trajectory_data.to_csv("s7.csv")

        self.scenario_id = str(self.trajectory_data['scenario_id'][0])  # Convert to string for directory names
        self.scenario_id = self.scenario_id.replace("-", "_")

        

        self.scenario_path = os.path.join(self.output_dir, self.scenario_id)
        

        if not os.path.exists(self.scenario_path):
                os.makedirs(self.scenario_path)

        self.file_count = len(glob.glob(os.path.join(self.scenario_path, "*.csv")))
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
        #print(file_count)
        
        self.filter_road(20, self.trajectory_data)

       # filtered_df.to_csv('filtered_file.csv', index=False)
       
        


    def filter_road(self,lenRoad,trajectory):

        self.ax.clear()
        self.enterS=False
        print("")


        if not self.menuTool.road_prediction.isChecked():
             self.trajectory_data2 = self.trajectory_data[self.trajectory_data['observed']==True]
        else:
            self.trajectory_data2=self.trajectory_data

        data_to_plot=self.filter_trajectory(self.trajectory_data2)

        self.lines=[]
        self.sensor_vehicle=[]
        self.vehicle_put=[]
        self.white_line=[]
        self.trajectory_means=[]
        self_list_pd=[]
      
        
        #self.ax.set_xlim([6469.52438,6620.9131])
        #self.ax.set_ylim([1307.2777,1403.090])
       
        for label in data_to_plot:
            
            trajectory = data_to_plot[label]
           
            #if trajectory["observed"][0]== "False":
             # print("pass")
             # pass
            #else:
            #trajectory["label"] = trajectory_data["label"].where((trajectory_data["x"] < 1.9492955858) & (trajectory_data["label"] == 2283),7777)
            self.trajectory_means.append(self.center_simulation(trajectory))
            if trajectory["object_type"][0]=="cyclist": 
                self.line, =self.ax.plot(trajectory["x"], trajectory["y"],label=trajectory["label"][0],linestyle='--',linewidth=0.8, color='red', solid_capstyle='projecting', picker=False,zorder=10)    
                #trajectory_data.drop(trajectory["label"][0], inplace=True)
                self.trajectory_data2=self.trajectory_data2.loc[self.trajectory_data2['label'] != trajectory["label"][0]]
                self.trajectory_data2.to_csv("s7.csv")
                self.lines.append(self.line)
                
            elif trajectory["object_type"][0]=="pedestrian":
                self.line, =self.ax.plot(trajectory["x"], trajectory["y"],label=trajectory["label"][0],linestyle='--',linewidth=0.8, color='blue', picker=False,zorder=10)    
                self.trajectory_data2=self.trajectory_data2.loc[self.trajectory_data2['label'] != trajectory["label"][0]]
                self.trajectory_data.to_csv("s7.csv")
                self.lines.append(self.line)
            elif trajectory["object_type"][0]=="static":
                self.line, =self.ax.plot(trajectory["x"], trajectory["y"],label=trajectory["label"][0],linestyle='-',linewidth=0.8, color='green', solid_capstyle='projecting', picker=False,zorder=10)    
                self.trajectory_data2=self.trajectory_data2.loc[self.trajectory_data2['label'] != trajectory["label"][0]]
                self.trajectory_data2.to_csv("s7.csv")
                self.lines.append(self.line)
            elif trajectory["object_type"][0]=="background":
                self.line, =self.ax.plot(trajectory["x"], trajectory["y"],label=trajectory["label"][0],linestyle='-',linewidth=0.8, color='orange', solid_capstyle='projecting', picker=False,zorder=10)    
                self.lines.append(self.line)
            else:
                lenx=len(trajectory["x"])
                leny=len(trajectory["y"])
                distancex=int(trajectory["x"][0]-trajectory["x"][lenx-1])
                distancey=int(trajectory["y"][0]-trajectory["y"][leny-1])
                distance = math.sqrt(distancex**2 + distancey**2)
                if distancex!=0 and distancey!=0 and distance>lenRoad:
                    self.line, =self.ax.plot(trajectory["x"], trajectory["y"],label=trajectory["label"][0],linewidth=8, color='grey', solid_capstyle='projecting', picker=True,zorder=10)
                    
                    self.ax.annotate(
                    "",
                    xy=(trajectory["x"][3], trajectory["y"][3]),  # End point of the arrow
                    xytext=(trajectory["x"][0], trajectory["y"][0]),zorder=29,  # Start point of the arrow (a little off)
                    arrowprops=dict(arrowstyle='->', color='red', lw=1)
                        )     
                    self.white_line.append(self.ax.plot(trajectory["x"], trajectory["y"], linestyle='--', color='white', linewidth=0.7, dash_capstyle='round',zorder=20))
                    
                    self.lines.append(self.line)
                elif distance<2 and self.menuTool.vehicle_satic.isChecked():    
                   
                    sensor_icon = Image.open('./assets/vehicle.png')
                    heading_degrees = math.degrees(trajectory["heading"][0])
                    sensor_icon=sensor_icon.rotate(heading_degrees)
    
                    self.sensor_vehicle.append(self.ax.imshow(sensor_icon, extent=[trajectory["x"][0]-1.3,trajectory["x"][0]+1.3,trajectory["y"][1]-1.3,trajectory["y"][1]+1.3], label=trajectory["label"][0],interpolation='antialiased',picker=False,aspect="auto",zorder=20))
                    #self.ax.plot(trajectory["x"], trajectory["y"],label=trajectory["label"][0],linewidth=7, color='grey', solid_capstyle='projecting', picker=True,zorder=10)    
                    pass
                else:
                    l=trajectory["label"][0]
              
                    trajectory = trajectory[trajectory['label'] != l]
           
                #point_b=np.array([trajectory["x"][0],trajectory["y"][0]])
                #point_c=np.array([trajectory["x"][3],trajectory["y"][3]])
               # poitn_a=np.array([point_c[0],point_b[1]])
                #angle=self.angle_vehicle(point_b,poitn_a,point_c)
            

            

                
            self.df_index=pd.DataFrame(trajectory)
            self_list_pd.append( self.df_index)
     
            


    

                #idx = np.argwhere(np.diff(np.sign(f - g))).flatten()  
            self.df = pd.concat(self_list_pd)

            mean_array = np.mean(self.trajectory_means, axis=0)

            self.simulation_center.setText("Center Simulation:  x: "+ str(round(mean_array[0])) +" y: "+ str(round(mean_array[1])))
            self.center_scene=[round(mean_array[0]),round(mean_array[1])]

            
            #self.lines.append(self.line)

        self.canavas.mpl_connect('pick_event',self.on_line)
        self.xcar = self.ax.get_xlim()
        ycar=self.ax.get_ylim()
        self.valorecar=abs(abs(self.xcar[0])-abs(self.xcar[1]))/200
        self.valorecary=abs(abs(ycar[0])-abs(ycar[1]))/200

        print(self.xcar)
        print(self.valorecar)
        self.canavas.draw()

    def center_simulation(self,trajectory_data):
        center_traj=trajectory_data[["x", "y"]].mean().values
        return center_traj


    def filter_trajectory(self,trajectory_data):

        data_to_filter=trajectory_data
        label_to_filter=data_to_filter['label'].unique()
        print(label_to_filter)
        filter_result={}
        for label in label_to_filter:
            filter_result[label]=data_to_filter[data_to_filter['label']==label].reset_index(drop=True)
           

        return filter_result     
    

    
    def on_line(self,event):
        print("dentro")
        print(event.artist.get_label())
        if event.artist in self.lines and self.vehicle_choose.isChecked():
            

            car_icon = Image.open('./assets/'+self.vehicle_choose.text()+'.png')

        
            #angle=self.angle_vehicle(event.artist.get_xydata()[0],point_a,event.artist.get_xydata()[2])
            print("angle")
            #print( self.df["heading"].loc[self.df['label'] == event.artist.get_label()])
            l= self.df["heading"].loc[self.df['label'] == event.artist.get_label()]
        
            print(l)
            heading_degrees = math.degrees(l[0])
            print(heading_degrees)
            car_icon=car_icon.rotate(heading_degrees,expand=True)
            self.ax.autoscale(False)
           
            self.sensor_vehicle.append(self.ax.imshow(car_icon, extent=[event.artist.get_xydata()[1][0]-self.valorecar,event.artist.get_xydata()[1][0]+self.valorecar,event.artist.get_xydata()[1][1]-self.valorecary,event.artist.get_xydata()[1][1]+self.valorecary],label=random.random() ,interpolation='antialiased',picker=True,aspect="auto",zorder=25))
            self.df.loc[self.df['label'] == event.artist.get_label(), "object_type"] = self.vehicle_choose.text()
      
           # self.df.to_csv(self.pathbScenari+'out.csv',index=False)

            
            
            # Check if the directory for this scenario exists
           
                

            if os.path.exists(os.path.join(self.scenario_path, f"{self.scenario_id}.csv")):
                self.df.to_csv(os.path.join(self.scenario_path, self.scenario_id+".csv"), index=False)    

            else:
                self.df.to_csv(self.pathTrajectory, index=False)


            self.save_csv_sample()
            


             
            self.canavas.draw()

        if event.artist in self.sensor_vehicle and self.initialTool.remove_vehicle.isChecked():

            
           
            self.trajectory_data=self.trajectory_data.loc[self.trajectory_data['label'] != event.artist.get_label()]
            self.trajectory_data.to_csv(self.pathTrajectory, index=False)  
            event.artist.remove()
            #self.save_csv_sample()
            self.canavas.draw()
    

    def vehicle_controller(self,vehicle_pick):
        print("vehicle controller")
        print(self.initialTool.vehicle_list) 
        self.vehicle_choose=vehicle_pick
        #vehicle_pick.setCheckable(True)  
        #self.initialTool.disableIcon(vehicle_pick) 
        CURSOR_NEW = QtGui.QCursor(QtGui.QPixmap('./assets/icons8-camera-96.png')) 
        #QApplication.setOverrideCursor(CURSOR_NEW)     
        #QApplication.restoreOverrideCursor()

    


    def on_scroll(self, event):
        """Handle zooming with the mouse wheel."""
        self.ax = self.ax  # Get the current axis
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        print(xlim)
       
        if self.enterS==False:
            self.enterS=True
            self.a=6

          # Define how much to zoom on each scroll

        if event.button == 'up'and self.a<30:  # Zoom in
            scale_factor = 1 / 1.7
            #self.a=self.a*1.5
            self.a *= 1.58
            print(self.a)
            
            
        elif event.button == 'down' and self.a>5.36:  # Zoom out
            scale_factor = 1.7
            self.a /= 1.58
           # self.a=self.a-(self.a*0.334)
            print(self.a)
         
        else:
            return  # Do nothing if it's not a wheel event

        # Calculate the new limits
        new_xlim = [event.xdata - (event.xdata - xlim[0]) * scale_factor,
                    event.xdata + (xlim[1] - event.xdata) * scale_factor]
        new_ylim = [event.ydata - (event.ydata - ylim[0]) * scale_factor,
                    event.ydata + (ylim[1] - event.ydata) * scale_factor]
        
        for line in self.lines:
            line.set_linewidth(self.a)




   
        # Set the new limits
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Redraw the canvas with the updated zoom
        self.canavas.draw()

    def on_mouse_move(self, event):
        """Handle panning when the middle mouse button is held down and the mouse is moved."""
        #print(event.xdata )
        #print("and")
        #print(event.ydata)

        if self.panning and event.xdata is not None and event.ydata is not None:
            ax = self.ax  # Get the current axis
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()

            # Calculate the shift in data coordinates
            dx = self.pan_start_x - event.xdata
            dy = self.pan_start_y - event.ydata

            # Update the axis limits by shifting them
            ax.set_xlim([x + dx for x in xlim])
            ax.set_ylim([y + dy for y in ylim])

            # Redraw the canvas with the updated panning
            self.canavas.draw()

    def on_mouse_release(self, event):
        """Stop panning when the middle mouse button is released."""
        if event.button == 2:  # Middle mouse button
            self.panning = False
            self.pan_start_x = None
            self.pan_start_y = None 

    def on_mouse_press(self, event):
        """Detect when the middle mouse button is pressed for panning."""
        if event.button == 2:  # Middle mouse button
            self.panning = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata


    def start_simulation(self):
        try:

         
        
            self.worker_process = multiprocessing.Process(target=worker_function, args=(self.pathTrajectory,self.name_sensor[0]+"/sensor_scenario"+"_"+self.name_sensor[1]+".csv", str(self.center_scene[0]), str(self.center_scene[1]),self.queue))
            self.worker_process.start()
            self.result_timer.start(100)
            self.dock.setVisible(True)


            self.initialTool.star_simulation.setEnabled(False)
            self.initialTool.star_simulation.setIcon(QIcon("./assets/blender.png"))
            self.initialTool.star_simulation.setText("Simulazione in corso")
           
            
           
        except Exception as e:
            # Gestisce eccezioni impreviste
            print(f"An error occurred while running the simulation: {e}")

    def check_queue(self):
        
        while not self.queue.empty():
           
            self.updatDock(self.queue.get())


        if not self.worker_process.is_alive():   
            self.initialTool.star_simulation.setText("Visualizza 3D")
            self.initialTool.star_simulation.setEnabled(True)
            self.initialTool.star_simulation.setIcon(QIcon("./assets/view3d.png"))
            self.initialTool.star_simulation.triggered.connect(lambda:self.trasformCoordinate())



    def trasformCoordinate(self):
        self.open3d.stackedWidget.setCurrentIndex(4)


       
        self.page5.callFromtrajectory(self.pathBase)


          

    def updatDock(self,item):
        self.listWidget.addItem(str(item))

    def save_center_simulation(self,x,y):
        self.center_scene=[x,y]
        print(self.center_scene)
    def save_index_sample(self,index):
        self.index=int(index)
        self.save_csv_sample()
        print(self.index)
    def save_csv_sample(self):
        #self.df.to_csv('out.csv',index=False)
      
        df_sample = self.df[self.df['object_type'] != "None" ].iloc[::self.index]
        df_sample = df_sample.reset_index(drop=True)
        df_sample.to_csv(self.pathTrajectory, index=False)

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
                stdout=subprocess.PIPE,  # Optional: captures the standard output
                stderr=subprocess.PIPE,  # Optional: captures the error output
                text=True  # Optional: ensures the output is treated as a string
            )

            #startViewLog()
            while True:
                output = process.stdout.readline()
                #listWidget = QListWidget()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    #print(output.strip())
                    #listWidget.addItem(output.strip())
                    self.queue.put(output.strip())    
                    

            # Capture remaining output
            stdout, stderr = process.communicate()

            # Print the final standard output and errors
            print("Standard Output (remaining):\n", stdout)
            print("Standard Error:\n", stderr)

            # Optionally, you can also check the exit code
            exit_code = process.returncode
            self.queue.put(exit_code)  


             

def main():
    app = QtWidgets.QApplication(sys.argv)

    window = View_Trajectory()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

  
  