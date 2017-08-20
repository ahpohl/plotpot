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
        
        self.cycles = self.getCycles()
        print(self.cycles)
        self.time = self.getTime()
        print(self.time)
        self.points = self.getPoints()
        print(self.points)
        
        
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
            if self.args.verbose:
                print("File size match!")
            return True 
        else:
            return False
        
    def parseRange(self, option):
        """This function parses the a command line option which specifies
        a data range and returns a tuple with the interval"""
        
        errormsg_not_recognised = "Error: Option not recognised."
        
        string = option.split(',')
        if len(string) == 2:
            if self.isNumber(string[0]) and self.isNumber(string[1]):
                interval = (string[0],string[1])
            else:
                sys.exit(errormsg_not_recognised)
        elif len(string) == 1:
            if self.isNumber(string[0]):
                interval = (0,string[0])
            else:
                sys.exit(errormsg_not_recognised)
        else:    
            sys.exit(errormsg_not_recognised)
            
        return interval
    
    
    def getCycles(self):
        """get cycles from --cycles option"""
        
        # init cycles
        cycles = None
        
        if self.args.cycles:
            # parse cycles option
            cycles = self.parseRange(self.args.cycles)
            cycles = [int(x) for x in cycles] # now list of integers
                    
            # sanity checks
            if cycles[0] > cycles[1] or len([x for x in cycles if x < 0]) != 0:
                sys.exit("ERROR: Cycles option out of range.")
                
        return cycles
    
                
    def getPoints(self):
        """get data points from --data option"""
    
        # init points
        points = None
    
        if self.args.data:
            # parse data point option
            points = self.parseRange(self.args.data)
            points = [int(x) for x in points] # now list of integers
            
            #sanity checks
            if points[0] > points[1] or len([x for x in points if x < 0]) != 0:
                sys.exit("ERROR: Data option out of range.")
        
        return points
    
    
    def getTime(self):
        """get time from --time option"""
        
        # init time
        time = None
        
        if self.args.time:
            # parse time option
            time = self.parseRange(self.args.time)
            time = [float(x) for x in time] # now list of floats
            
            # sanity checks
            if time[0] >= time[1] or len([x for x in time if x < 0]) != 0:
                sys.exit("ERROR: Time option out of range.")
            
            time = [x*3600 for x in time] # in seconds
        
        return time
    
    
    def filterCycles(self, data, stats):
        """filter data and stats according to selected cycles"""
        
        cycles = self.getCycles()
        
        # filter data according to --cycles option
        if cycles is not None:
            data = data[np.logical_and(cycles[0] <= data[:,1], data[:,1] <= cycles[1])]
            stats = stats[np.logical_and(cycles[0] <= stats[:,0], stats[:,0] <= cycles[1])]
        
        return data, stats
        
        