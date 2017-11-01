# -*- coding: utf-8 -*-
import sys, os
import subprocess
from distutils.spawn import find_executable
import sqlite3

# import own files
from plotpot.plot import Plot
from plotpot.journal import Journal
from plotpot.battery import Battery
from plotpot.dbmanager import DbManager


class Plotpot(object):
    
    def __init__(self, args):
        self.args = args
        self.setConvpotPath()
        self.setGlobalArgs()
        
        if self.args.subcommand == "show":
            self.subcommandShow()

        if self.args.subcommand == "journal":
            self.subcommandJournal()
            
        if self.args.subcommand == "merge":
            self.subcommandMerge()
            

    def subcommandShow(self):
        """run show subcommand"""
        
        # call convpot to convert raw data
        self.callConvpot()
        
        # create battery object
        bat = Battery(self.args, self.globalArgs)
        
        # create figures
        plot = Plot(self.args, bat)
        plot.drawPlots()
        
        # export data and statistics  
        if self.args.showExport:
            print("INFO: Exporting data, statistics and figures.")
            bat.export()
            plot.savePlots()
        
        # show plots if quiet option not given
        if not self.args.showQuiet:
            plot.showPlots()

            
    def subcommandJournal(self):
        """run journal subcommand"""
        
        # create journal object
        journal = Journal(self.args)
        
        # display plotpot journal file on screen
        if not (self.args.journalDelete or self.args.journalExport or 
                self.args.journalShow):
            journal.displayJournal()

        # delete journal entry
        if self.args.journalDelete:
            journal.deleteJournalRow()
            
        # export journal
        if self.args.journalExport:
            journal.exportJournal()
            #journal.exportMergeFiles()
            
        # display merged files
        if self.args.journalShow:
            journal.displayMergeFiles()
        
        
    def subcommandMerge(self):
        """run merge subcommand"""

        # # construct call to convpot
        convpotArgs = []
        convpotArgs.append(self.convpotPath)
        
        # verbose arg
        if self.args.verbose:
            convpotArgs.append("-{0}".format(self.args.verbose * 'v'))
        
        # output filename
        if self.args.mergeOutput:
            convpotArgs.extend(["-o", self.args.mergeOutput])
        
        # merge list
        if self.args.mergeList:
            convpotArgs.extend(["-m", self.args.mergeList])
        
        # files given after merge subcommand
        elif self.args.mergeFileNames:
            convpotArgs.extend(self.args.mergeFileNames)
        
        # call external Convpot program
        if len(convpotArgs) > 1:
            try:
                subprocess.check_call(convpotArgs)
            except subprocess.CalledProcessError as e:
                sys.exit(e)
        
        # journal
        journal = Journal(self.args, self.globalArgs, "working")
        if journal.batIsFullCell:
            Journal(self.args, self.globalArgs, "counter")
    
    
    ### internal methods ###

    def setGlobalArgs(self):
        """set global arguments"""
        self.globalArgs = None

        # show subcommand
        if self.args.subcommand == "show":
            try:
                open(os.path.abspath(self.args.showFileName), "r")
            except IOError as e:
                sys.exit(e)
                
            self.globalArgs = {'dataFileName': self.args.showFileName.rsplit('.')[0]+'.sqlite',
                               'plots': self.getPlotsOption(), 
                               'time': self.getTimeOption(),
                               'points': self.getDataOption(),
                               'cycles': self.getCyclesOption()}
        
        # merge subcommand
        elif self.args.subcommand == "merge":
            if self.args.mergeOutput:
                self.globalArgs = {'dataFileName': self.args.mergeOutput}
                if self.globalArgs['dataFileName'].split('.')[-1] != "sqlite":
                    self.globalArgs['dataFileName'] += ".sqlite"
                
            elif self.args.mergeList:
                self.globalArgs = {'dataFileName': self.args.mergeList.split('.')[0]+".sqlite"}
            
            elif self.args.mergeFileNames:
                self.globalArgs = {'dataFileName': self.args.mergeFileNames[0].split('.')[0]+".sqlite"}
            
    
    def getGlobalArgs(self):
        """return global args"""
        return self.globalArgs


    def setConvpotPath(self):
        """check if Convpot is installed and return path of executable"""
        
        # search path for Convpot program
        self.convpotPath = find_executable("convpot")
        
        # search in current dir
        if self.convpotPath is None:
            self.convpotPath = find_executable("convpot", sys.argv[0])
        
        if not self.convpotPath:
            sys.exit("ERROR: Convpot program not installed.")
            
        # test if convpot is executable
        if not os.access(self.convpotPath, os.X_OK):
            sys.exit("ERROR: Convpot program not executable.")
            

    def getConvpotPath(self):
        """return Convpot path"""
        return self.convpotPath

    
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
        
        errormsg_not_recognised = "ERROR: Option not recognised."
        
        string = option.split(',')
        if len(string) == 2:
            if self.isNumber(string[0]) and self.isNumber(string[1]):
                interval = (string[0],string[1])
            else:
                sys.exit(errormsg_not_recognised)
        elif len(string) == 1:
            if self.isNumber(string[0]):
                if self.args.showTime is not None:    
                    interval = (0,string[0])
                else:
                    interval = (1,string[0])
            else:
                sys.exit(errormsg_not_recognised)
        else:    
            sys.exit(errormsg_not_recognised)
        
        return interval
    
    
    def getCyclesOption(self):
        """get cycles from --cycles option"""
        
        # init cycles
        cycles = None
        
        if self.args.showCycles:
            # parse cycles option
            cycles = self.parseRange(self.args.showCycles)
            cycles = [int(x) for x in cycles] # now list of integers
            
            # sanity checks
            if cycles[0] > cycles[1] or len([x for x in cycles if x <= 0]) != 0:
                sys.exit("ERROR: Cycles option out of range.")
        
        return cycles
    
                
    def getDataOption(self):
        """get data points from --data option"""
    
        # init points
        points = None
    
        if self.args.showData:
            # parse data point option
            points = self.parseRange(self.args.showData)
            points = [int(x) for x in points] # now list of integers
            
            #sanity checks
            if points[0] > points[1] or len([x for x in points if x < 0]) != 0:
                sys.exit("ERROR: Data option out of range.")
        
        return points
    
    
    def getTimeOption(self):
        """get time from --time option"""
        
        # init time
        time = None
        
        if self.args.showTime:
            # parse time option
            time = self.parseRange(self.args.showTime)
            time = [float(x) for x in time] # now list of floats
            
            # sanity checks
            if time[0] >= time[1] or len([x for x in time if x < 0]) != 0:
                sys.exit("ERROR: Time option out of range.")
        
        return time


    def getPlotsOption(self):
        """This function parses the --plot option and returns a list of plots."""
        
        errormsg_not_recognised = "ERROR: Plot option not recognised."
        errormsg_range_error = "ERROR: Plot number out of range."
        
        plots = []
        string_sequence = self.args.showPlot.split(',')
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
    
    
    def callConvpot(self):
        """create the sqlite database by calling Convpot to convert raw
        data. Check if sqlite file is up-to-date and skip conversion 
        if necessary."""
        
        # get extension of raw file
        rawFileExtension = self.args.showFileName.rsplit('.')[1]
        
        # test if sqlite file needs updating
        isUpToDate = self.checkRawFileSize()
        
        if (self.args.showForce or not isUpToDate) and (rawFileExtension != "sqlite"):
        
            # construct call to convpot
            convpotArgs = []
            convpotArgs.append(self.convpotPath)
        
            # verbose arg
            if self.args.verbose:
                convpotArgs.append("-{0}".format(self.args.verbose * 'v'))
                
            # filename arg 
            convpotArgs.append(self.args.showFileName)
        
            # call external Convpot program
            try:
                subprocess.check_call(convpotArgs)
            except subprocess.CalledProcessError as e:
                sys.exit(e)
                
                
    def checkRawFileSize(self):
        """Check file size of raw file and compare with size saved in 
           sqlite file. Return True if file is up-to-date and False
           if sizes differ."""
           
        db = DbManager(self.globalArgs['dataFileName'])

        currentSize = 0
        with open(self.args.showFileName, 'r') as fh:
            fh.seek(0, os.SEEK_END)
            currentSize = fh.tell()
            fh.close()
        
        listOfVars = ["File_Size"]
        select_query = '''SELECT {0} FROM Global_Table'''.format(','.join(listOfVars))
        try:
            db.query(select_query)
        except sqlite3.OperationalError as e:
            return False
        
        previousSize = int(db.fetchone()[0])
            
        if self.args.verbose:
            print("currentSize: %ld, previousSize: %ld" % (currentSize, previousSize))
        
        if currentSize == previousSize:
            if self.args.verbose:
                print("File size match!")
            return True 
        else:
            return False