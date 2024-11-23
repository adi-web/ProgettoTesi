import sys
import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
                             QFileDialog, QVBoxLayout, QWidget, QDialog, QLabel, QLineEdit, QComboBox, QCheckBox, QHBoxLayout,QBoxLayout)


#tabella per mostrare i file csv delle traiettorie
class TableWidget(QTableWidget):
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.load_df(df)
    
    def init_table(self):
        
        nRows = len(self.df.index)
        nColumns = len(self.df.columns)
        self.setRowCount(nRows)
        self.setColumnCount(nColumns)

        #mostra una tabella vuota 
        if self.df.empty:
            self.clearContents()
            return

        self.setHorizontalHeaderLabels( self.df.columns)
        self.setVerticalHeaderLabels(self.df.index.astype(str))

        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = QTableWidgetItem(str(self.df.iat[row, col]))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.setItem(row, col, item)
                

        self.resizeColumnsToContents()        
        
        self.setSortingEnabled(True)
       
        
        self.horizontalHeader().setSectionsMovable(True)
    
    def load_df(self, df):
        self.df = df
        self.init_table()



class read_csv(QMainWindow):

    #signal usato quando si vuole rappresentare le traiettorie
    switch_window=QtCore.pyqtSignal(pd.DataFrame,object)

    def __init__(self , back):
        super().__init__()
        self.initUI()
        self.back_link=back
        self.selected_columns=[]
        self.init_columns=[]

    def initUI(self):

        self.setWindowTitle("Upload CSV file")
        self.setGeometry(500,100,1000,800)

        self.df = pd.DataFrame()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.browse_button = QPushButton("Choose Trajectory")
        self.browse_button.clicked.connect(self.open_file)
        self.layout.addWidget(self.browse_button)


        
        self.table_widget = TableWidget(self.df)
        self.layout.addWidget(self.table_widget)



        self_container_bottom=QHBoxLayout()

      
        #button che permette di caricare il file e rappresentare le traiettorie
        self.ok_button=QPushButton("Load file")
        self.ok_button.clicked.connect(self.send_csv)
        self.ok_button.setEnabled(True)

        self.back_button=QPushButton("Go Back")
        self.back_button.clicked.connect(self.back)
        self.back_button.setEnabled(True)

        self_container_bottom.addWidget(self.back_button)
        self_container_bottom.addWidget(self.ok_button)

        

        self.layout.addLayout(self_container_bottom)

    #permette di tornare alla pagina iniziale dell'applicativo
    def back(self):
        self.back_link.stackedWidget.setCurrentIndex(0)

    #funzione che fa emit con file traiettorie da visualizzare    
    def send_csv(self):
        self.switch_window.emit(self.file_to_load,self.back_link)


    def open_file(self):
        self.file_dialog = QFileDialog.Options()
        self.file_dialog = QFileDialog.ReadOnly
        self.file_name, _= QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All files (*.*)", options=self.file_dialog)

        if self.file_name:
            self.file_to_load=pd.read_csv(self.file_name)
           
           #per caricare la tabella
            self.table_widget.load_df(self.file_to_load)
            
            for col in range(self.table_widget.columnCount()):
                self.table_widget.horizontalHeaderItem(col)
    

                    
            
