import sys
from PyQt5.QtWidgets import *
from PIL import Image
from PyQt5 import QtWidgets
from matplotlib import pyplot as plt
from matplotlib.backend_bases import MouseEvent    
from matplotlib.transforms import Affine2D
import numpy as np
import pandas as pd
from PyQt5.QtCore import QPoint,Qt


class Setting_Sensor(QWidget):

    def __init__(self,sensor_controll,nameSensor):

        super().__init__()

        self.sensor=sensor_controll
        self.nameSensor=nameSensor

        self.setGeometry(700,200,100,80)
       
        vertical = QVBoxLayout()
        orizontal = QHBoxLayout()
        self.form_layout = QFormLayout()
        
       
        self.z_rotation = QDoubleSpinBox()
        self.x_rotation = QDoubleSpinBox()
        self.y_rotation = QDoubleSpinBox()

        self.z_rotation.setRange(-100000.0000, 100000.0000)
        self.x_rotation.setRange(-100000.0000, 100000.0000)
        self.y_rotation.setRange(-100000.0000, 100000.0000)

      
        self.z_rotation.setDecimals(3)
        self.x_rotation.setDecimals(3)
        self.y_rotation.setDecimals(3)
        
        
        self.form_layout.addRow("Z_Rotation:", self.z_rotation)
        self.form_layout.addRow("X_Rotation:", self.x_rotation)
        self.form_layout.addRow("Y_Rotation:", self.y_rotation)
        
     
        from_coordinatase = QFormLayout()
        self.x_coord = QDoubleSpinBox()
        self.y_coord = QDoubleSpinBox()
        self.z_coord = QDoubleSpinBox()
        
        self.x_coord.setRange(-100000.0000, 100000.0000)
        self.y_coord.setRange(-100000.0000, 10000.0000)
        self.z_coord.setRange(-100000.0000, 100000.0000)

       
        self.x_coord.setDecimals(3)
        self.y_coord.setDecimals(3)
        self.z_coord.setDecimals(3)


        from_coordinatase.addRow("x:", self.x_coord)
        from_coordinatase.addRow("y:", self.y_coord)
        from_coordinatase.addRow("z:", self.z_coord)
        

        self.title = QLabel() 

        vertical.addWidget(self.title)

        orizontal.addLayout(from_coordinatase)
        orizontal.addLayout(self.form_layout)
        vertical.setAlignment(Qt.AlignTop)
        vertical.addLayout(orizontal)
        
        
        
        self.setLayout(vertical)

        self.z_rotation.valueChanged.connect(lambda value: self.on_interaction(self.z_rotation,"z_rotation", value))
        self.x_rotation.valueChanged.connect(lambda value: self.on_interaction(self.x_rotation,"x_rotation", value))
        self.y_rotation.valueChanged.connect(lambda value: self.on_interaction(self.y_rotation,"y_rotation", value))

        self.x_coord.valueChanged.connect(lambda value: self.on_interaction(self.x_coord,"x", value))
        self.y_coord.valueChanged.connect(lambda value: self.on_interaction(self.y_coord,"y", value))
        self.z_coord.valueChanged.connect(lambda value: self.on_interaction(self.z_coord,"z", value))
        

    def add_info_sensro(self,x,y,z,z_rotation,name):
        
        self.title.setText("Sensor"+str(name))
        self.x_coord.setValue(x)
        self.y_coord.setValue(y)
        self.z_rotation.setValue(z_rotation)
        self.x_rotation.setValue(90)
        self.z_coord.setValue(z)

    # permette di salvare le modifiche fatte nella tabella dei sensori
    def on_interaction(self, field,field_name, value):

        
        if self.nameSensor in self.sensor.setting_sensor:

            index = self.sensor.data_pd["name"].index(self.nameSensor) 

            self.sensor.data_pd[field_name][index]=value

            self.sensor.save_data_to_csv()



class Sensor_controller(QtWidgets.QWidget):
    def __init__(self,initial_tool,view_trajectory, *args, **kwargs):
        super().__init__(*args, **kwargs) 

        self.data_pd={"x":[],"y":[],"z":[],"x_rotation":[],"y_rotation":[],"z_rotation":[],"name":[]}

        self.view_trajectory = view_trajectory
        self.ax= self.view_trajectory.ax
        self.initial_tool=initial_tool

        #tiene traccia della tabella delle info dei sensori
        self.setting_sensor={}

        self.selected_sensor=None
        self.sensor_list=[]
        self.sensor_text={}
        self.sensor_icon = Image.open('./assets/icons8-camera-96.png')

        self.view_trajectory.canavas.mpl_connect('button_press_event', self.on_mouse_press)
        self.view_trajectory.canavas.mpl_connect('button_release_event', self.on_mouse_release)
        self.view_trajectory.canavas.mpl_connect('motion_notify_event', self.on_mouse_move)
        pass

    def sensor_import(self):
        self.file_dialog = QFileDialog.Options()
        self.file_dialog = QFileDialog.ReadOnly
        self.sensor, _= QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All files (*.*)", options=self.file_dialog)

        if True:
            self.sensor_file=pd.read_csv(self.sensor)
            
            self.ax.autoscale(False)
            

            for index, row in self.sensor_file.iterrows():

                    self.add_new_sensor(row["x"],row["y"],row["z_rotation"],index, self.sensor_icon)

            self.view_trajectory.canavas.mpl_connect('button_press_event',self.on_mouse_click)
            self.view_trajectory.canavas.draw()

    def on_mouse_click(self, event):

        if self.initial_tool.rotate_sensorIcon.isChecked():
            
            sensor_click=event

            #index per indentifica nel dizionario data_pd
            index = self.data_pd["name"].index(sensor_click.label) 

            #permette di controllare il valore di rotazione in gradi
            if self.data_pd["z_rotation"]>=360:
                self.data_pd["z_rotation"]=0


            self.data_pd["z_rotation"][index] = self.data_pd["z_rotation"][index]+15

            #permette di cambiare i valori nella tabella di info sensori
            self.setting_sensor[sensor_click.label].z_rotation.setValue(self.data_pd["z_rotation"][index])
           
            self.save_data_to_csv()
       
       # for i in self.sensor_text:
        #    self.sensor_text[i].set_fontsize(self.view_trajectory.valoreZoom)


    def add_new_sensor(self,x,y,z,index,sensor_icon):

        self.data_pd["x"].append(x)
        self.data_pd["y"].append(y)
        self.data_pd["z"].append(z)
        self.data_pd["x_rotation"].append(90)
        self.data_pd["y_rotation"].append(0)
        self.data_pd["z_rotation"].append(0)
        

        sensor_icon = sensor_icon.rotate(z)
        self.s=self.ax.imshow(sensor_icon, extent=[x-self.view_trajectory.valorecarx-0.1,x+self.view_trajectory.valorecarx+0.1,y-self.view_trajectory.valorecary-0.1,y+self.view_trajectory.valorecary+0.1],picker=True, aspect='auto', zorder=15)
        #self.ax.text(z,y,str(1),color="white")
        
        self.s.label =  str(index)
        self.ax.autoscale(False)

        # Definisci un'affine trasformation (identity) per mantenere dimensione fissa
        identity_transform = Affine2D()

        # Usa un sistema di coordinate dei dati ma con una trasformazione che non cambia la dimensione del testo
        text=self.ax.text(x-0.05, y-0.001, f" {index}",
                    color="white", fontsize=8, ha="center", va="center", 
                    zorder=16, transform=self.ax.transData + identity_transform)



        self.ax.autoscale(False)    

        
        self.data_pd["name"].append(self.s.label)
        #self.s.angle = 0
        
        self.sensor_list.append(self.s)

        self.sensor_text[self.s.label]=text
        
        self.save_data_to_csv()

        self.view_trajectory.canavas.draw()

        #modo per aggiungere nello scroll le info del sensor
        new_setting=Setting_Sensor(self,self.s.label)
        new_setting.add_info_sensro(x, y, z, 90, self.s.label)
        self.setting_sensor[self.s.label]=new_setting
        self.view_trajectory.updateTableInfoSensor(new_setting)

        #self.view_trajectory.update_window(s)
    def save_data_to_csv(self):

        df = pd.DataFrame(self.data_pd)

        # salva in csv 
        df.to_csv(self.view_trajectory.name_sensor[0]+"\sensor_scenario_"+self.view_trajectory.name_sensor[1]+".csv", index=False)
            

    def on_mouse_press(self, event):

        # permette di aggiungere nuovo sensore
        if self.initial_tool.new_sensorIcon.isChecked():
            self.ax.autoscale(False)
            
            # dati dove si è clickato per aggiungere il sensore
            xdata, ydata = event.xdata, event.ydata
            
            
            self.add_new_sensor(xdata,ydata,5,len(self.sensor_list)+1,self.sensor_icon)

            # quando si clicka un sensore verra chiamato la funzione on_mouse_click
            self.view_trajectory.canavas.mpl_connect('pick_event',self.on_mouse_click)

            #aggiorna grafico
            self.view_trajectory.canavas.draw()

        elif event.inaxes is self.ax and event.button == 1 and self.initial_tool.modify_sensorIcon.isChecked() :

            self.mouse_pressed = True
            
            # ciclo per cercare il sensore selezionato
            for sensor_img in self.sensor_list:
                if self.is_mouse_over_sensor(event, sensor_img):
                    
                    self.selected_sensor = sensor_img
                   
                    break 

            
        elif self.initial_tool.remove_sensor.isChecked():
        
            # cerca sensore da eliminare
            for sensor_img in self.sensor_list:
                if self.is_mouse_over_sensor(event, sensor_img):
                    
                    self.selected_sensor_delete = sensor_img
                    
                    index = self.data_pd["name"].index(self.selected_sensor_delete.label) 

                    #rimuove dal grafico il sensore
                    self.view_trajectory.remove_widgetScroll("Sensor"+self.selected_sensor_delete.label)

                    # elimina dati sensore
                    for key in self.data_pd:
                        del self.data_pd[key][index]

                    self.selected_sensor_delete.remove()
                    self.view_trajectory.canavas.draw()

                    self.sensor_list.remove(sensor_img)
                    
                    #salva modifiche
                    self.save_data_to_csv()  

                    break

        elif self.initial_tool.rotate_sensorIcon.isChecked() and event.inaxes is self.ax :

            for sensor_img in self.sensor_list:
                if self.is_mouse_over_sensor(event, sensor_img):
                    
                    self.selected_sensor = sensor_img
                   
                    break

            index = self.data_pd["name"].index(self.selected_sensor.label) 

            #permette di controllare il valore di rotazione in gradi
            if self.data_pd["z_rotation"][index]>=360:
                self.data_pd["z_rotation"][index]=0

            self.data_pd["z_rotation"][index] = self.data_pd["z_rotation"][index]+15
         

            #serve per ruotare il sensore ogni 15 gradi
            sensor_icon = self.selected_sensor.get_array().copy()  
            pil_image = Image.fromarray(sensor_icon)  
            rotated_image = pil_image.rotate(15, expand=False) 

            
            self.selected_sensor.set_data(np.array(rotated_image)) 

            #permette di cambiare i valori nella tabella di info sensori
            self.setting_sensor[self.selected_sensor.label].z_rotation.setValue(self.data_pd["z_rotation"][index])
           
            self.save_data_to_csv()      
            self.view_trajectory.canavas.draw()
       



    #funzione che fa il check se siamo sopra il sensore
    def is_mouse_over_sensor(self, event, sensor_img):
       
        xdata, ydata = event.xdata, event.ydata
        extent = sensor_img.get_extent()
        return extent[0] <= xdata <= extent[1] and extent[2] <= ydata <= extent[3]


    def on_mouse_release(self, event):
        if event.button == 1:  
            self.mouse_pressed = False
            self.selected_sensor=None
            

    #funzione che permette di muovere il sensore
    def on_mouse_move(self, event):

        if self.selected_sensor is not None and self.initial_tool.modify_sensorIcon.isChecked():
    
            xdata, ydata = event.xdata, event.ydata
            new_extent = [xdata - self.view_trajectory.valorecarx-0.1, xdata +self.view_trajectory.valorecarx+0.1,
                          ydata -self.view_trajectory.valorecary-0.1, ydata + self.view_trajectory.valorecary+0.1]

            # Aggiorna posizione solo il sensore selezionato
            self.selected_sensor.set_extent(new_extent)

            self.sensor_text[self.selected_sensor.label].set_x(xdata-0.005)
            self.sensor_text[self.selected_sensor.label].set_y(ydata)


    

            #permette di cambiare i valori nella tabella di info sensori
            self.setting_sensor[self.selected_sensor.label].x_coord.setValue(xdata)
            self.setting_sensor[self.selected_sensor.label].y_coord.setValue(ydata)
            
            #serve per aggiornare il file csv
            index = self.data_pd["name"].index(self.selected_sensor.label) 
            self.data_pd["x"][index] = xdata
            self.data_pd["y"][index] = ydata

            self.save_data_to_csv()

            print(self.selected_sensor)
           

            self.view_trajectory.canavas.draw()