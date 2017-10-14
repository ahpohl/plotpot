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
        self.theoCapacity = 0     # theoretical capacity [mAh/g]
        self.area = 0         # electrode area [cm²]
        self.volume = 0       # volume of electrode [µL]
        
        # mass 
        if any([x in [1,2,6,8,10,12] for x in self.showArgs['plots']]):
            self.setMass()
        # capacity
        if 12 in self.showArgs['plots']:
            self.setTheoCapacity()
        # area
        if 11 in self.showArgs['plots']:
            self.setArea()
        # volume
        if any([x in [7,9] for x in self.showArgs['plots']]):
            self.setVolume()
        
        
    def getProperties(self):
        """return dict of properties"""
        
        return {'mass': self.mass,
                'theoCapacity': self.theoCapacity,
                'area': self.area,
                'volume': self.volume}
    
    
    def __Property(self, prop, desc, unit):
        """ask electrode property from user"""
        
        if prop == 0:
            while True:
                try:
                    prop = float(input("Please give %s in [%s]: " % (desc, unit)))
                    if prop == 0:
                        continue
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
                        if prop == 0:
                            continue
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


    def setTheoCapacity(self):
        """set electrode capacity"""        
        self.theoCapacity = self.__Property(self.theoCapacity, "capacity", "mAh/g")


    def getTheoCapacity(self):
        """return electrode capacity in mAh/g"""        
        return self.theoCapacity

    
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
        self.voltage = np.array(self.fetchall())

        
    def getVoltage(self):
        """voltage"""
        return self.voltage
    
    
    def setCapacity(self):
        """capacity"""
        self.query('''SELECT Capacity FROM Channel_Normal_Table''')
        self.capacity = np.array(self.fetchall())
        # convert capacity from As to mAh/g
        if self.mass is not 0:
            self.capacity = np.abs(self.capacity / (3.6e-3 * self.mass))

        
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
        self.energy = np.array(self.fetchall())
        # convert energy from Ws to Wh/kg
        if self.mass is not 0:
            self.energy = self.energy / (3.6e-3 * self.mass)

        
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
        self.dqdv = np.array(self.fetchall())

        
    def getDqDv(self):
        """dQdV"""
        return self.dqdv
    
    
    ### per cycle statistics methods ###
    
    def setStatistics(self):
        """fetch statistics from raw file"""
        
        # calculate full cycle statistics
        self.setStatSpecificCapacity()
        self.setStatVolumetricCapacity()
        self.setStatSpecificEnergy()
        self.setStatVolumetricEnergy()
        self.setStatSpecificCurrentDensity()
        self.setStatAreaCurrentDensity()
        self.setStatCRate()
        self.setStatAverageVoltage()
        self.setStatHysteresis()
        
        # export statistics into a dictionary of numpy arrays
        self.statistics = {'specificCapacity': self.statSpecificCapacity,
                           'volumetricCapacity': self.statVolumetricCapacity,
                           'specificEnergy': self.statSpecificEnergy,
                           'volumetricEnergy': self.statVolumetricEnergy,
                           'specificCurrentDensity': self.statSpecificCurrentDensity,
                           'areaCurrentDensity': self.statAreaCurrentDensity,
                           'CRate': self.statCRate,
                           'averageVoltage': self.statAverageVoltage,
                           'hysteresis': self.statHysteresis}
        
        
    def getStatistics(self):
        """return battery statistics"""
        return self.statistics
    

    def setStatSpecificCapacity(self):
        """specific capacity"""
        self.query('''SELECT Charge_Capacity,Discharge_Capacity FROM Full_Cycle_Table''')
        self.statSpecificCapacity = np.array(self.fetchall())
        # convert capacity from As to mAh/g
        if self.mass is not 0:
            self.statSpecificCapacity = np.abs(self.statSpecificCapacity / (3.6e-3 * self.mass))

        
    def getStatSpecificCapacity(self):
        """specific capacity"""
        return self.statSpecificCapacity
    
    
    def setStatVolumetricCapacity(self):
        """volumetric capacity"""
        self.query('''SELECT Charge_Capacity,Discharge_Capacity FROM Full_Cycle_Table''')
        self.statVolumetricCapacity = np.array(self.fetchall())
        # convert capacity from As to Ah/L
        if self.volume is not 0:
            self.statVolumetricCapacity = np.abs(self.statVolumetricCapacity / (3.6e-3 * self.volume))

        
    def getStatVolumetricCapacity(self):
        """volumetric capacity"""
        return self.statVolumetricCapacity
    

    def setStatSpecificEnergy(self):
        """specific capacity"""
        if self.electrode == 'we':
            self.query('''SELECT Charge_Energy,Discharge_Energy FROM Full_Cycle_Table''')
        elif self.electrode == 'ce':
            self.query('''SELECT Charge_Energy2,Discharge_Energy2 FROM Full_Cycle_Table''')
        else:
            sys.exit("ERROR: Unknown electrode %s" % self.electrode)
        self.statSpecificEnergy = np.array(self.fetchall())
        # convert capacity from Ws to Wh/kg
        if self.mass is not 0:
            self.statSpecificEnergy = np.abs(self.statSpecificEnergy / (3.6e-3 * self.mass))

        
    def getStatSpecificEnergy(self):
        """specific capacity"""
        return self.statSpecificEnergy
    
    
    def setStatVolumetricEnergy(self):
        """volumetric capacity"""
        if self.electrode == 'we':
            self.query('''SELECT Charge_Energy,Discharge_Energy FROM Full_Cycle_Table''')
        elif self.electrode == 'ce':
            self.query('''SELECT Charge_Energy2,Discharge_Energy2 FROM Full_Cycle_Table''')
        else:
            sys.exit("ERROR: Unknown electrode %s" % self.electrode)
        self.statVolumetricEnergy = np.array(self.fetchall())
        # convert capacity from Ws to Wh/L
        if self.volume is not 0:
            self.statVolumetricEnergy = np.abs(self.statVolumetricEnergy / (3.6e-3 * self.volume))

        
    def getStatVolumetricEnergy(self):
        """volumetric capacity"""
        return self.statVolumetricEnergy
    
    
    def setStatSpecificCurrentDensity(self):
        """specific current density"""

        # get average current in [µA]
        self.query('''SELECT Charge_Current,Discharge_Current FROM Full_Cycle_Table''')
        averageCurrent = np.array(self.fetchall()) * 1e6
        
        # calculate specific current density in [µA mg-1] = [mA g-1]
        if self.mass is not 0:
            self.statSpecificCurrentDensity = np.abs(averageCurrent / self.mass)
        else:
            self.statSpecificCurrentDensity = np.zeros(averageCurrent.shape)

            
    def getStatSpecificCurrentDensity(self):
        """specific current density"""
        return self.statSpecificCurrentDensity
    

    def setStatAreaCurrentDensity(self):
        """area current density"""

        # get average current in [mA]
        self.query('''SELECT Charge_Current,Discharge_Current FROM Full_Cycle_Table''')
        self.statAreaCurrentDensity = np.array(self.fetchall()) * 1e3
        
        # calculate area current density in [mA cm-1]
        if self.area is not 0:
            self.statAreaCurrentDensity = np.abs(self.statAreaCurrentDensity / self.area)

            
    def getStatAreaCurrentDensity(self):
        """area current density"""
        return self.statSpecificCurrentDensity


    def setStatCRate(self):
        """C-rate"""

        # get average current in [A]
        self.query('''SELECT Charge_Current,Discharge_Current FROM Full_Cycle_Table''')
        self.statCRate = np.array(self.fetchall())
        
        # calculate theoretical capacity
        # C = m * Ctheo [mg * mAh/g = Ah *1e-6]
        # calculate C-rate / t
        # t = C / I [Ah / A = h]
        if (self.mass and self.theoCapacity) is not 0:
            self.statCRate = np.abs(self.mass * self.theoCapacity * 1e-6 / self.statCRate)
            
            
    def getStatCRate(self):
        """C-rate"""
        return self.statCRate
    

    def setStatAverageVoltage(self):
        """average voltage"""
        if self.electrode == 'we':
            self.query('''SELECT Charge_Voltage,Discharge_Voltage FROM Full_Cycle_Table''')
        elif self.electrode == 'ce':
            self.query('''SELECT Charge_Voltage2,Discharge_Voltage2 FROM Full_Cycle_Table''')
        else:
            sys.exit("ERROR: Unknown electrode %s" % self.electrode)
        self.statAverageVoltage = np.array(self.fetchall())
        
            
    def getStatAverageVoltage(self):
        """average voltage"""
        return self.statAverageVoltage    


    def setStatHysteresis(self):
        """voltage hysteresis"""
        if self.electrode == 'we':
            self.query('''SELECT Hysteresis FROM Full_Cycle_Table''')
        elif self.electrode == 'ce':
            self.query('''SELECT Hysteresis2 FROM Full_Cycle_Table''')
        else:
            sys.exit("ERROR: Unknown electrode %s" % self.electrode)
        self.statHysteresis = np.array(self.fetchall())
        
            
    def getStatHysteresis(self):
        """voltage hysteresis"""
        return self.statHysteresis