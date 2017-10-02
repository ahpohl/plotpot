# -*- coding: utf-8 -*-
import os, sys
import numpy as np
import sqlite3
import csv
import subprocess
from distutils.spawn import find_executable
import zipfile, tempfile, shutil
from plotpot.dbmanager import DbManager
from plotpot.journal import Journal


class Data(DbManager):
    """class for handling the raw data"""
    
    def __init__(self, args):
        self.args = args
        self.dataFileName = self.getDataFile()
        super().__init__(self.dataFileName)
        
        # do the work
        self.callConvpot()
        self.data = self.fetchData()
        self.stats = self.fetchStatistics()
        self.filterData()
        self.filterStatistics()
        self.plots = self.getPlotsOption()
        self.cycles = self.getCycles()
        self.metaInfo = self.updateMetaInfo()
        self.fullStats = self.calcStatistics()
        
        
    def exportData(self):
        """process --export option"""
        self.writeStatisticsTable()
        self.writeDataTable()
        self.writeVoltageProfile()
        self.writeMergeFileSummary()
        jourObj = Journal(self.args)
        jourObj.writeJournalEntry(self.getNameAndDate())
        
    
    def getMetaInfo(self):
        return self.metaInfo
        
    
    def getData(self):
        return self.data
    
    
    def getStatistics(self):
        return self.fullStats
    
    
    def getPlots(self):
        return self.plots
    
    
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
    
    
    def getNameAndDate(self):
        """get file name and start time"""
        fileCount = self.getFileCount()
        
        # merged file
        if fileCount > 1:
            select_query = '''SELECT File_Name,DateTime FROM Global_Table'''
            self.query(select_query)
            return self.fetchone()
        
        # single file
        else:
            select_query = '''SELECT File_Name,Start_DateTime FROM File_Table'''
            self.query(select_query)
            return self.fetchone()
    
    
    def getFileDetails(self):
        """get file details for insertion into journal"""
        fileCount = self.getFileCount()
        
        # merged file
        if fileCount > 1:
            listOfVars = ["File_Name", "File_Size", "DateTime", "Data_Points"]
            select_query = '''SELECT {0} FROM Global_Table'''.format(','.join(listOfVars))
            self.query(select_query)
            return self.fetchone() + ("merged", "",) # add device and comment columns to result set
        
        # single file
        else:    
            listOfVars = ["File_Name", "File_Size", "Start_DateTime", "Data_Points", "Device", "Comment"]
            select_query = '''SELECT {0} FROM File_Table'''.format(','.join(listOfVars))
            self.query(select_query)
            return self.fetchone()
    
    
    def getFileCount(self):
        self.query('''SELECT Count(*) FROM File_Table''')
        return self.fetchone()[0]
    

    def updateMetaInfo(self):
        """Search journal for battery filename and date. If battery already exists
           fetch meta info from journal. Ask questions to update
           meta info according to selected plots.
           If battery does not exist create new journal entry"""
           
        # create journal object
        jourObj = Journal(self.args)
           
        # read file name and start datetime
        fileNameDate = self.getNameAndDate()
        
        # search plotpot-journal.dat if battery exists
        searchResult = jourObj.searchJournalTable(fileNameDate)
        
        if searchResult is not None:
            # set metaInfo with values found in journal
            jourObj.setMetaInfo(searchResult[0], searchResult[1], searchResult[2], searchResult[3])
            jourObj.askMetaInfo(self.plots)
            jourObj.updateMetaInfo(fileNameDate)
        
        else:
            # if entry not found, fetch data from data file (global or file table)
            jourObj.askMetaInfo(self.plots)
            journalEntry = self.getFileDetails() + jourObj.tupleMetaInfo()
            # create new record in journal file
            jourObj.insertRowJournalTable(journalEntry)
            
        return jourObj.getMetaInfo()


    def checkFileSize(self, sqlFile):
        """Check file size of raw file and compare with size saved in 
           sqlite file. Return True if file is up-to-date and False
           if sizes differ."""

        currentSize = 0
        with open(self.args.filename, 'r') as fh:
            fh.seek(0, os.SEEK_END)
            currentSize = fh.tell()
            fh.close()
        
        listOfVars = ["File_Size"]
        select_query = '''SELECT {0} FROM Global_Table'''.format(','.join(listOfVars))
        try:
            self.query(select_query)
        except sqlite3.OperationalError as e:
            return False
        
        previousSize = int(self.fetchone()[0])
            
        if self.args.verbose:
            print("currentSize: %ld, previousSize: %ld" % (currentSize, previousSize))
        
        if currentSize == previousSize:
            if self.args.verbose:
                print("File size match!")
            return True 
        else:
            return False
                
    
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
        """Fetch data from Channel_Normal_Table"""
        listOfData = ["Data_Point","Full_Cycle","Step_Index","Test_Time","Step_Time",
            "DateTime","Current","Voltage","Voltage2","Capacity","Energy","dQdV","Aux_Channel"]
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
        
    
    def isFullCell(self):
        """test if voltage2 counter electrode column is not zero"""
        return np.any(self.data[:,8])
    
        
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
    
    
    def filterData(self):
        """filter data according to selected cycles, time and points""" 
        
        # get cycles, points and time range
        cycles = self.getCyclesOption()
        time = self.getTimeOption()
        points = self.getDataOption()
        
        # shape data
        if not self.data.any():
            self.data = np.zeros((1,12))
        
        self.data[:,1] = self.data[:,1]+1 # one based cycle index
        
        # fix discharge capacity and energy being negative
        self.data[:,9] = np.abs(self.data[:,9])
        self.data[:,10] = np.abs(self.data[:,10])
        
        # filter data according to --cycles option
        if cycles is not None:
            self.data = self.data[np.logical_and(cycles[0] <= self.data[:,1], self.data[:,1] <= cycles[1])]
            
        # filter data according to --data option
        elif points is not None:
            self.data = self.data[np.logical_and(points[0] <= self.data[:,0], self.data[:,0] <= points[1])]
            
        # filter data according to --time option
        elif time is not None:
            self.data = self.data[np.logical_and(time[0] <= self.data[:,3], self.data[:,3] <= time[1])]

        if self.args.verbose:
            print("data: %d, %d" % (self.data.shape[0], self.data.shape[1]))   
            
        
    def filterStatistics(self):
        """filter statistics according to selected cycles"""
        
        # get cycles, points and time range
        cycles = self.getCyclesOption()
        
        # shape statistics
        if not self.stats.any():
            self.stats = np.zeros((1,13))
            
        self.stats[:,0] = self.stats[:,0]+1 # one based cycle index
        
        # fix discharge capacity and energy being negative
        self.stats[:,6] = np.abs(self.stats[:,6])
        self.stats[:,8] = np.abs(self.stats[:,8])
        
        # filter stats according to --cycles option
        if cycles is not None:
            self.stats = self.stats[np.logical_and(cycles[0] <= self.stats[:,0], self.stats[:,0] <= cycles[1])]
            
        if self.args.verbose:
            print("stats: %d, %d" % (self.stats.shape[0], self.stats.shape[1]))
    
    
    def calcStatistics(self):
        """
        stats (stats array):
        0: cycle index
        1: cycle start
        2: cycle end
        3: charge time [s]
        4: discharge time [s]    
        5: charge capacity [As]
        6: discharge capacity [As]
        7: charge energy [VAs]
        8: discharge energy [VAs]
        9: average charge voltage [V]
        10: average discharge voltage [V]
        11: voltage hysteresis [V]
        12: coulombic efficiency
        
        extended stats (export array):
        0: cycle index
        1: cycle start
        2: cycle end
        3: charge time [s]
        4: discharge time [s]    
        5: charge capacity [mAh/g]
        6: discharge capacity [mAh/g]
        7: specific charge energy [Wh/kg]
        8: specific discharge energy [Wh/kg]
        9: volumetric charge energy [Wh/L]
        10: volumetric discharge energy [Wh/L]
        11: average charge voltage [V]
        12: average discharge voltage [V]
        13: average charge current [A]
        14: average discharge current [A]
        15: voltage hysteresis [V]
        16: coulombic efficiency [%]
        17: specific charge current density [mA/g]
        18: specific discharge current density [mA/g]
        19: area charge current density [mA/cm-2]
        20: area discharge current density [mA/cm-2]
        21: charge c-rate [h]
        22: discharge c-rate [h]
        """        
        # ignore division by zero errors
        np.seterr(divide='ignore', invalid='ignore')
        
        # copy cycle index, start, end, time(c) and time(d) to export array 
        export = self.stats[:,:5] # [0,1,2,3,4]
        
        # convert capacity from As to mAh/g [5,6]
        export = np.c_[export, self.stats[:,5:7]] # [5,6]
        if self.metaInfo['mass'] == 0:
            export[:,5] = 0
            export[:,6] = 0
        else:
            export[:,5] = export[:,5] / (3.6e-3 * self.metaInfo['mass'])
            export[:,6] = export[:,6] / (3.6e-3 * self.metaInfo['mass'])
                  
        # convert energy from Ws to Wh/kg
        export = np.c_[export, self.stats[:,7:9]] # [7,8]
        if self.metaInfo['mass'] == 0:
            export[:,7] = 0
            export[:,8] = 0
        else:        
            export[:,7] = export[:,7] / (3.6e-3 * self.metaInfo['mass'])
            export[:,8] = export[:,8] / (3.6e-3 * self.metaInfo['mass'])
        
        # convert energy from Ws to Wh/L
        # 1 h = 3600 s, volume in µL
        export = np.c_[export, self.stats[:,7:9]] # [9,10]
        if self.metaInfo['volume'] == 0:
            export[:,9] = 0
            export[:,10] = 0
        else:    
            export[:,9] = export[:,9] / (3.6e-3 * self.metaInfo['volume'])
            export[:,10] = export[:,10] / (3.6e-3 * self.metaInfo['volume'])
            
        # copy average voltage
        export = np.c_[export, self.stats[:,9:11]] # [11,12]
                           
        # calculate average current for each cycle
        # I = Q / t [As / s = A ]
        # step time is wrong if there was rest time
        try:
            export = np.c_[export, self.stats[:,5] / self.stats[:,3]] # charge [13]
            export = np.c_[export, self.stats[:,6] / self.stats[:,4]] # discharge [14]
        except ZeroDivisionError as e:
            print("Warning: %s" % e)
            
        # copy coulombic efficienty and voltage hysteresis
        export = np.c_[export, self.stats[:,11:13]] # [15,16]
        
        # calculate specific current density
        # J_mass = I / m [A/mg] * 1e6 = [mA/g]
        if self.metaInfo['mass'] == 0:
            export = np.c_[export, np.zeros((export.shape[0], 2))]
        else:
            export = np.c_[export, export[:,13] / self.metaInfo['mass'] * 1e6] # [17]
            export = np.c_[export, export[:,14] / self.metaInfo['mass'] * 1e6] # [18]
        
        # calculate area current density
        # J_Area = I / A [ A / cm² ] * 1e3 = [mA/cm²]
        if self.metaInfo['area'] == 0:
            export = np.c_[export, np.zeros((export.shape[0], 2))]
        else:
            export = np.c_[export, export[:,13] / self.metaInfo['area'] * 1e3] # [19]
            export = np.c_[export, export[:,14] / self.metaInfo['area'] * 1e3] # [20]
        
        # calculate theoretical capacity
        # C = m * Ctheo [mg * mAh/g *1e-3 = Ah]
        cap_th = self.metaInfo['mass'] * self.metaInfo['cap'] * 1e-6
        
        # calculate C-rate / x
        # x = C / I [Ah / A = h]
        try:
            export = np.c_[export, cap_th / export[:,13]] # [21]
            export = np.c_[export, cap_th / export[:,14]] # [22]
        except ZeroDivisionError as e:
            print("Warning: %s" % e)     
        
        return export
        
    
    def __dumpArray(self, fh, array, formatstring="%f", delimiter=',', header=''):
        if formatstring == '%f':
            formatspec = []
            f = 0
            while True:
                if f == array.shape[1]:
                    break
                else:
                    formatspec.append(formatstring)
                f += 1
        else:
            formatspec = formatstring.split(' ')
        if header != '':
            fh.write(header)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                if array[i,j] == None:
                    array[i,j] = 0
                if j == array.shape[1]-1:
                    fh.write(formatspec[j] % (array[i,j]))
                else:
                    fh.write(formatspec[j] % (array[i,j])+delimiter)
            fh.write("\n")


    def writeMergeFileSummary(self):
        listOfVars = ["File_ID", "File_Name", "File_Size", "Data_Points", "Localtime", "Comment"]
        select_query = '''SELECT {0} FROM File_Table'''.format(','.join(listOfVars))
        self.query(select_query)
        metadata = self.fetchall()
        
        # insert metaInfo (mass, cap and area)    
        with open(self.args.filename.split('.')[0]+'_files.csv', 'w',  newline='') as fh:
            header = "%s,%s,%s,%s,%s,%s\n" % (
                "file_ID", "file_name", "file_size", 
                "data_points", "start_datetime", 
                "comment")
        
            fh.write(header)
            writer = csv.writer(fh, dialect='excel')
            writer.writerows(metadata)
            fh.close()
    
    
    def writeDataTable(self):
        
        with open(self.args.filename.split('.')[0]+'_data.csv', 'w') as fh:
            header = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                "data_point", "cycle_index", "step_index", 
                "test_time", "step_time", "datetime", 
                "current", "voltage", "voltage2", "capacity", 
                "energy", "dQ/dV", "temperature")
            fh.write(header)
            header = ",,,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                "s", "s", "s", "A", "V", "V", "As", "Ws", "As/V", "°C")
            fh.write(header)        
            self.__dumpArray(fh, self.data, '%d %d %d %f %f %f %e %f %f %f %f %f %f')
            fh.close()
    
    
    def writeStatisticsTable(self): 
        # calculate mass loading
        if self.metaInfo['area'] == 0:
            loading = 0
        else:
            # m / A = [ mg / cm² ]
            loading = self.metaInfo['mass'] / self.metaInfo['area']
        
        with open(self.args.filename.split('.')[0]+'_statistics.csv', 'w') as fh:
        
            # export metaInfo
            header = """Mass,Capacity,Area,Volume,Loading
mg,mAh/g,cm²,µL,mg/cm²\n"""
            fh.write(header)
            
            dat = "%.2f,%.2f,%.2f,%.2f,%.2f\n" % (
                    self.metaInfo['mass'], 
                    self.metaInfo['cap'], 
                    self.metaInfo['area'], 
                    self.metaInfo['volume'], 
                    loading)
            fh.write(dat)
            
            # write statistics
            header = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    "cycle_index", "start", "end",
                    "time(c)", "time(d)", 
                    "capacity(c)", "capacity(d)", 
                    "energy(c)", "energy(d)",
                    "energy(c)", "energy(d)",
                    "Vav(c)", "Vav(d)",
                    "current(c)", "current(d)",
                    "efficiency", "hysteresis",
                    "density(c)", "density(d)",
                    "density(c)", "density(d)",
                    "c-rate(c)", "c-rate(d)")
            fh.write(header)
            
            units = ",,,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    "s", "s", "mAh/g", "mAh/g", "Wh/kg",
                    "Wh/kg", "Wh/L", "Wh/L", "V", "V", "A", "A", "%", "V",
                    "mA/g", "mA/g", "mA/cm²", "mA/cm²", "h", "h")
            fh.write(units)
            
            self.__dumpArray(fh, self.fullStats, "%d %d %d %f %f %f %f %f %f %f %f %f %f %e %e %f %f %f %f %f %f %f %f")
            fh.close()
    
      
    def writeVoltageProfile(self):
        
        # convert from As to mAh/g
        if self.metaInfo['mass'] == 0:
            self.data[:,9] = 0
        else:
            self.data[:,9] = self.data[:,9] / (3.6e-3 * self.metaInfo['mass'])
            
        cwd = os.getcwd() # save current directory
        os.chdir(tempfile.gettempdir()) # change to tmp dir
        filestem = self.args.filename.split('.')[0] # create filename
        if not os.path.exists(filestem):
            os.makedirs(filestem) # create directory
        path = os.path.abspath(filestem) # change to directory
        os.chdir(path)
        
        # loop over cycles
        for c in self.cycles:
            d = self.data[self.data[:,1]==c] # select cycle
            ch = d[d[:,2]==1] # select charge half cycle
            dc = d[d[:,2]==-1] # select discharge hafl cycle
            ch = ch[:-1] # discard last data point, zero capacity
            dc = dc[:-1] # discard last data point, zero capacity
                
            # charg
            if ch.size:
                header = """# cycle %d
# charge
# mass %.2f mg
# %-12s %-12s %-12s
# %-12s %-12s %-12s\n""" % (c, self.metaInfo['mass'], "capacity", "voltage", "dQ/dV", "mAh/g", "V", "As/V")
                cyclename = filestem+'_%03d_charge.txt' % c
                fh = open(cyclename, 'w')
                fh.write(header)
                for i in range(ch.shape[0]):
                    line = "%12.6f %12.6f %12.6f\n" % (ch[i,9], ch[i,7], ch[i,11])
                    fh.write(line)
                fh.close()
                
            # discharge
            if dc.size:
                header = """# cycle %d
# discharge
# mass %.2f mg
# %-12s %-12s %-12s
# %-12s %-12s %-12s\n""" % (c, self.metaInfo['mass'], "capacity", "voltage", "dQ/dV", "mAh/g", "V", "As/V")
                cyclename = filestem+'_%03d_discharge.txt' % c
                fh = open(cyclename, 'w')
                fh.write(header)
                for i in range(dc.shape[0]):
                    line = "%12.6f %12.6f %12.6f\n" % (dc[i,9], dc[i,7], dc[i,11])
                    fh.write(line)
                fh.close()
                
        # create zip archive
        os.chdir(tempfile.gettempdir())
        zfile = filestem + '.zip'
        zipf = zipfile.ZipFile(zfile, 'w', zipfile.ZIP_DEFLATED)
        base = os.path.basename(path)
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                zipf.write(os.path.join(base, name))
        zipf.close()
        shutil.rmtree(path) # remove tmp directory
        shutil.copy(zfile, cwd)
        os.remove(zfile)
        os.chdir(cwd)