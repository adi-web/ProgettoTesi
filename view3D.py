
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
def prova():
    ply_directory = r"e:\universita\tesi\ply"

    # List all .ply files in the directory
    ply_files = sorted([f for f in os.listdir(ply_directory) if f.endswith('.ply')])

    # Create a visualizer window
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    
    for i in range(0, 5):  # Loop through different time steps
        vis.clear_geometries()  # Clear previous geometries
        
        for j in range(0, 9):  # Loop through sensor indices
            ply_file = f"sensor_{j}_{i}.ply"  # Construct the filename dynamically
            ply_path = os.path.join(ply_directory, ply_file)

            # Check if the file exists before attempting to load it
            if os.path.isfile(ply_path):
                pcd = o3d.io.read_point_cloud(ply_path)
                pcd.paint_uniform_color([0.5, 0.5, 1.0])
                mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, 0.4)
                
                mesh.compute_vertex_normals()
                vis.add_geometry(mesh)  # Add the mesh to the visualizer
              
                print(f"Loaded: {ply_file}")
            else:
                print(f"File not found: {ply_file}")

        # Update the visualizer to show the current point cloud
        vis.poll_events()
        vis.update_renderer()

        # Use a non-blocking loop to keep the visualizer responsive
        #time.sleep(1)

    # Clean up the visualizer
    vis.destroy_window()
    
class toolOpen3d(QMainWindow):
    def __init__(self,open3d) :
        super().__init__()

        self.open3d=open3d

        toolbar = QToolBar("My main toolbar")
        toolbar.setFixedHeight(50)
       
        self.addToolBar(toolbar)
        if self.open3d.split[len(self.open3d.split)-1] == "ply":
            self.create_widget_sensor(len(open3d.sensorFile))
            for i in range(len(self.sensorwidget)):
                toolbar.addWidget(self.sensorwidget[i])
                
                toolbar.addSeparator()

            self.savePly=QAction("Salva simulazione",self)
            self.savePly.triggered.connect(lambda:open3d.savePly())  
            self.savePly.setCheckable(True)  
            toolbar.addAction(self.savePly)
        #toolbar.addAction(button_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Make the spacer expand
        toolbar.addWidget(spacer)
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.slider.setRange(0, 1)
        self.slider.setSingleStep(1)
        if self.open3d.split[len(self.open3d.split)-1] == "ply":
            self.slider.valueChanged.connect(lambda: open3d.render(self.slider.value()))
        else:
            self.slider.valueChanged.connect(lambda: open3d.renderPly(self.slider.value()))

        toolbar.addWidget(self.slider)

        self.start_animation = QAction("start animation", self)
        self.start_animation.setStatusTip("This is your button")
       
        self.start_animation.triggered.connect(lambda: open3d.update_visulization())
        self.start_animation.setCheckable(True)
        #start_animation.setText("ci")
        toolbar.addAction(self.start_animation)
        
    def create_widget_sensor(self,numSensor):
        self.sensorwidget=[]
        for i in range(numSensor):
            #s = QAction( "S_"+str(i),self,checkable=True)
           
            s=QCheckBox("S_"+str(i))
            s.setChecked(True)
            s.setFixedWidth(55)
            
            s.toggled.connect(lambda checked, i=i: self.open3d.sensor_display(i))
            self.sensorwidget.append(s)
        return self.sensorwidget

class WorkPly(QObject):
    result_ready = pyqtSignal(object)  # Signal to notify when the result is ready
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
       # print("qua si tolgono i punti outlier che sono inutili per la visualizzazione")
        cl, denoised_ind = downpcd.remove_statistical_outlier(nb_neighbors=6, std_ratio=2.0)
        denoised_cloud = downpcd.select_by_index(denoised_ind)
        noise_cloud = downpcd.select_by_index(denoised_ind, invert=True)
        return denoised_cloud,noise_cloud
    
    def searchPlane(self,denoised_cloud):
        #print("qua si va a trovare il piano e si toglie dalla visualizzazione")
        plane_model, inliers = denoised_cloud.segment_plane(distance_threshold=0.2,
                                         ransac_n=3,
                                         num_iterations=1000)
        
        noneplane_cloud = denoised_cloud.select_by_index(inliers, invert=True)
        return noneplane_cloud
    
    def voxelDownSampl(self,pcd):
        #print(" per ridure numero di punti nella nuvola , utile quando abbiamo tanti punit , permette di mantenere la struttura")
        downpcd=pcd.voxel_down_sample(voxel_size=0.3)
        #downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid( radius=0.1, max_nn=30))
        return downpcd
    


    def process_files(self):
        #if not self.time_read_ply.isActive():
            #self.time_read_ply.start(1000)
        #if self.i>=12:
        self.list_toSave={}
        self.list_point={}
        for k in range(len(self.sensorFile)):
            self.list_point[k]=None
            self.list_toSave[k]=[]
            
        for i in range(self.numScan):  
            #self.list_point={"sensor_step":[],"point":[]}  
            geometries = []
            
            for j in range(len(self.sensorFile)):
                geometry = self.process_single_file(j, i)
                if geometry is not None:
                    geometries.append(geometry)
                    #self.list_point["sensor_step"].append((j,i))
                    #self.list_point["point"].append(geometry)
                    self.list_point[j]=geometry
                    self.list_toSave[j].append(geometry)

            self.i+=1
            self.queue.put(self.list_point)
            
           # print(self.queue)
            
            #self.queue.put(geometries)        
            #self.result_ready.emit(geometries)
        
        print(self.list_toSave)
        self.save_combination()

        #self.render_point.emit()

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
                print(self.ply_directory)        


    def process_single_file(self, j,i):
        ply_file = f"sensor_{j}_{i}.ply"
        ply_path = os.path.join(self.ply_directory, ply_file)
        if os.path.isfile(ply_path):
            pcd = o3d.io.read_point_cloud(ply_path)
            pcd_voxel = self.voxelDownSampl(pcd)
            denoised_cloud, _ = self.removeNoise(pcd_voxel)
            #noneplane_cloud = self.searchPlane(denoised_cloud)
            mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(pcd, 0.4)
            mesh.compute_vertex_normals()
            #points = np.asarray(noneplane_cloud.points)
            points = np.asarray(pcd.points)
            #points = np.asarray(pcd_voxel.points)
            return points
    """
    @QtCore.pyqtSlot(int)
    def process_files(self,i):
        geometries = []
        for j in range(0, len(self.sensorFile)):
            ply_file = f"sensor_{j}_{i}.ply"
            ply_path = os.path.join(self.ply_directory, ply_file)
            if os.path.isfile(ply_path):
                pcd = o3d.io.read_point_cloud(ply_path)
                pcd_voxel = self.voxelDownSampl(pcd)
                denoised_cloud, _ = self.removeNoise(pcd_voxel)
                noneplane_cloud = self.searchPlane(denoised_cloud)
                geometries.append(noneplane_cloud)
        self.result_ready.emit(geometries)  # Emit the loaded geometries when ready

       """


def worker_function(ply_files, ply_directory, sensor_file,numScan ,queue):
    worker = WorkPly(ply_files, ply_directory, sensor_file,numScan, queue)
    worker.process_files()
    

class view3D(QMainWindow):
    def __init__(self,back):
        super(view3D, self).__init__()
        self.go_back=back
        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("./assets/goback.png"),"Go back", self)
        button_action.setStatusTip("Open Trajesctory")
       
        button_action.triggered.connect(self.goback)
        toolbar.addAction(button_action)

        



    def start(self,path):
       

        

        #da cambiare
        #self.basePath = r'./output_scans'
        self.basePath=path.replace("\\", "/")
        self.split=self.basePath.split("/") 
        number = self.split[len(self.split)-2].split("_")
       # print("Nuova directory corrente:", os.getcwd())
       
        self.path_sensor = os.path.join(
    
            self.split[len(self.split)-4],
            self.split[len(self.split)-3],
            self.split[len(self.split)-2],
            f"sensor_scenario_{number[len(number)-1]}.csv"
        )#self.basePath=r"e:\universita\tesi\ply"
       #self.basePath = r"C:\Users\mucaj\Desktop\universita\fit-plane-open3d-main\fit-plane-open3d-main"
        self.ply_files = glob.glob(os.path.join(self.basePath, "*.ply"))
        self.sensorFile = pd.read_csv(os.path.join(os.getcwd(),self.path_sensor))
        widget = QWidget()
        self.setGeometry(500,100,1000,800)
        layout = QGridLayout(widget)
        self.setCentralWidget(widget)

       
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(window_name="Open3D", visible=False)

        #self.pcd_road = o3d.io.read_point_cloud(r"C:\Users\mucaj\Desktop\universita\tesi\blensor lidar simulation frontEnd\road.ply")
        #self.vis.add_geometry(self.pcd_road)

        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        self.window = QtGui.QWindow.fromWinId(hwnd)    
        self.windowcontainer = self.createWindowContainer(self.window, widget)
        self.windowcontainer.setFixedHeight(800)
        self.windowcontainer.setGeometry(500,100,1000,800)
        
        
        
        self.toolOpen=toolOpen3d(self)

        layout.addWidget(self.toolOpen)
        layout.addWidget(self.windowcontainer)
        
        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update_visulization)

        self.update_timer2 = QtCore.QTimer(self)
        self.update_timer2.timeout.connect(self.update_vis_move)
        self.update_timer2.start(1)
        #self.update_timer.start(1000)
        self.zoom_factor = 2
        
        self.numebrScan=round(len(self.ply_files)/len(self.sensorFile))
        
        self.queue =multiprocessing.Queue()   
        self.worker_process = multiprocessing.Process(target=worker_function, args=(self.ply_files, self.basePath, self.sensorFile,self.numebrScan, self.queue))
            
        if str(self.split[len(self.split)-1]) == "ply":
            self.worker_process.start()
        else:
            self.listPly=[]
            for i in range(len(self.ply_files)):
                self.listPly.append("")

            directory=Path(self.basePath)
            j=0
            for file_path in directory.glob("*.ply"):
                    timestamp=file_path.stem.split("_")
                    pcd = o3d.io.read_point_cloud(str(file_path))
                    self.listPly[int(timestamp[1])]=pcd
                    self.toolOpen.slider.setMaximum(j)
                    j=j+1

        self.result_timer = QtCore.QTimer(self)
        self.result_timer.timeout.connect(self.check_queue)
        self.result_timer.start(100)
    
        
        self.i=0    

        #self.thread = QThread()
        
        #self.worker = WorkPly(self.ply_files, self.basePath, self.sensorFile)
        
        

        #self.worker.moveToThread(self.thread)
       # self.worker.result_ready.connect(self.save_geometry)
        #self.worker.render_point.connect(self.update_visulization)
       # self.thread.start()
        #self.update_vis()
        self.simulationD={}
        self.hide_sensor=[]
        self.view_control = self.vis.get_view_control()
        self.view_control.set_zoom(1.2)
        
        
        self.windowcontainer.installEventFilter(self)
        

        self.list_step_sensor={}
        for k in range(len(self.sensorFile)):
            self.hide_sensor.append(k)
            self.list_step_sensor[k]=[]

        #self.update_vis()
   
    def goback(self):
        self.go_back.stackedWidget.setCurrentIndex(0)
        self.update_timer.stop()
        if self.worker_process.is_alive:
            self.worker_process.kill()
   

    def costruction_surface(self,i):
        
        ply_directory = r"e:\universita\tesi\ply"

    # List all .ply files in the directory
        ply_files = sorted([f for f in os.listdir(ply_directory) if f.endswith('.ply')])

        # Create a visualizer window
    
        
       # for i in range(0, 5):  # Loop through different time steps
        self.vis.clear_geometries()  # Clear previous geometries
        self.openFile(ply_files,ply_directory,i)
        self.executor.submit(self.openFile(ply_files,ply_directory,i))
    
    

    def check_queue(self):
        
        while not self.queue.empty():
            geometries = self.queue.get()
            self.save_geometry(geometries)   
            
    def update_vis_move(self):
        
        self.camera_params = self.view_control.convert_to_pinhole_camera_parameters() 
        self.vis.poll_events()
        self.vis.update_renderer()
          
    def start_processing(self):
        print("")
         #QtCore.QMetaObject.invokeMethod(self.worker, "process_files", QtCore.Qt.QueuedConnection)


    def update_visulization(self):
        print("visualizzazione")
        if self.toolOpen.start_animation.isChecked():
            if not self.update_timer.isActive():
                self.update_timer.start(1000)
                self.g=0
            
            if self.g>=len(self.ply_files):
                self.g=0

            if str(self.split[len(self.split)-1])=="ply":
                self.render(self.g)
            else:
                self.renderPly(self.g)  

            self.g+=1
        else:
            self.update_timer.stop()

    def renderPly(self,timestamp):

        self.vis.clear_geometries()
        self.vis.add_geometry(self.listPly[timestamp])

        self.view_control.convert_from_pinhole_camera_parameters(self.camera_params,True)    
        self.vis.poll_events()
        self.vis.update_renderer()



    def sensor_display(self,sensor):
        
        print(sensor)
        if self.toolOpen.sensorwidget[sensor].isChecked():

            self.hide_sensor.append(sensor)
            print("aggiunot")
        elif sensor in self.hide_sensor:
            self.hide_sensor.remove(sensor)
            print("eli")


    def savePly(self):


        folder_path = QFileDialog.getExistingDirectory(self, "Salva i ply")
     
       #k indica il timestamp
        for k in range(self.numebrScan):
                
                savePoint=self.list_step_sensor[0][k]
                for j in range(1,len(self.sensorFile)):
                    if j not in self.hide_sensor or self.list_step_sensor[j][k]==None :
                        pass
                      
                    else:
                        pcd =self.list_step_sensor[j][k]
                        #pcd.points = o3d.utility.Vector3dVector(self.list_toSave[j][k])
                        savePoint+=pcd
                     
                file_path = os.path.join(folder_path, f"point_{k}.ply")
                
                o3d.io.write_point_cloud(file_path, savePoint)

                savePoint=None    
              
    #value indica il timestamp
    def render(self,value):
        self.vis.clear_geometries()
        a=self.list_step_sensor[0][value]
        for k in range(len(self.sensorFile)):
                if self.list_step_sensor[k][value]==None or k not in self.hide_sensor:
                   pass
                else:
                   #o3d.visualization.draw_geometries([source.translate((0, 0, 0)), target])
                   self.vis.add_geometry(self.list_step_sensor[k][value])
                   
                  # self.vis.add_geometry(self.pcd_road)

        #for geometry in self.simulationD[value]:
            #self.vis.add_geometry(geometry)
        self.view_control.convert_from_pinhole_camera_parameters(self.camera_params,True)    
        self.vis.poll_events()
        self.vis.update_renderer()
        

    def save_geometry(self, geometries):
        """
        if not self.update_timer.isActive():
            self.update_timer.start(1000)

        """
          
               
       
        print("salvando point cloud")
        reconstructed_geometries = []

        #x = geometries.get("sensor_step")
        #self.list_step_sensor.append(geometries)
        #print(geometries)

        for key in geometries:
            #print(key)
            #print(geometries[key][0])
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(geometries[key])
           
            self.list_step_sensor[key].append(pcd)


            
        #for points in geometries:
            # Reconstruct the Open3D point cloud from the numpy array
           # pcd = o3d.geometry.PointCloud()
            #pcd.points = o3d.utility.Vector3dVector(points)
            #reconstructed_geometries.append(pcd)
        
        #self.simulationD[self.i]=geometries
        #self.simulationD[self.i] = reconstructed_geometries
        #print(len(self.simulationD))
        self.i += 1
        self.toolOpen.slider.setMaximum(self.i-1)   

        """
        self.vis.clear_geometries()
        for geometry in geometries:
            self.vis.add_geometry(geometry)


        if not self.update_timer.isActive():
            self.update_timer.start(1000)
            self.camera_params = self.view_control.convert_to_pinhole_camera_parameters()
            self.view_control.set_zoom(1.2)
        
        self.vis.clear_geometries()
        for geometry in geometries:
            self.vis.add_geometry(geometry)    
        self.view_control.convert_from_pinhole_camera_parameters(self.camera_params,True)    
        self.vis.poll_events()
        self.vis.update_renderer()
        self.i += 1    
        """
        



    def update_vis(self):# metodo chiamat ogni secondo dal time
        
        #if self.i < self.numebrScan:
        self.start_processing()# comincia il prcesso
        #else:

          #  self.i = 0 #permette di ricominciare la simulazione da capo

        
        #self.vis.update_geometry()
        

    def eventFilter(self, source, event):
        # Check if the event is a wheel event and the source is the windowcontainer.
        if event.type() == QtCore.QEvent.Wheel and source == self.windowcontainer:
            # Get the scroll amount. event.angleDelta().y() returns the scroll amount in eighths of a degree.
            delta = event.angleDelta().y()

            # Adjust zoom sensitivity as needed.
            zoom_sensitivity = 0.2

            # Get the current view control.
            view_control = self.vis.get_view_control()

            # Get the current distance to the look-at point.
           

            # Adjust the zoom level. Positive delta means scroll up (zoom in), negative means scroll down (zoom out).
            if delta > 0:
                # Zoom in
                self.zoom_factor *= (1 - zoom_sensitivity)
            else:
                # Zoom out
                self.zoom_factor *= (1 + zoom_sensitivity)

            # Set the new zoom level.
            view_control.set_zoom(self.zoom_factor)
            self.vis.poll_events()
            self.vis.update_renderer()


            return True  # Indicate that the event was handled.

        # Default processing for other events.
        return super(view3D, self).eventFilter(source, event)
 
    
if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    form = view3D()
    form.setWindowTitle('o3d Embed')
  
    form.show()
    sys.exit(app.exec_())




