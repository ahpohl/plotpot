# -*- coding: utf-8 -*-
import sys
import numpy as np
    
# import own files
from plotpot.plot import Plot
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
        jourObj = Journal(self.args)
        
        # print plotpot journal file
        jourObj.printJournal("Journal_Table")
        
        # delete journal entry
        if self.args.delete:
            jourObj.deleteRow("Journal_Table", self.args.delete)
        
        sys.exit() 

        
    def subcommandShow(self):
        """run show subcommand"""
        
        # create plot object
        plotObj = Plot(self.args)
        
        sys.exit()
        
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