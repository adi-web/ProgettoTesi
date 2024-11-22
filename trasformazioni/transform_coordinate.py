import os
import glob
import numpy as np
import pandas as pd

class TransformCoordinates:
    def __init__(self,p,basePath) -> None:
        self.basePath = basePath
        self.last_part = os.path.basename(self.basePath)
        self.split = self.basePath.split('/') or self.basePath.split('\\') 

        if len(self.split)==1:
            self.basePatht = os.path.join(self.basePath,
                                          'blender',
                     'csvTrasformato')
            self.pathBaseSensor=basePath
            self.basePath=os.path.join(self.basePath,
                                          'blender',
                     'csv')

        else:   
            self.basePatht = os.path.join(
                'raccolta_scenari', 
                self.split[len(self.split)-4], 
                self.split[len(self.split)-3], 
                'blender', 
                'csvTrasformato'
            )
        if not os.path.exists(self.basePatht):
                os.makedirs(self.basePatht)
              
     
        self.numberSensor = self.sensor_number()
        self.p=p
        # prende tutti i file csv
        csv_files = glob.glob(os.path.join(self.basePath, "*.csv"))
  
        self.numberFile=len(csv_files)
        self.numberScan = round(len(csv_files) / self.numberSensor)

        self.center_sensor()
        self.origin_sensors_global = np.full(self.matrix_sensor.shape, np.nan)
        self.set_global_sensor()
        self.transform_coordinates()

    
    def sensor_number(self):


        if len(self.split)==1:
             number=self.pathBaseSensor.split("_")

             path_sensor = os.path.join(self.pathBaseSensor,f"sensor_scenario_{number[len(number)-1]}.csv")


        else:    
            # ricava indice scansione
            number = self.split[len(self.split)-3].split("_")
        
           
            path_sensor = os.path.join(
                'raccolta_scenari', 
                self.split[len(self.split)-4], 
                self.split[len(self.split)-3], 
                f"sensor_scenario_{number[len(number)-1]}.csv"
            )
        
        self.sensorFile = pd.read_csv(os.path.join(os.getcwd(),path_sensor))
       
        self.matrix_sensor = self.sensorFile[['x', 'y', 'z']].to_numpy().T  # Transpose for a 3xN matrix
    
        return len(self.sensorFile) 

    def center_sensor(self):
        # Calcola il centro di simulazione
        self.sensorCenter = np.array([
            self.sensorFile['x'].mean(),
            self.sensorFile['y'].mean(),
            0
        ])
    

    def set_global_sensor(self):
        # Calcola lo scostamento
        for ss in range(self.matrix_sensor.shape[1]):
            self.origin_sensors_global[:, ss] = self.matrix_sensor[:, ss] - self.sensorCenter
        

    def transform_coordinates(self):

        i=50/self.numberFile
      
        for kk in range(self.numberScan):

            for ii in range(self.numberSensor):
                
                csvFilePath = os.path.join(self.basePath, f"sensor_{ii}_{kk}.csv")
                
                # legge i file dal path costruito
                csvData = pd.read_csv(csvFilePath)
                xyz = csvData[['x', 'y', 'z']].to_numpy()
                
                # trasforma le coordinate
                for jj in range(xyz.shape[0]):
                    xyz[jj, :] = xyz[jj, :] + self.origin_sensors_global[:, ii]
                
                # 
                transformed_data = pd.DataFrame(xyz, columns=['x', 'y', 'z'])
                combined_data = pd.concat([csvData.drop(columns=['x', 'y', 'z']), transformed_data], axis=1)
                combined_data.to_csv(os.path.join(self.basePatht, f"sensor_{ii}_{kk}.csv"), index=False)
                self.p.signal_accept(i)
            
        

if __name__ == '__main__':
    TransformCoordinates()
