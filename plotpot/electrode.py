# -*- coding: utf-8 -*-
import sys
import numpy as np

# own modules
from plotpot.dbmanager import DbManager


class Electrode(DbManager):
    
    def __init__(self, args, showArgs, electrode = "we"):
        self.args = args
        self.showArgs = showArgs
        self.electrode = electrode
        super().__init__(showArgs['dataFile'])
        
        # set electrode properties
        self.setProperties()
        
        # set electrode data
        self.setData()
        
        # set electrode statistics
        self.setStatistics()
        
        
    ### property methods ###
    
    def setProperties(self):
        """ask electrode properties from user"""
        
        # set initial properties
        self.mass = 0         # active mass [mg]
        self.capacity = 0     # theoretical capacity [mAh/g]
        self.area = 0         # electrode area [cm²]
        self.volume = 0       # volume of electrode [µL]
        
        # mass 
        if any([x in [1,2,6,11] for x in self.showArgs['plots']]):
            self.setMass()
        # capacity
        if 10 in self.showArgs['plots']:
            self.setCapacity()
        # area
        if 12 in self.showArgs['plots']:
            self.setArea()
        # volume
        if 8 in self.showArgs['plots']:
            self.setVolume()
        
        
    def getProperties(self):
        """return dict of properties"""
        
        return {'mass': self.mass,
                'capacity': self.propCapacity,
                'area': self.area,
                'volume': self.volume}
    
    
    def __Property(self, prop, desc, unit):
        """ask electrode property from user"""
        
        if prop == 0:
            while True:
                try:
                    prop = float(input("Please give %s in [%s]: " % (desc, unit)))
                    break
                except ValueError as e:
                    continue
        else:
            print("INFO: Found old record %s %s %s in journal." % (desc, str(prop), unit))
            choice = input("Do you want to use it [Y/n]? ")
            if choice == 'n':
                while True:
                    try:
                        prop = float(input("Please give new %s in [%s]: " % (desc, unit)))
                        break
                    except ValueError as e:
                        continue
        return prop
    

    def setMass(self):
        """set electrode mass"""        
        self.mass = self.__Property(self.mass, "mass", "mg")


    def getMass(self):
        """return electrode mass in mg"""        
        return self.mass


    def setPropCapacity(self):
        """set electrode capacity"""        
        self.propCapacity = self.__Property(self.propCapacity, "capacity", "mAh/g")


    def getPropCapacity(self):
        """return electrode capacity in mAh/g"""        
        return self.propCapacity

    
    def setArea(self):
        """set electrode area"""
        self.area = self.__Property(self.area, "area of the electrode", "cm²")


    def getArea(self):
        """return electrode area in cm²"""        
        return self.area


    def setVolume(self):
        """set electode volume"""        
        self.volume = self.__Property(self.volume, "volume of electrode", "µL")

        
    def getVolume(self):
        """return electrode volume in µL"""        
        return self.volume


    ### data methods ###
    
    def setData(self):
        """fetch data from raw file"""
        
        # fetch data
        self.setVoltage()
        self.setCapacity()
        self.setEnergy()
        self.setDqDv()
        
        # assemble data dictionary
        self.data = {'voltage': self.voltage,
                     'capacity': self.capacity,
                     'energy': self.energy,
                     'dQdV': self.dqdv}
    
    
    def getData(self):
        """return dictonary with electrode data"""
        return self.data
    

    def setVoltage(self):
        """voltage"""
        if self.electrode == 'we':
            self.query('''SELECT Voltage FROM Channel_Normal_Table''')
        elif self.electrode == 'ce':
            self.query('''SELECT Voltage2 FROM Channel_Normal_Table''')
        else:
            sys.exit("ERROR: Unknown electrode %s" % self.electrode)
        self.voltage = np.squeeze(np.array(self.fetchall()))

        
    def getVoltage(self):
        """voltage"""
        return self.voltage
    
    
    def setCapacity(self):
        """capacity"""
        self.query('''SELECT Capacity FROM Channel_Normal_Table''')
        self.capacity = np.squeeze(np.array(self.fetchall()))
        # convert capacity from As to mAh/g
        if self.mass:
            self.capacity = np.abs(self.capacity / (3.6e-3 * self.mass))
        else:
            self.capacity = np.zeros(self.capacity.shape)

        
    def getCapacity(self):
        """capacity"""
        return self.capacity
    
    
    def setEnergy(self):
        """energy"""
        if self.electrode == 'we':
            self.query('''SELECT Energy FROM Channel_Normal_Table''')
        elif self.electrode == 'ce':
            self.query('''SELECT Energy2 FROM Channel_Normal_Table''')
        else:
            sys.exit("ERROR: Unknown electrode %s" % self.electrode)
        self.energy = np.squeeze(np.array(self.fetchall()))
        # convert energy from Ws to Wh/kg
        if self.mass:
            self.energy = self.energy / (3.6e-3 * self.mass)
        else:
            self.energy = np.zeros(self.energy.shape)

        
    def getEnergy(self):
        """energy"""
        return self.energy
    
    
    def setDqDv(self):
        """dQdV"""
        if self.electrode == 'we':
            self.query('''SELECT dQdV FROM Channel_Normal_Table''')
        elif self.electrode == 'ce':
            self.query('''SELECT dQdV2 FROM Channel_Normal_Table''')
        else:
            sys.exit("ERROR: Unknown electrode %s" % self.electrode)
        self.dqdv = np.squeeze(np.array(self.fetchall()))

        
    def getDqDv(self):
        """dQdV"""
        return self.dqdv
    
    
    ### per cycle statistics methods ###
    
    def setStatistics(self):
        """fetch statistics from raw file"""
        
        # fetch statistics
        self.setStatCapacity()
        
        self.statistics = {'capacity': self.statCapacity}
        
        
    def getStatistics(self):
        """return battery statistics"""
        return self.statistics

    def setStatCapacity(self):
        """capacity"""
        self.query('''SELECT Charge_Capacity,Discharge_Capacity FROM Full_Cycle_Table''')
        self.statCapacity = np.squeeze(np.array(self.fetchall()))
        # convert capacity from As to mAh/g
        if self.mass:
            self.statCapacity = np.abs(self.capacity / (3.6e-3 * self.mass))
        else:
            self.statCapacity = np.zeros(self.statCapacity.shape)

        
    def getStatCapacity(self):
        """capacity"""
        return self.capacity