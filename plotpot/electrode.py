# -*- coding: utf-8 -*-
import numpy as np

# own modules
from plotpot.dbmanager import DbManager


class Electrode(DbManager):
    
    def __init__(self, args, showArgs, fullCell = False):
        self.args = args
        self.showArgs = showArgs
        self.fullCell = fullCell
        super().__init__(showArgs['dataFile'])
        
        # set electrode properties
        self.setProperties()
        
        # set electrode data
        self.setData()
        
        
    ### property methods ###
    
    def setProperties(self):
        """ask electrode properties from user"""
        
        # set initial properties
        self.mass = 0         # active mass [mg]
        self.capacity = 0     # theoretical capacity [mAh/g]
        self.area = 0         # electrode area [cm²]
        self.volume = 0       # volume of electrode [µL]
        
        # mass 
        if any([x in [1,4,5,11] for x in self.showArgs['plots']]):
            self.setMass()
        # capacity
        if 10 in self.showArgs['plots']:
            self.setCapacity()
        # area
        if 12 in self.showArgs['plots']:
            self.setArea()
        # volume
        if 6 in self.showArgs['plots']:
            self.setVolume()
    
    
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
        if not self.fullCell:
            self.query('''SELECT Voltage FROM Channel_Normal_Table''')
        else:
            self.query('''SELECT Voltage2 FROM Channel_Normal_Table''')
        self.voltage = np.array(self.fetchall())

        
    def getVoltage(self):
        """voltage"""
        return self.voltage
    
    
    def setCapacity(self):
        """capacity"""
        self.query('''SELECT Capacity FROM Channel_Normal_Table''')
        self.capacity = np.array(self.fetchall())
        # convert capacity from As to mAh/g
        if self.mass:
            self.capacity = self.capacity / (3.6e-3 * self.mass)
        else:
            self.capacity = np.zeros(self.capacity.shape)

        
    def getCapacity(self):
        """capacity"""
        return self.capacity
    
    
    def setEnergy(self):
        """energy"""
        if not self.fullCell:
            self.query('''SELECT Energy FROM Channel_Normal_Table''')
        else:
            self.query('''SELECT Energy2 FROM Channel_Normal_Table''')
        self.energy = np.array(self.fetchall())
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
        if not self.fullCell:
            self.query('''SELECT dQdV FROM Channel_Normal_Table''')
        else:
            self.query('''SELECT dQdV2 FROM Channel_Normal_Table''')
        self.dqdv = np.array(self.fetchall())

        
    def getDqDv(self):
        """dQdV"""
        return self.dqdv
    
    
    ### per cycle statistics methods ###
    
    
    