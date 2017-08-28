# -*- coding: utf-8 -*-
import sys
import numpy as np
    
# import own files
from plotpot.plot import Plot
from plotpot.journal import Journal

    
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

        # delete journal entry
        rc = None
        if self.args.delete:
            rc = jourObj.deleteRowJournalTable(self.args.delete)
        
        # print plotpot journal file
        jourObj.printJournalTable()
        
        # print outcome of delete
        if rc is not None:
            print(rc)
        
        sys.exit() 

        
    def subcommandShow(self):
        """run show subcommand"""
        
        # create plot object
        plotObj = Plot(self.args)

        # create figures    
        plotObj.drawPlots()
        
        # export  
        if self.args.export:
            print("INFO: Exporting data, statistics and figures.")
            plotObj.exportData()
            plotObj.saveFigure()
            
        # show plots if quiet option not given
        if not self.args.quiet:
            plotObj.showPlots()