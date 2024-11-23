
import glob
import multiprocessing
import sys
import time
import concurrent
import open3d as o3d
import numpy as np
from pathlib import Path
import os
from PyQt5.QtCore import Qt,pyqtSignal,QObject
from PyQt5.QtWidgets import *
import pandas as pd
import win32gui
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QThread
    
class toolOpen3d(QMainWindow):
    def __init__(self,open3d) :
        super().__init__()

        self.open3d=open3d

        toolbar = QToolBar("")
        toolbar.setFixedHeight(50)
       
        self.addToolBar(toolbar)
        if self.open3d.split[len(self.open3d.split)-1] == "ply":
            self.create_widget_sensor(len(open3d.sensorFile))
            for i in range(len(self.sensorwidget)):
                toolbar.addWidget(self.sensorwidget[i])
                
                toolbar.addSeparator()

            self.savePly=QAction("Save simulation",self)
            self.savePly.triggered.connect(lambda:open3d.savePly())  
            self.savePly.setCheckable(True)  
            toolbar.addAction(self.savePly)
      

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  
        toolbar.addWidget(spacer)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider.setRange(0, 1)
        self.slider.setSingleStep(1)
        # controllo se la rendirazzazione della simulazione viene fatta da un file o direttamente subito dopo che blender finisce
        if self.open3d.split[len(self.open3d.split)-1] == "ply":
            self.slider.valueChanged.connect(lambda: open3d.render(self.slider.value()))
        else:
            self.slider.valueChanged.connect(lambda: open3d.renderPly(self.slider.value()))

        toolbar.addWidget(self.slider)

        self.start_animation = QAction("start animation", self)
        self.start_animation.setStatusTip("start animation")
       
        self.start_animation.triggered.connect(lambda: open3d.update_visulization())
        self.start_animation.setCheckable(True)
       
        toolbar.addAction(self.start_animation)
        
        # crea i button dei sensori 
    def create_widget_sensor(self,numSensor):
        self.sensorwidget=[]
        for i in range(numSensor):
            
            s=QCheckBox("S_"+str(i))
            s.setChecked(True)
            s.setFixedWidth(55)
            
            s.toggled.connect(lambda checked, i=i: self.open3d.sensor_display(i))
            self.sensorwidget.append(s)
        return self.sensorwidget

# classe utilizzata per leggere i file ply
class WorkPly(QObject):


    result_ready = pyqtSignal(object)  
    render_point=pyqtSignal()

    def __init__(self, ply_files, ply_directory,  sensorFile,numScan,queue):
        super().__init__()

        self.ply_files = ply_files
        self.i=0
        self.ply_directory = ply_directory
        self.time_read_ply = QtCore.QTimer(self)
        self.time_read_ply.timeout.connect(self.process_files)
        self.sensorFile = sensorFile
        self.numScan=numScan
        self.queue = queue
  


    def removeNoise(self,downpcd):
       
        cl, denoised_ind = downpcd.remove_statistical_outlier(nb_neighbors=6, std_ratio=2.0)

        denoised_cloud = downpcd.select_by_index(denoised_ind)

        # salva punti di tipo noise
        noise_cloud = downpcd.select_by_index(denoised_ind, invert=True)

        return denoised_cloud,noise_cloud
    
    def searchPlane(self,denoised_cloud):
        
        plane_model, inliers = denoised_cloud.segment_plane(distance_threshold=0.2,
                                         ransac_n=3,
                                         num_iterations=1000)
        # point cloud senza il piano
        noneplane_cloud = denoised_cloud.select_by_index(inliers, invert=True)

        return noneplane_cloud
    
    def voxelDownSampl(self,pcd):
       
        downpcd=pcd.voxel_down_sample(voxel_size=0.3)
     
        return downpcd
    


    def process_files(self):

        self.list_toSave={}
        self.list_point={}
        # inizializzo i dizionari per salvare i point cloud
        for k in range(len(self.sensorFile)):
            self.list_point[k]=None
            self.list_toSave[k]=[]

        # ciclo che leggera i file per ogni scnasione    
        for i in range(self.numScan):  
          
            geometries = []
            
            # ciclo che leggera il timestamp in base alla scansione
            for j in range(len(self.sensorFile)):
                # legge file ply del sensore j e della scansione i
                geometry = self.process_single_file(j, i)

                if geometry is not None:

                    geometries.append(geometry)
                    self.list_point[j]=geometry
                    self.list_toSave[j].append(geometry)

            self.i+=1

            # point cloud letto salvato nella coda che viene passato all'applicazione per renderizzare i point cloud
            self.queue.put(self.list_point)

        # chiamata quando i file ply sono letti tutti
        self.save_combination()


    #salva i point cloud alla fine del processo
    def save_combination(self):
        pathTosave="point3D"
        i=0
        pcd = o3d.geometry.PointCloud()

        if not os.path.exists(os.path.join(os.getcwd(),os.path.normpath(self.ply_directory[:-3]),pathTosave)):

            os.makedirs(os.path.join(os.getcwd(),os.path.normpath(self.ply_directory[:-3]),pathTosave))

            for k in range(self.numScan):
                
                pcd.points = o3d.utility.Vector3dVector(self.list_toSave[0][k])
                savePoint=pcd
                for j in range(1,len(self.sensorFile)):

                    pcd = o3d.geometry.PointCloud()
                    pcd.points = o3d.utility.Vector3dVector(self.list_toSave[j][k])
                    savePoint+=pcd

                file_path = os.path.join(os.getcwd(),os.path.normpath(self.ply_directory[:-3]),pathTosave, f"point_{i}.ply")
                o3d.io.write_point_cloud(file_path, savePoint)    
                i=i+1
                 


    def process_single_file(self, j,i):
        ply_file = f"sensor_{j}_{i}.ply"
        ply_path = os.path.join(self.ply_directory, ply_file)

        if os.path.isfile(ply_path):
            # file ply viene processanto con algoritmi vari
            pcd = o3d.io.read_point_cloud(ply_path)
            pcd_voxel = self.voxelDownSampl(pcd)
            denoised_cloud, _ = self.removeNoise(pcd_voxel)
         
            #mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, 0.4)
            #mesh.compute_vertex_normals()
        
            points = np.asarray(denoised_cloud.points)
          
            return points
    

# funzion chiamata dal processor di lettura file ply
def worker_function(ply_files, ply_directory, sensor_file,numScan ,queue):

    # istanziata classe per leggere file ply
    worker = WorkPly(ply_files, ply_directory, sensor_file,numScan, queue)
    worker.process_files()
    

class view3D(QMainWindow):
    def __init__(self,back):
        super(view3D, self).__init__()

        # variabile che tiene tracciata dell' istanza della finestra principale del programma
        self.go_back=back
        toolbar = QToolBar("")
        self.addToolBar(toolbar)

        # button che fa andare indietro sulla pagina principale
        button_action = QPushButton(QIcon("./assets/goback.png"),"Go back", self)
        button_action.setStatusTip("Go back")
       
        button_action.clicked.connect(self.goback)
        toolbar.addWidget(button_action)

        


    
    def start(self,path):
       
        # path per identificare dove andare a leggere i file ply
        self.basePath=path.replace("\\", "/")
        self.split=self.basePath.split("/") 
        number = self.split[len(self.split)-2].split("_")

        # path per indentificare il file sensor della simulazione da renderizzare
        self.path_sensor = os.path.join(
    
            self.split[len(self.split)-4],
            self.split[len(self.split)-3],
            self.split[len(self.split)-2],
            f"sensor_scenario_{number[len(number)-1]}.csv"
        )

        self.ply_files = glob.glob(os.path.join(self.basePath, "*.ply"))
        self.sensorFile = pd.read_csv(os.path.join(os.getcwd(),self.path_sensor))

        widget = QWidget()
        self.setGeometry(500,100,1000,800)

        layout = QGridLayout(widget)
        self.setCentralWidget(widget)

       
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="Open3D", visible=False)

        # creazione di una Window per inserire la finestra 3d
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        self.window = QtGui.QWindow.fromWinId(hwnd)    
        self.windowcontainer = self.createWindowContainer(self.window, widget)
        self.windowcontainer.setFixedHeight(800)
        self.windowcontainer.setGeometry(500,100,1000,800)
        
        
        
        self.toolOpen=toolOpen3d(self)

        layout.addWidget(self.toolOpen)
        layout.addWidget(self.windowcontainer)
        
        # timer che permette di far funzionare l'animazione
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update_visulization)

        # timer utilizzato per aggiornare sempre la visualizzazione per zoom e movimenti 
        self.update_timer2 = QtCore.QTimer(self)
        self.update_timer2.timeout.connect(self.update_vis_move)
        self.update_timer2.start(1)

        # inizializza lo zoom
        self.zoom_factor = 2
        
       
        
        # queue che serve per leggere i point cloud e renderizzarli
        self.queue =multiprocessing.Queue()   
        self.worker_process=None

        # controllo se stiamo facendo prima lettura di file ply o dobbiamo renderizzare simulazione vecchia    
        if str(self.split[len(self.split)-1]) == "ply":

             # numero di scansioni fatte da un unico sensore ( non tutte le scansioni )
            self.numebrScan=round(len(self.ply_files)/len(self.sensorFile))
            
            self.worker_process = multiprocessing.Process(target=worker_function, args=(self.ply_files, self.basePath, self.sensorFile,self.numebrScan, self.queue))

            self.worker_process.start()
        else:
            self.listPly=[]
            for i in range(len(self.ply_files)):
                self.listPly.append("")

            directory=Path(self.basePath)
            j=0
            # leggo i file ply 
            for file_path in directory.glob("*.ply"):
                    timestamp=file_path.stem.split("_")
                    pcd = o3d.io.read_point_cloud(str(file_path))
                    self.listPly[int(timestamp[1])]=pcd
                    self.toolOpen.slider.setMaximum(j)
                    j=j+1

        # timer che permette di controllare se abbiamo nella coda point cloud letti da file
        self.result_timer = QtCore.QTimer(self)
        self.result_timer.timeout.connect(self.check_queue)
        self.result_timer.start(100)
    
        
        self.i=0    

        #self.simulationD={}

        # identifica i sensori da visualizzare nella simulazione
        self.view_sensor=[]

        self.view_control = self.vis.get_view_control()
        self.view_control.set_zoom(1.2)
        
        
        self.windowcontainer.installEventFilter(self)
        

        # lista utilizzata per salvare i point cloud per renderizzzarli nell'applicazione principale
        self.list_step_sensor={}

        for k in range(len(self.sensorFile)):
            self.view_sensor.append(k)
            self.list_step_sensor[k]=[]


   # funzione che manda nella pagina principale dell'applicativo
    def goback(self):

        self.go_back.stackedWidget.setCurrentIndex(0)
        self.update_timer.stop()
        if self.worker_process is not None  :
            if self.worker_process.is_alive:
                self.worker_process.kill()



        self.update_timer.stop()
        self.update_timer2.stop()
        self.result_timer.stop()
        self.vis.destroy_window()  
        self.vis = None        
   

    def costruction_surface(self,i):
        
        ply_directory = r"e:\universita\tesi\ply"


        ply_files = sorted([f for f in os.listdir(ply_directory) if f.endswith('.ply')])

    
        self.vis.clear_geometries() 
        self.openFile(ply_files,ply_directory,i)
        self.executor.submit(self.openFile(ply_files,ply_directory,i))
    
    

    def check_queue(self):
        
        while not self.queue.empty():
            geometries = self.queue.get()
            self.save_geometry(geometries)   


    # aggiorna la visualizzazione dei point cloud        
    def update_vis_move(self):
        
        self.camera_params = self.view_control.convert_to_pinhole_camera_parameters() 
        self.vis.poll_events()
        self.vis.update_renderer()
          
    #def start_processing(self):
      #  print("")

    # funzione che permette di animare la simulazione
    def update_visulization(self):
      

        if self.toolOpen.start_animation.isChecked():
            if not self.update_timer.isActive():
                self.update_timer.start(1000)
                self.g=0
            
            if self.g>=len(self.ply_files):
                self.g=0

            # controllo se dobbiamo visualizzare point cloud direttamnete dopo che blender finisce
            if str(self.split[len(self.split)-1])=="ply":
                self.render(self.g)
            else:
                # permette di visualizzare point cloud gia processati e combinati
                self.renderPly(self.g)  

            self.g+=1
        else:
            # annula l'animazione
            self.update_timer.stop()

    # permette di visualizzare sulla finestra il point cloud di un certo timestamp
    def renderPly(self,timestamp):

        self.vis.clear_geometries()

        self.vis.add_geometry(self.listPly[timestamp])

        self.view_control.convert_from_pinhole_camera_parameters(self.camera_params,True)    
        self.vis.poll_events()
        self.vis.update_renderer()



    # check dei sensori da visualizzare nella renderizzazione dei punti
    def sensor_display(self,sensor):
        
       
        if self.toolOpen.sensorwidget[sensor].isChecked():

            self.view_sensor.append(sensor)
          
        elif sensor in self.view_sensor:
            self.view_sensor.remove(sensor)
          

    # funzione che permette di salvare la simulazione con sensori disattivati 
    def savePly(self):

        # permette di scegliere dove salvare i file ply
        folder_path = QFileDialog.getExistingDirectory(self, "Salva i ply")
     
       # k indica il timestamp
        for k in range(self.numebrScan):
                
                savePoint=self.list_step_sensor[0][k]
                # j identifica il sensore
                for j in range(1,len(self.sensorFile)):
                    # controllo che permette di controllare i point cloud dei sensori da salvare
                    if j not in self.view_sensor or self.list_step_sensor[j][k]==None :
                        pass
                      
                    else:
                        pcd =self.list_step_sensor[j][k]
     
                        savePoint+=pcd
                     
                file_path = os.path.join(folder_path, f"point_{k}.ply")
                
                o3d.io.write_point_cloud(file_path, savePoint)

                savePoint=None    
              
    # value indica il timestamp
    # renderizza i point cloud avendo a disposizione in modo separato i point cloud di ogni sensore
    def render(self,value):
        self.vis.clear_geometries()

        for k in range(len(self.sensorFile)):
                
                if self.list_step_sensor[k][value]==None or k not in self.view_sensor:
                   pass
                else:
                
                   self.vis.add_geometry(self.list_step_sensor[k][value])
                   
        self.view_control.convert_from_pinhole_camera_parameters(self.camera_params,True)    
        self.vis.poll_events()
        self.vis.update_renderer()
        
    # salva i point cloud ricevuti dal processor
    def save_geometry(self, geometries):

    

        for key in geometries:
            
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(geometries[key])
           
            self.list_step_sensor[key].append(pcd)
    
        self.i += 1

        # permette di aumentar lo slider
        self.toolOpen.slider.setMaximum(self.i-1)   

    
    #def update_vis(self):# metodo chiamat ogni secondo dal timer
        
      
     #   self.start_processing()# comincia il prcesso

        

    def eventFilter(self, source, event):
        # controllo del button wheel
        if event.type() == QtCore.QEvent.Wheel and source == self.windowcontainer:
         
            delta = event.angleDelta().y()
            
            zoom_sensitivity = 0.2
            view_control = self.vis.get_view_control()

            # controllo zoom out/in
            if delta > 0:
                # Zoom in
                self.zoom_factor *= (1 - zoom_sensitivity)
            else:
                # Zoom out
                self.zoom_factor *= (1 + zoom_sensitivity)

            # Nuovi livelli di zoom
            view_control.set_zoom(self.zoom_factor)
            self.vis.poll_events()
            self.vis.update_renderer()

            return True  
      
        return super(view3D, self).eventFilter(source, event)
 
    
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    form = view3D()
    form.setWindowTitle('o3d Embed')
  
    form.show()
    sys.exit(app.exec_())




