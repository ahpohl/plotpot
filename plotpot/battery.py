# -*- coding: utf-8 -*-
import os, sys
import zipfile, tempfile, shutil
import numpy as np
import csv

# own modules
from plotpot.dbmanager import DbManager
from plotpot.electrode import Electrode


class Battery(DbManager):
    """A class for implementing an electrochemical device"""
    
    def __init__(self, args, globalArgs):
        self.args = args
        self.globalArgs = globalArgs
        super().__init__(globalArgs['dataFileName'])
    
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
        self.we = Electrode(self.args, self.globalArgs, "working")
        self.ce = None
 
        if self.isFullCell:
            print("*** Counter electrode ***")
            self.ce = Electrode(self.args, self.globalArgs, "counter")
          
            
    def getElectrodes(self):
        """return electrode objects"""
        return self.we, self.ce


    def exportProperties(self):
        """write battery properties to csv file"""
        properties = []
        properties.append(["working"]+self.we.getProperties())
        if self.isFullCell:
            properties.append(["counter"]+self.ce.getProperties())
        header = ",".join(["electrode", "mass", "capacity", "area", "volume", "loading"])+"\r\n"
        header += ",".join(["", "mg", "mAh/g", "cm²", "µL", "mg/cm²"])+"\r\n"
        with open(self.args.showFileName.split('.')[0]+'_properties.csv', "w", encoding='utf-8') as fh:
            fh.write(header)
            writer = csv.writer(fh)
            writer.writerows(properties)
            fh.close()
        
    
    def export(self):
        """export battery data, statistics, voltage profile and properties"""
        self.exportData()
        self.exportVoltageProfile()
        self.exportStatistics()
        self.exportProperties()
            
    
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
    

    def exportData(self):
        """write data to a csv file"""
        header = ",".join(["point", "cycle", "step", "test time", "step time", "timestamp", "temperature", 
                           "current", "WE capacity", "CE capacity", "WE voltage", "CE voltage",
                           "WE energy", "CE energy", "WE dQdV", "CE dQdV"])+"\r\n"
        header += ",".join(["", "", "", "h", "s", "s", "°C", 
                            "mA", "mAh/g", "mAh/g", "V", "V",
                            "Wh/kg", "Wh/kg", "As/V", "As/V"])+"\r\n"
    
        with open(self.args.showFileName.split('.')[0]+'_data.csv', "wb") as fh:
            fh.write(header.encode('utf-8'))
            np.savetxt(fh, self.data, delimiter=',', newline="\r\n", 
                   fmt=['%d','%d','%d','%f','%f','%d','%f',
                        '%f','%f','%f','%f','%f','%f',
                        '%f','%f','%f'])
            fh.close()
   

    def exportVoltageProfile(self):
        """create zip archive with capacity, voltage, dQdV per discharge
           and charge half cycle for easy generating plots in Origin"""
        
        # create temporary directory
        cwd = os.getcwd() # save current directory
        os.chdir(tempfile.gettempdir()) # change to tmp dir
        filestem = self.args.showFileName.split('.')[0] # create filename
        if not os.path.exists(filestem):
            os.makedirs(filestem) # create directory
        path = os.path.abspath(filestem) # change to directory
        os.chdir(path)
        
        # file header
        header = ",".join(["WE capacity", "CE capacity" ,"WE voltage", 
                                    "CE voltage", "WE dQ/dV",  "CE dQ/dV"])+"\r\n"
        header += ",".join(["mAh/g", "mAh/g", "V", "V", "As/V", "As/V"])+"\r\n"
        
        # construct data array
        if self.isFullCell:
            data = np.concatenate([self.we.capacity, self.ce.capacity, self.we.voltage, self.ce.voltage,
                                   self.we.dqdv, self.ce.dqdv], axis=1)
        else:
            zeroElements = np.zeros(self.points.shape)
            data = np.concatenate([self.we.capacity, zeroElements, self.we.voltage, zeroElements,
                                   self.we.dqdv, zeroElements], axis=1)        
        
        # loop over half cycles
        c = 0;
        for ((a,b),s,h) in zip(self.halfStatPoints, self.halfStatStep, self.halfStatCycles):
            if h % 2 == 0:
                c += 1;
            # charge
            if s > 0:
                filename = filestem+'_%03d_charge.csv' % c
            # discharge
            elif s < 0:
                filename = filestem+'_%03d_discharge.csv' % c
            # rest 
            else:
                sys.exit("ERROR: Rest cycles not supported")
            # save data
            with open(filename, "wb") as fh:
                fh.write(header.encode('utf-8'))
                np.savetxt(fh, data[a:b], delimiter=',', newline="\r\n", fmt='%f')
                fh.close()
                
        # create zip archive
        os.chdir(tempfile.gettempdir())
        zfile = filestem + '.zip'
        zipf = zipfile.ZipFile(zfile, 'w', zipfile.ZIP_DEFLATED)
        base = os.path.basename(path)
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                zipf.write(os.path.join(base, name))
        zipf.close()
        shutil.rmtree(path) # remove tmp directory
        shutil.copy(zfile, cwd)
        os.remove(zfile)
        os.chdir(cwd)
    
    
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
        self.setStatTime()
        self.setStatAverageCurrent()
        self.setStatEfficiency()
        
        # assemble statistics numpy array including electrode data
        if self.isFullCell:
            self.statistics = np.concatenate(
                    [self.statCycles,
                     self.statPoints,
                     self.statTime,
                     self.statAverageCurrent,
                     self.statEfficiency,
                     self.we.statSpecificCapacity,
                     self.ce.statSpecificCapacity,
                     self.we.statVolumetricCapacity,
                     self.ce.statVolumetricCapacity,
                     self.we.statSpecificEnergy,
                     self.ce.statSpecificEnergy,
                     self.we.statVolumetricEnergy,
                     self.ce.statVolumetricEnergy,
                     self.we.statSpecificCurrentDensity,
                     self.ce.statSpecificCurrentDensity,
                     self.we.statAreaCurrentDensity,
                     self.ce.statAreaCurrentDensity,
                     self.we.statCRate,
                     self.ce.statCRate,
                     self.we.statAverageVoltage,
                     self.ce.statAverageVoltage,
                     self.we.statHysteresis,
                     self.ce.statHysteresis], axis=1)
        
        else:
            zeroElements = np.zeros(self.statPoints.shape)
            self.statistics = np.concatenate(
                    [self.statCycles,
                     self.statPoints,
                     self.statTime,
                     self.statAverageCurrent,
                     self.statEfficiency,
                     self.we.statSpecificCapacity,
                     zeroElements,
                     self.we.statVolumetricCapacity,
                     zeroElements,
                     self.we.statSpecificEnergy,
                     zeroElements,
                     self.we.statVolumetricEnergy,
                     zeroElements,
                     self.we.statSpecificCurrentDensity,
                     zeroElements,
                     self.we.statAreaCurrentDensity,
                     zeroElements,
                     self.we.statCRate,
                     zeroElements,
                     self.we.statAverageVoltage,
                     zeroElements,
                     self.we.statHysteresis,
                     np.zeros(self.statCycles.shape)], axis=1)
        
    def getStatistics(self):
        """return battery statistics"""
        return self.statistics
    

    def exportStatistics(self):
        """write battery statistics to a csv file"""
            
        header = ",".join([
                "cycle",
                "points", "", 
                "time", "",
                "current", "", 
                "efficiency",
                "WE capacity", "", "CE capacity", "", 
                "WE capacity", "", "CE capacity", "", 
                "WE energy", "", "CE energy", "", 
                "WE energy", "", "CE energy", "", 
                "WE density", "", "CE density", "", 
                "WE density", "", "CE density", "", 
                "WE C-rate", "", "CE C-rate", "", 
                "WE voltage", "", "CE voltage","", 
                "WE hysteresis", "CE hysteresis"])+"\r\n"
        
        header += ",".join([
                 "",
                 "", "",
                 "h", "", 
                 "mA", "", 
                 "%",
                 "mAh/g", "", "mAh/g", "", 
                 "Ah/L", "", "Ah/L", "", 
                 "Wh/kg","", "Wh/kg", "", 
                 "Wh/L", "", "Wh/L", "", 
                 "mA/g", "", "mA/g", "", 
                 "mA/cm²", "", "mA/cm²", "", 
                 "h", "", "h", "", 
                 "V", "", "V", "", 
                 "V", "V"])+"\r\n"
    
        with open(self.args.showFileName.split('.')[0]+'_statistics.csv', "wb") as fh:
            fh.write(header.encode('utf-8'))
            np.savetxt(fh, self.statistics, delimiter=',', newline="\r\n", fmt='%f')
            fh.close()
            
    
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
    
    
    def setStatTime(self):
        """charge and discharge time in hours"""
        self.query('''SELECT Charge_Time,Discharge_Time FROM Full_Cycle_Table''')
        self.statTime = np.array(self.fetchall()) / 3.6e3

        
    def getStatTime(self):
        """charge and discharge time in hours"""
        return self.statTime
    
    
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