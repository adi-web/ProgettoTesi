import re
import pandas as pd
from pyntcloud import PyntCloud
from mathutils import *

import os


class convert_csv_ply:
    def __init__(self,trasform,path) -> None:
        self.origin = path
        self.p=trasform
        self.destination = trasform.basePath
        if not os.path.exists(self.destination):
                os.makedirs(self.destination)


        self.lista_file = sorted(os.listdir(self.origin), key=self.extract_sort_key)
        self.convert()        



    def extract_sort_key(self,nome_file):
        # Usa un'espressione regolare per estrarre tutti i numeri dal nome del file
        numeri = re.findall(r"\d+", nome_file)
        # Converte i numeri estratti in interi
        return [int(numero) for numero in numeri]
    
    def convert(self):
        # Ottieni la lista dei file nella cartella
        
        j=self.p.i
        # Esegui un ciclo for per iterare sui file
        for i, nome_file in enumerate(self.lista_file):
            # Crea il percorso completo al file
            percorso_completo = os.path.join(self.origin, nome_file)
            #print(f"converting: {percorso_completo}")
            percorso_completo = percorso_completo.replace("\\", "/")
            df = pd.read_csv(percorso_completo)
            if df.empty:
                continue

            # taglia la stringa percorso_completo dal primo / in poi
            percorso_completo = os.path.basename(percorso_completo).split(".")[0]
           # destination = destination.replace("\\", "/")
            #print(df)
            self.p.signal_accept(i)
            cloud = PyntCloud(df)
            cloud.to_file(f"{self.destination}/{percorso_completo}.ply")
            if i==len(self.lista_file):
                 break  

            
