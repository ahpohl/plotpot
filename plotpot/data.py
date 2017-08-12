# -*- coding: utf-8 -*-
from plotpot.journal import DatabaseManager
import os
import numpy as np
import sqlite3
#import sys
import csv

# functions and classes for manipulating the journal file
class DataSqlite(DatabaseManager):
    
    def __init__(self, args, dataDbPath):
        DatabaseManager.__init__(self, dataDbPath)
        self.args = args
        
    def writeMergeFileSummary(self):
        listOfVars = ["File_ID", "File_Name", "File_Size", "Data_Points", "Localtime", "Comment"]
        select_query = '''SELECT {0} FROM File_Table'''.format(','.join(listOfVars))
        self.query(select_query)
        metadata = self.fetchall()
        
        # insert massStor (mass, cap and area)    
        with open(self.args.filename.split('.')[0]+'_files.csv', 'w',  newline='') as fh:
            header = "%s,%s,%s,%s,%s,%s\n" % (
                "file_ID", "file_name", "file_size", 
                "data_points", "start_datetime", 
                "comment")
        
            fh.write(header)
            writer = csv.writer(fh, dialect='excel')
            writer.writerows(metadata)
            fh.close()
    
    def getNameAndDate(self):
        # get file name and start time
        select_query = '''SELECT File_Name,Start_DateTime FROM File_Table'''
        self.query(select_query)
        return self.fetchone()
        
    def getFileDetails(self):
        # get file details
        listOfVars = ["File_ID", "File_Name", "File_Size", "Data_Points", "Comment", "Start_DateTime", "Device"]
        select_query = '''SELECT {0} FROM File_Table'''.format(','.join(listOfVars))
        self.query(select_query)
        return self.fetchone() + (0,0,0,0) # add dummy fields for mass, cap, area and volume
    
    def getFileCount(self):
        self.query('''SELECT Count(*) FROM File_Table''')
        return self.fetchone()[0]
    
    def getData(self):
        if self.args.counter:
            listOfData = ["Data_Point","Full_Cycle","Step_Index","Test_Time","Step_Time",
                "DateTime","Current","Voltage2","Capacity","Energy","dQdV","Aux_Channel"]
        else:
            listOfData = ["Data_Point","Full_Cycle","Step_Index","Test_Time","Step_Time",
                "DateTime","Current","Voltage","Capacity","Energy","dQdV","Aux_Channel"]
        select_query = '''SELECT {0} FROM Channel_Normal_Table'''.format(','.join(listOfData))
        self.query(select_query)
        return np.array(self.fetchall())
    
    def getStatistics(self):
        listOfStats = ["Full_Cycle","Cycle_Start","Cycle_End","Charge_Time","Discharge_Time",
            "Charge_Capacity","Discharge_Capacity","Charge_Energy","Discharge_Energy",
            "Charge_Voltage","Discharge_Voltage","Hysteresis","Efficiency"]        
        select_query = '''SELECT {0} FROM Full_Cycle_Table'''.format(','.join(listOfStats))
        self.query(select_query)
        return np.array(self.fetchall())
    
    def checkFileSize(self, sqlFile):
        listOfVars = ["File_Size"]
        select_query = '''SELECT {0} FROM File_Table'''.format(','.join(listOfVars))
        try:
            self.query(select_query)
        except sqlite3.OperationalError as e:
            return True
        
        previousSize = int(self.fetchone()[0])
        currentSize = 0
        with open(self.args.filename, 'r') as fh:
            fh.seek(0, os.SEEK_END)
            currentSize = fh.tell()
            fh.close()
            
        if self.args.debug:
            print("currentSize: %ld, previousSize: %ld" % (currentSize, previousSize))
        
        if currentSize == previousSize:
            return False
        else:
            return True