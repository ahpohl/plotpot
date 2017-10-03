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
    
        # set electrodes
        self.setIsFullCell()
        self.setElectrodes()
        
        # set data
        self.setData()
        
        # set statistics
        self.setStatistics()
        self.setHalfStatistics()
    
    
    def setIsFullCell(self):
        """test if voltage2 column is not zero"""
        self.query('''SELECT Voltage2 FROM Channel_Normal_Table''')
        self.isFullCell = np.any(np.array(self.fetchall()))
    
    
    def getIsFullCell(self):
        """return boolean if full or half cell"""
        return self.isFullCell
    
    
    def setElectrodes(self):
        """create electode objects"""
        
        print("*** Working electrode ***")
        self.we = Electrode(self.args, self.showArgs, "we")
        self.ce = None
 
        if self.isFullCell:
            print("*** Counter electrode ***")
            self.ce = Electrode(self.args, self.showArgs, "ce")
          
            
    def getElectrodes(self):
        """return electrode objects"""
        return self.we, self.ce
        
    
    ### battery data methods ###
    
    def setData(self):
        """fetch battery data from raw file"""
        
        # fetch data
        self.setPoints()
        self.setCycles()
        
        # assemble data dictionary
        self.data = {'points': self.points,
                     'cycles': self.cycles}
    
    
    def getData(self):
        """return dictonary with battery data"""
        return self.data
    
    
    def setPoints(self):
        """data points"""
        self.query('''SELECT Data_Point FROM Channel_Normal_Table''')
        self.points = np.squeeze(np.array(self.fetchall()))

        
    def getPoints(self):
        """capacity"""
        return self.points
    
    
    def setCycles(self):
        """full cycles"""
        self.query('''SELECT Full_Cycle FROM Channel_Normal_Table''')
        self.cycles = np.squeeze(np.array(self.fetchall()))

        
    def getCycles(self):
        """full cycles"""
        return self.cycles
    
   
    ### battery statistics methods ###
    
    def setStatistics(self):
        """fetch statistics from raw file"""
        
        # fetch statistics
        self.setStatCycles()
        self.setStatCycleRange()
        
        self.statistics = {'cycles': self.statCycles,
                           'range': self.statCycleRange}
        
        
    def getStatistics(self):
        """return battery statistics"""
        return self.statistics
        
    
    def setStatCycles(self):
        """full cycle statistics"""
        self.query('''SELECT Full_Cycle FROM Full_Cycle_Table''')
        self.statCycles = np.squeeze(np.array(self.fetchall()))

        
    def getStatCycles(self):
        """full cycle statistics"""
        return self.statCycles
    
    
    def setStatCycleRange(self):
        """start and end data point of cycle"""
        self.query('''SELECT Cycle_Start,Cycle_End FROM Full_Cycle_Table''')
        self.statCycleRange = np.array(self.fetchall())

        
    def getStatCycleRange(self):
        """start and end data point of cycle"""
        return self.statCycleRange
    
    
    ### half cycle statistics methods ###
    
    def setHalfStatistics(self):
        """fetch half cycle statistics from raw file"""
        
        # fetch statistics
        self.setHalfStatCycles()
        self.setHalfStatRange()
        
        self.halfStatistics = {'cycles': self.halfStatCycles,
                               'points': self.halfStatRange}
        
        
    def getHalfStatistics(self):
        """return half cycle battery statistics"""
        return self.halfStatistics
    
    
    def setHalfStatCycles(self):
        """half cycles"""
        self.query('''SELECT Half_Cycle FROM Half_Cycle_Table''')
        self.halfStatCycles = np.squeeze(np.array(self.fetchall()))

        
    def getHalfStatCycles(self):
        """half cycles"""
        return self.halfStatCycles
    
    
    def setHalfStatRange(self):
        """start and end data point of half cycle"""
        self.query('''SELECT Cycle_Start,Cycle_End FROM Half_Cycle_Table''')
        self.halfStatRange = np.array(self.fetchall())
        
    def getHalfStatRange(self):
        """start and end data point of half cycle"""
        return self.halfStatRange