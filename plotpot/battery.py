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
    
    
    def isFullCell(self):
        """test if voltage2 column is not zero"""
        self.query('''SELECT Voltage2 FROM Channel_Normal_Table''')
        return np.any(np.array(self.fetchall()))
        
    
    ### battery data methods ###
    
     def setData(self):
        """fetch battery data from raw file"""
        
        # fetch data
        self.setPoints()
        
        # assemble data dictionary
        self.data = {'points': self.points}
    
    
    def getData(self):
        """return dictonary with battery data"""
        return self.data
    
    
    def setPoints(self):
        """data points"""
        self.query('''SELECT Data_Point FROM Channel_Normal_Table''')
        self.points = np.array(self.fetchall())

        
    def getPoints(self):
        """capacity"""
        return self.points
    
    
    def setCycles(self):
        """full cycles"""
        self.query('''SELECT Full_Cycle FROM Channel_Normal_Table''')
        self.cycles = np.array(self.fetchall())

        
    def getCycles(self):
        """full cycles"""
        return self.cycles
    
    
    
    
    

    
    
