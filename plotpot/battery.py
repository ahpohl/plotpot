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
        self.setStepIndex()
        self.setTestTime()
        self.setStepTime()
        self.setDateTime()
        self.setCurrent()
        self.setTemperature()
        
        # assemble data numpy array including electrode data
        if self.isFullCell:
            self.data = np.concatenate([self.points, self.cycles, self.stepIndex, self.testTime,
                                        self.stepTime, self.dateTime, self.temperature, self.current,
                                        self.we.capacity, self.ce.capacity, self.we.voltage, self.ce.voltage,
                                        self.we.energy, self.ce.energy, self.we.dqdv, self.ce.dqdv], axis=1)
        else:
            zeroElements = np.zeros(self.points.shape)
            self.data = np.concatenate([self.points, self.cycles, self.stepIndex, self.testTime,
                                        self.stepTime, self.dateTime, self.temperature, self.current,
                                        self.we.capacity, zeroElements, self.we.voltage, zeroElements,
                                        self.we.energy, zeroElements, self.we.dqdv, zeroElements], axis=1)
    
    
    def getData(self):
        """return battery data"""
        return self.data
    

    def exportData(self, bat):
        """write data to a csv file"""    
        with open(self.args.filename.split('.')[0]+'_data.csv', 'w') as fh:
            header = ("point", "cycle", "step", "test time", "step time", "timestamp", "temperature", 
                      "current", "WE capacity", "CE capacity", "WE voltage", "CE voltage",
                      "WE energy", "CE energy", "WE dQdV", "CE dQdV")
            units = ("", "", "", "h", "s", "s", "°C", 
                     "mA", "mAh/g", "mAh/g", "V", "V",
                     "Wh/kg", "Wh/kg", "As/V", "As/V")           
            fh.write(",".join(header)+"\r\n")
            fh.write(",".join(units)+"\r\n")
            fh.close()
        np.savetxt()
    
    
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
    
    
    def setStepIndex(self):
        """step index"""
        self.query('''SELECT Step_Index FROM Channel_Normal_Table''')
        self.stepIndex = np.array(self.fetchall())

        
    def getStepIndex(self):
        """full cycles"""
        return self.stepIndex
    
    
    def setTestTime(self):
        """test time in hours"""
        self.query('''SELECT Test_Time FROM Channel_Normal_Table''')
        self.testTime = np.array(self.fetchall()) / 3.6e3
    
    
    def getTestTime(self):
        """test time in hours"""
        return self.testTime


    def setStepTime(self):
        """step time in seconds"""
        self.query('''SELECT Step_Time FROM Channel_Normal_Table''')
        self.stepTime = np.array(self.fetchall())
    
    
    def getStepTime(self):
        """step time in hours"""
        return self.stepTime
    

    def setDateTime(self):
        """time stamp in seconds since epoch"""
        self.query('''SELECT DateTime FROM Channel_Normal_Table''')
        self.dateTime = np.array(self.fetchall())
    
    
    def getDateTime(self):
        """time stamp in seconds since epoch"""
        return self.dateTime


    def setCurrent(self):
        """current in mA"""
        self.query('''SELECT Current FROM Channel_Normal_Table''')
        self.current = np.array(self.fetchall()) * 1e3
    
    
    def getCurrent(self):
        """test time in hours"""
        return self.current
   
    
    def setTemperature(self):
        """Temperature in °C"""
        self.query('''SELECT Aux_Channel FROM Channel_Normal_Table''')
        self.temperature = np.array(self.fetchall())
    
    
    def getTemperature(self):
        """Temperature in °C"""
        return self.temperature
    
    
    ### battery statistics methods ###
    
    def setStatistics(self):
        """fetch statistics from raw file"""
        
        # fetch statistics
        self.setStatCycles()
        self.setStatPoints()
        self.setStatAverageCurrent()
        self.setStatEfficiency()
        
        self.statistics = {'cycles': self.statCycles,
                           'points': self.statPoints,
                           'averageCurrent': self.statAverageCurrent,
                           'efficiency': self.statEfficiency}
        
        
    def getStatistics(self):
        """return battery statistics"""
        return self.statistics
        
    
    def setStatCycles(self):
        """full cycle statistics"""
        self.query('''SELECT Full_Cycle FROM Full_Cycle_Table''')
        self.statCycles = np.array(self.fetchall())

        
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
    
    
    def setStatAverageCurrent(self):
        """average current in mA"""
        self.query('''SELECT Charge_Current,Discharge_Current FROM Full_Cycle_Table''')
        self.statAverageCurrent = np.array(self.fetchall()) * 1e3       
        
    
    def getStatAverageCurrent(self):
        """average current in mA"""
        return self.statAverageCurrent
    
    
    def setStatEfficiency(self):
        """coulombic efficiency in %"""
        self.query('''SELECT Efficiency FROM Full_Cycle_Table''')
        self.statEfficiency = np.array(self.fetchall()) * 100      
        
    
    def getStatEfficiency(self):
        """coulombic efficiency in %"""
        return self.statEfficiency
    
    
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
        self.halfStatCycles = np.array(self.fetchall())

        
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
        self.halfStatStep = np.array(self.fetchall())
    
    
    def getHalfStatStep(self):
        """step index of half cycle"""
        return self.halfStatStep