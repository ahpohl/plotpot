# -*- coding: utf-8 -*-
import os, sys
import numpy as np
import sqlite3
import csv
import subprocess
from distutils.spawn import find_executable
from plotpot.dbmanager import DbManager
from plotpot.journal import Journal


class Data(DbManager):
    """class for handling the raw data"""
    
    def __init__(self, args):
        self.args = args
        self.dataFileName = self.getDataFile()
        super().__init__(self.dataFileName)
        self.callConvpot()
        
    
    def reduceData(self):
        """reduce data and stats"""
        self.data = self.fetchData()
        self.stats = self.fetchStatistics()
        self.cycles = self.getCyclesOption()
        self.time = self.getTimeOption()
        self.points = self.getDataOption()
        self.filterData()
        self.filterStatistics()
        
    
    def getData(self):
        return self.data
    
    
    def getStatistics(self):
        return self.stats
    
    
    def getCycles(self):
        """get unique number of cycles"""
        return np.unique(self.stats[:,0])
        
        
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
    
    
    def fetchData(self):
        if self.args.bio_ce:
            listOfData = ["Data_Point","Full_Cycle","Step_Index","Test_Time","Step_Time",
                "DateTime","Current","Voltage2","Capacity","Energy","dQdV","Aux_Channel"]
        else:
            listOfData = ["Data_Point","Full_Cycle","Step_Index","Test_Time","Step_Time",
                "DateTime","Current","Voltage","Capacity","Energy","dQdV","Aux_Channel"]
        select_query = '''SELECT {0} FROM Channel_Normal_Table'''.format(','.join(listOfData))
        self.query(select_query)
        return np.array(self.fetchall())
    
    
    def fetchStatistics(self):
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
        
        
    def isNumber(self, s):
        """This function tests if string s is a number."""
        try:
            float(s)
            return True
        except ValueError:
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
    
    
    def getCyclesOption(self):
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
    
                
    def getDataOption(self):
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
    
    
    def getTimeOption(self):
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
    
    
    def filterData(self):
        """filter data according to selected cycles, time and points""" 
        
        # shape data
        if not self.data.any():
            self.data = np.zeros((1,12))
        
        self.data[:,1] = self.data[:,1]+1 # one based cycle index
        
        # fix discharge capacity and energy being negative
        self.data[:,8] = np.abs(self.data[:,8])
        self.data[:,9] = np.abs(self.data[:,9])
        
        # filter data according to --cycles option
        if self.cycles is not None:
            self.data = self.data[np.logical_and(self.cycles[0] <= self.data[:,1], self.data[:,1] <= self.cycles[1])]
            
        # filter data according to --data option
        elif self.points is not None:
            self.data = self.data[np.logical_and(self.points[0] <= self.data[:,0], self.data[:,0] <= self.points[1])]
            
        # filter data according to --time option
        elif self.time is not None:
            self.data = self.data[np.logical_and(self.time[0] <= self.data[:,3], self.data[:,3] <= self.time[1])]

        if self.args.verbose:
            print("data: %d, %d" % (self.data.shape[0], self.data.shape[1]))   
            
        
    def filterStatistics(self):
        """filter statistics according to selected cycles, time and points"""
        
        # shape statistics
        if not self.stats.any():
            self.stats = np.zeros((1,13))
            
        self.stats[:,0] = self.stats[:,0]+1 # one based cycle index
        
        # fix discharge capacity and energy being negative
        self.stats[:,6] = np.abs(self.stats[:,6])
        self.stats[:,8] = np.abs(self.stats[:,8])
        
        # filter stats according to --cycles option
        if self.cycles is not None:
            self.stats = self.stats[np.logical_and(self.cycles[0] <= self.stats[:,0], self.stats[:,0] <= self.cycles[1])]
            
        # filter data according to --data option
        elif self.points is not None:
            self.stats = self.stats[np.logical_and(self.points[0] <= self.stats[:,2], self.stats[:,1] <= self.points[1])]
            
        if self.args.verbose:
            print("stats: %d, %d" % (self.stats.shape[0], self.stats.shape[1]))
            
            
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
        
        
    def getPlotsOption(self):
        """This function parses the --plot option and returns a list of plots."""
        
        errormsg_not_recognised = "ERROR: Plot option not recognised."
        errormsg_range_error = "ERROR: Plot number out of range."
        
        plots = []
        string_sequence = self.args.plot.split(',')
        for s in string_sequence:
            if self.isNumber(s):
                plots.append(int(s))
            elif '-' in s:
                string_range = s.split('-')
                if self.isNumber(string_range[0]) and self.isNumber(string_range[1]) and len(string_range) == 2:
                    plots_start = int(string_range[0])
                    plots_end = int(string_range[1])+1
                    if int(plots_start) < int(plots_end):
                        sequence = range(plots_start, plots_end)
                        plots.extend(sequence)
                    else:
                        sys.exit(errormsg_range_error)
                else:
                    sys.exit(errormsg_not_recognised)
            else:
                sys.exit(errormsg_not_recognised)
            
        return sorted(set(plots)) # remove duplicates and sort
        
        