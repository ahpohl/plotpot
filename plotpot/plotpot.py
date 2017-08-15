#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
import subprocess
from distutils.spawn import find_executable
import numpy as np
    
# import own files
from plotpot.plot import plot
from plotpot.export import export
from plotpot.data import DataSqlite
from plotpot.journal import JournalSqlite

# plotpot class
    
class Plotpot(object):
    
    def __init__(self, args):
        self.args = args
        self.__RunPlotpot()        
    
    def __RunPlotpot(self):
  
        #disable division by zero warnings
        np.seterr(divide='ignore')
        
        # create global database in program directroy
        envCfg = os.environ.get('PLOTPOT_JOURNAL')
        fileCfg = "plotpot-journal.dat"
        if envCfg:
            journalDbPath = os.path.join(envCfg, fileCfg)
        else:
            journalDbPath = os.path.join(os.path.dirname(sys.argv[0]), fileCfg)
            
        # check if journal file exists
        try:
            fh = open(journalDbPath, "r")
        except IOError as e:
            print(e)
            create = input("Do you want to create a new journal file (Y,n)? ")
            if create == 'n':
                sys.exit()
                
        # store mass and capacity in dict
        # mass: active mass [mg]
        # cap: theoretical capacity [mAh/g]
        # area: electrode area [cm²]
        # volume: volume of electrode [µL]
        massStor = {'mass': 0, 'cap': 0, 'area': 0, 'volume': 0}
    			   
        # create journal object and schema
        journalDb = JournalSqlite(self.args, journalDbPath, massStor)
        
        # update schema if needed
        journalDb.updateSchema()
        
        # delete journal entry    
        if self.args.delete and self.args.journal:
            journalDb.deleteRow("Journal_Table", self.args.delete)
            journalDb.printJournal("Journal_Table")
            print("Journal file: %s." % journalDbPath)
            print("Deleted row %d from journal." % self.args.delete)
            sys.exit()
        
        # print plotpot journal file
        if self.args.journal:
            journalDb.printJournal("Journal_Table")
            print("Journal file: %s." % journalDbPath)
            sys.exit()
        
        # check if filename exists
        path = os.path.abspath(self.args.filename)
        try:
            fh = open(path, "r")
        except IOError as e:
            sys.exit(e)
            
        # execute external program to convert args[0] into sqlite file
        mdbpath = find_executable("convpot") # search path
        
        if mdbpath == None:
            mdbpath = find_executable("convpot", sys.argv[0]) # search current dir
        
        if not mdbpath:
            sys.exit("ERROR: Convpot not found.")
            
        # test if mdbpath is executable
        if not os.access(mdbpath, os.X_OK):
            sys.exit("ERROR: Convpot program not executable.")
        
        sqlfile = path.rsplit('.')[0]+'.sqlite'
        sqlext = path.rsplit('.')[1]
        
        # create data object  
        dataDb = DataSqlite(self.args, sqlfile)
        
        # test if sqlite file needs updating
        isUpdate = dataDb.checkFileSize(sqlfile)
        
        if (isUpdate or self.args.force) and sqlext != "sqlite":
        
            mdbargs = []
            mdbargs.append(mdbpath)
        
            if self.args.verbose:
                mdbargs.append("--verbose")
        
            mdbargs.append(self.args.filename)
        
            try:
                subprocess.check_call(mdbargs)
            except subprocess.CalledProcessError as e:
                sys.exit(e)
            
        # parse plot option
        plots = self.plot_option()
        
        # read file name and start datetime
        fileNameDate = dataDb.getNameAndDate()
        fileCount = dataDb.getFileCount()
        
        if fileCount > 1:
            fileNameList = list(fileNameDate)
            fileNameList[0] = self.args.filename
            fileNameDate = tuple(fileNameList)
        
        # search arbin.cfg if battery exists in file
        searchResult = journalDb.searchJournal(fileNameDate)
        
        # if entry not found, fetch data from data file (global or file table)
        if searchResult == None:
            journalEntry = dataDb.getFileDetails()
            
            # treat merged file different than single file
            if fileCount > 1:
                journalList = list(journalEntry)
                journalList[1] = self.args.filename
                journalList[6] = "merged"
                journalEntry = tuple(journalList)
              
        else:
            # get mass and capapcity from journal
            journalEntry = searchResult
            massStor['mass'] = journalEntry[6]
            massStor['cap'] = journalEntry[7]
            massStor['area'] = journalEntry[8]
            massStor['volume'] = journalEntry[9]
        
        # ask questions
        if any([x in [1,4,5,11] for x in plots]):
            journalDb.ask_mass()
        if 10 in plots:
            journalDb.ask_capacity()
        if any([x in [12] for x in plots]):
            journalDb.ask_area()
        if 6 in plots:
            journalDb.ask_volume()
            
        # update massStor
        massStor = journalDb.get_mass()
                        
        # create new record in journal file if previous record was not found, otherwise update mass
        if searchResult == None:
            journalDb.insertRow("Journal_Table", journalEntry, massStor)
        else:
            journalDb.updateColumn("Journal_Table", "Mass", massStor['mass'], journalEntry)
            journalDb.updateColumn("Journal_Table", "Capacity", massStor['cap'], journalEntry) 
            journalDb.updateColumn("Journal_Table", "Area", massStor['area'], journalEntry)
            journalDb.updateColumn("Journal_Table", "Volume", massStor['volume'], journalEntry)       
           
        if self.args.time:
            # parse time option
            time_cmd = self.range_option(self.args.time)
            time_cmd = [float(x) for x in time_cmd] # now list of floats
            
            # sanity checks
            if time_cmd[0] >= time_cmd[1] or len([x for x in time_cmd if x < 0]) != 0:
                sys.exit("ERROR: Time option out of range.")
            
            time_cmd = [x*3600 for x in time_cmd] # in seconds
        
        elif self.args.cycles:
            # parse cycles option
            cycles_cmd = self.range_option(self.args.cycles)
            cycles_cmd = [int(x) for x in cycles_cmd] # now list of integers
                    
            # sanity checks
            if cycles_cmd[0] > cycles_cmd[1] or len([x for x in cycles_cmd if x < 0]) != 0:
                sys.exit("ERROR: Cycles option out of range.")
                
        elif self.args.data:
            # parse data point option
            data_cmd = self.range_option(self.args.data)
            data_cmd = [int(x) for x in data_cmd] # now list of integers
            
            #sanity checks
            if data_cmd[0] > data_cmd[1] or len([x for x in data_cmd if x < 0]) != 0:
                sys.exit("ERROR: Data option out of range.")
        
        # fetch all data
        data = dataDb.getData()
        
        if not data.any():
            data = np.zeros((1,12))
        
        if self.args.debug:
            print("data:")
            print(data.shape)
        
        data[:,1] = data[:,1]+1 # one based cycle index
        
        # fix discharge capacity and energy being negative
        data[:,8] = np.abs(data[:,8])
        data[:,9] = np.abs(data[:,9])
    
        # fetch statistics
        stats = dataDb.getStatistics()
        
        if not stats.any():
            stats = np.zeros((1,13))
        
        if self.args.debug:
            print("stats:")
            print(stats.shape)
            
        stats[:,0] = stats[:,0]+1 # one based cycle index
        
        # fix discharge capacity and energy being negative
        stats[:,6] = np.abs(stats[:,6])
        stats[:,8] = np.abs(stats[:,8])
        
        # get number of cycles
        numberOfCycles = np.unique(stats[:,0])
            
        # filter data according to --cycles option
        if self.args.cycles:
            data = data[np.logical_and(cycles_cmd[0] <= data[:,1], data[:,1] <= cycles_cmd[1])]
            stats = stats[np.logical_and(cycles_cmd[0] <= stats[:,0], stats[:,0] <= cycles_cmd[1])]
        
        # filter data according to --data option
        elif self.args.data:
            data = data[np.logical_and(data_cmd[0] <= data[:,0], data[:,0] <= data_cmd[1])]
            stats = stats[np.logical_and(data_cmd[0] <= stats[:,2], stats[:,1] <= data_cmd[1])]
            
        # filter data according to --time option
        elif self.args.time:
            data = data[np.logical_and(time_cmd[0] <= data[:,3], data[:,3] <= time_cmd[1])]    
            
        # calc extended statistics, convert units
        expStat = export(self.args, data, numberOfCycles, stats, massStor)
        statistics = expStat.get_stats()
        
        # create figures    
        fig = plot(self.args, plots, data, numberOfCycles, statistics, massStor)
        fig.draw()
                        
        # export  
        if self.args.export:
            print("INFO: Exporting data, statistics and figures.")
            journalDb.writeJournalEntry(fileNameDate)
            expStat.writeStatisticsTable()
            expStat.writeDataTable()
            expStat.writeVoltageProfile()
            dataDb.writeMergeFileSummary()
            fig.savefigure()
            
        # show plots if quiet option not given
        if not self.args.quiet:
            fig.show_plots()

    def is_number(self, s):
        """This function tests if string s is a number."""
        try:
            float(s)
            return True
        except ValueError:
            return False
    
    def range_option(self, option):
        """This function parses the a command line option which specifies
        a data range and returns a tuple with the interval"""
        
        errormsg_not_recognised = "Error: Option not recognised."
        
        string = option.split(',')
        if len(string) == 2:
            if self.is_number(string[0]) and self.is_number(string[1]):
                interval = (string[0],string[1])
            else:
                sys.exit(errormsg_not_recognised)
        elif len(string) == 1:
            if self.is_number(string[0]):
                interval = (0,string[0])
            else:
                sys.exit(errormsg_not_recognised)
        else:    
            sys.exit(errormsg_not_recognised)
            
        return interval
    
    def plot_option(self):
        """This function parses the --plot option and returns a list of plots."""
        
        errormsg_not_recognised = "Error: Plot option not recognised."
        errormsg_range_error = "Error: Plot out of range."
        
        plots = []
        string_sequence = self.args.plot.split(',')
        for s in string_sequence:
            if self.is_number(s):
                plots.append(int(s))
            elif '-' in s:
                string_range = s.split('-')
                if self.is_number(string_range[0]) and self.is_number(string_range[1]) and len(string_range) == 2:
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