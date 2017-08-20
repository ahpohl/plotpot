# -*- coding: utf-8 -*-
import os, sys
import numpy as np
import sqlite3
import csv
import subprocess
from distutils.spawn import find_executable
from plotpot.dbmanager import DbManager


class Data(DbManager):
    """class for handling the raw data"""
    
    def __init__(self, args):
        self.args = args
        self.dataFileName = self.getDataFile()
        super().__init__(self.dataFileName)
        self.callConvpot()
        
        
    def getDataFile(self):
        """check if filename with raw data exists"""

        # ckeck if raw file exists        
        rawFileFullPath = os.path.abspath(self.args.filename)
        
        try:
            fh = open(rawFileFullPath, "r")
        except IOError as e:
            sys.exit(e)
            
        # construct sqlite filename 
        dataFileName = self.args.filename.rsplit('.')[0]+'.sqlite'        
        
        return dataFileName
                
    
    def callConvpot(self):
        """create the sqlite database by calling Convpot to convert raw
        data. Check if sqlite file is up-to-date and skip conversion 
        if necessary."""
        
        # search path for Convpot program
        convpotPath = find_executable("convpot")
        
        # search in current dir
        if convpotPath is None:
            convpotPath = find_executable("convpot", sys.argv[0])
        
        if not convpotPath:
            sys.exit("ERROR: Convpot program not installed.")
            
        # test if convpot is executable
        if not os.access(convpotPath, os.X_OK):
            sys.exit("ERROR: Convpot program not executable.")
        
        # get extension of raw file
        rawFileExtension = self.args.filename.rsplit('.')[1]
        
        # test if sqlite file needs updating
        isUpToDate = self.checkFileSize(self.dataFileName)
        
        if (self.args.force or not isUpToDate) and (rawFileExtension != "sqlite"):
        
            # construct call to convpot
            convpotArgs = []
            convpotArgs.append(convpotPath)
        
            # verbose arg
            if self.args.verbose:
                convpotArgs.append("-{0}".format(self.args.verbose * 'v'))
                
            # filename arg 
            convpotArgs.append(self.args.filename)
        
            # call external Convpot program
            try:
                subprocess.check_call(convpotArgs)
            except subprocess.CalledProcessError as e:
                sys.exit(e)
    
        
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
        if self.args.bio_ce:
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
        """Check file size of raw file and compare with size saved in 
           sqlite file. Return True if file is up-to-date and False
           if sizes differ."""
        
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
            
        if self.args.verbose:
            print("currentSize: %ld, previousSize: %ld" % (currentSize, previousSize))
        
        if currentSize == previousSize:
            print("File size match!")
            return True
        
        else:
            return False