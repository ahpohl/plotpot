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
    
class Plotpot(object):
    
    def __init__(self, args):
        self.args = args
        self.runSubcommands()        

    
    def runSubcommands(self):
        """run plotpot subcommands"""
        
        if self.args.subcommand == "show":
            self.subcommandShow()

        if self.args.subcommand == "journal":
            self.subcommandJournal()
            

    def subcommandJournal(self):
        """run journal subcommand"""
        
        # create journal object
        jour = Journal(self.args)
        
        # print plotpot journal file
        jour.printJournal("Journal_Table")
        
        # delete journal entry
        if self.args.delete:
            jour.deleteRow("Journal_Table", self.args.delete)
        
        sys.exit() 

        
    def subcommandShow(self):
        """run show subcommand"""
        
        # create plot object
        plotObj = Plot(self.args)
            
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