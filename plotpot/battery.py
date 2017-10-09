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
        self.setTestTime()
        self.setCurrent()
        self.setTemperature()
        
        # assemble data dictionary
        self.data = {'points': self.points,
                     'cycles': self.cycles,
                     'testtime': self.testTime,
                     'current': self.current,
                     'temperature': self.temperature}
    
    
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
    
    
    def setTestTime(self):
        """test time in hours"""
        self.query('''SELECT Test_Time FROM Channel_Normal_Table''')
        self.testTime = np.squeeze(np.array(self.fetchall())) / 3.6e3
    
    
    def getTestTime(self):
        """test time in hours"""
        return self.testTime


    def setCurrent(self):
        """current in mA"""
        self.query('''SELECT Current FROM Channel_Normal_Table''')
        self.current = np.squeeze(np.array(self.fetchall())) * 1e3
    
    
    def getCurrent(self):
        """test time in hours"""
        return self.current
   
    
    def setTemperature(self):
        """Temperature in °C"""
        self.query('''SELECT Aux_Channel FROM Channel_Normal_Table''')
        self.temperature = np.squeeze(np.array(self.fetchall()))
    
    
    def getTemperature(self):
        """Temperature in °C"""
        return self.temperature
    
    
    ### battery statistics methods ###
    
    def setStatistics(self):
        """fetch statistics from raw file"""
        
        # fetch statistics
        self.setStatCycles()
        self.setStatPoints()
        
        self.statistics = {'cycles': self.statCycles,
                           'points': self.statPoints}
        
        
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
    
    
    def setStatPoints(self):
        """start and end data point of cycle"""
        self.query('''SELECT Cycle_Start,Cycle_End FROM Full_Cycle_Table''')
        self.statPoints = np.array(self.fetchall())

        
    def getStatPoints(self):
        """start and end data point of cycle"""
        return self.statPoints
    
    
    ### half cycle statistics methods ###
    
    def setHalfStatistics(self):
        """fetch half cycle statistics from raw file"""
        
        # fetch statistics
        self.setHalfStatCycles()
        self.setHalfStatPoints()
        self.setHalfStatStep()
        
        self.halfStatistics = {'cycles': self.halfStatCycles,
                               'points': self.halfStatPoints,
                               'step': self.halfStatStep}
        
        
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
    
    
    def setHalfStatPoints(self):
        """start and end data point of half cycle"""
        self.query('''SELECT Cycle_Start,Cycle_End FROM Half_Cycle_Table''')
        self.halfStatPoints = np.array(self.fetchall())
    
    
    def getHalfStatPoints(self):
        """start and end data point of half cycle"""
        return self.halfStatPoints
    
    
    def setHalfStatStep(self):
        """step index of half cycle"""
        self.query('''SELECT Step_Index FROM Half_Cycle_Table''')
        self.halfStatStep = np.squeeze(np.array(self.fetchall()))
    
    
    def getHalfStatStep(self):
        """step index of half cycle"""
        return self.halfStatStep
    