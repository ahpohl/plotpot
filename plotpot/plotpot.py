# -*- coding: utf-8 -*-
import sys
import numpy as np
    
# import own files
from plotpot.plot import Plot
from plotpot.export import Export
from plotpot.data import Data
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
        Journal.printJournal(self, "Journal_Table")
        
        # delete journal entry
        if self.args.delete:
            Journal.deleteRow(self, "Journal_Table", self.args.delete)
        
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
            journalEntry = plotObj.getFileDetails()
            
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
        
        # parse plot option
        plots = self.getPlots()
        
        # ask questions
        if any([x in [1,4,5,11] for x in plots]):
            self.setMass()
        if 10 in plots:
            self.setCapacity()
        if any([x in [12] for x in plots]):
            self.setArea()
        if 6 in plots:
            self.setVolume()
            
        # create new record in journal file if previous record was not found, otherwise update mass
        if searchResult == None:
            self.insertRow("Journal_Table", journalEntry, self.getMetaInfo())
        else:
            self.updateColumn("Journal_Table", "Mass", massStor['mass'], journalEntry)
            self.updateColumn("Journal_Table", "Capacity", massStor['cap'], journalEntry) 
            self.updateColumn("Journal_Table", "Area", massStor['area'], journalEntry)
            self.updateColumn("Journal_Table", "Volume", massStor['volume'], journalEntry)       
            
        sys.exit()
        
        # calc extended statistics, convert units
        expStat = export(self.args, self.data, numberOfCycles, self.stats, massStor)
        statistics = expStat.get_stats()
        
        # create figures    
        fig = plot(self.args, plots, data, numberOfCycles, statistics, massStor)
        fig.draw()
                        
        # export  
        if self.args.export:
            print("INFO: Exporting data, statistics and figures.")
            self.journal.writeJournalEntry(fileNameDate)
            expStat.writeStatisticsTable()
            expStat.writeDataTable()
            expStat.writeVoltageProfile()
            dataDb.writeMergeFileSummary()
            fig.savefigure()
            
        # show plots if quiet option not given
        if not self.args.quiet:
            fig.show_plots()