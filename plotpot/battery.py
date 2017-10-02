# -*- coding: utf-8 -*-
import numpy as np

# own modules
from plotpot.dbmanager import DbManager
from plotpot.electrode import Electrode


class Battery(DbManager):
    """A class for implementing an electrochemical device"""
    
    def __init__(self, args, showArgs):
        self.args = args
        self.showArgs = showArgs
        super().__init__(showArgs['dataFile'])
        
        self.run()
        
    def run(self):
        """run battery"""
        
        print("*** Working electrode ***")
        we = Electrode(self.args, self.showArgs, False)
        print(we.getData())
        
        if self.isFullCell():
            print("*** Counter electrode ***")
            ce = Electrode(self.args, self.showArgs, True)
            print(ce.getData())
    
    
    def isFullCell(self):
        """test if voltage2 column is not zero"""
        self.query('''SELECT Voltage2 FROM Channel_Normal_Table''')
        return np.any(np.array(self.fetchall()))
        
    
    ### battery data methods ###

    
    
