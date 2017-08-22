# -*- coding: utf-8 -*-
import sys
import numpy as np
    
# import own files
from plotpot.plot import Plot
from plotpot.journal import Journal

# disable division by zero warnings
np.seterr(divide='ignore')

# plotpot class
    
class Plotpot(Journal):
    
    def __init__(self, args):
        self.args = args
        super().__init__(args)
        self.runSubcommands()        

    
    def runSubcommands(self):
        """run plotpot subcommands"""
        
        if self.args.subcommand == "show":
            self.subcommandShow()

        if self.args.subcommand == "journal":
            self.subcommandJournal()
            

    def subcommandJournal(self):
        """run journal subcommand"""
        
        # print plotpot journal file
        self.printJournal("Journal_Table")
        
        # delete journal entry
        if self.args.delete:
            self.deleteRow("Journal_Table", self.args.delete)
        
        sys.exit() 

        
    def subcommandShow(self):
        """run show subcommand"""
        
        # create plot object
        plotObj = Plot(self.args)
        
        # read file name and start datetime
        fileNameDate = plotObj.getNameAndDate()
        fileCount = plotObj.getFileCount()
        
        if fileCount > 1:
            fileNameList = list(fileNameDate)
            fileNameList[0] = self.args.filename
            fileNameDate = tuple(fileNameList)
        
        # search plotpot-journal.dat if battery exists
        searchResult = self.searchJournal(fileNameDate)
        
        # if entry not found, fetch data from data file (global or file table)
        if searchResult is None:
            journalEntry = self.getFileDetails()
            
            # treat merged file different than single file
            if fileCount > 1:
                journalList = list(journalEntry)
                journalList[1] = self.args.filename
                journalList[6] = "merged"
                journalEntry = tuple(journalList)
              
        else:
            # get mass and capapcity from journal
            journalEntry = searchResult
            self.setMetaInfo(journalEntry[6], journalEntry[7], journalEntry[8], journalEntry[9])
        
        # get selected plots
        plots = plotObj.getPlots()
        
        # ask questions
        if any([x in [1,4,5,11] for x in plots]):
            self.setMass()
        if 10 in plots:
            self.setCapacity()
        if any([x in [12] for x in plots]):
            self.setArea()
        if 6 in plots:
            self.setVolume()
            
        # create new record in journal file if previous record was not found, otherwise update meta info
        if searchResult == None:
            self.insertRow("Journal_Table", journalEntry)
        else:
            self.updateMetaInfo(fileNameDate)
        
        # export  
        if self.args.export:
            print("INFO: Exporting data, statistics and figures.")
            self.writeJournalEntry(fileNameDate)
            plotObj.export(self.getMetaInfo())
            plotObj.savefigure()
        
        # create figures    
        plotObj.drawPlots(self.args, self.getMetaInfo())
            
        # show plots if quiet option not given
        if not self.args.quiet:
            plotObj.showPlots()