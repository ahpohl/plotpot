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
        
        # set electrode half cycle statistics
        self.setHalfStatistics()
        
        
    ### property methods ###
    
    def setProperties(self):
        """ask electrode properties from user"""
        
        # set initial properties
        self.mass = 0         # active mass [mg]
        self.capacity = 0     # theoretical capacity [mAh/g]
        self.area = 0         # electrode area [cm²]
        self.volume = 0       # volume of electrode [µL]
        
        # mass 
        if any([x in [1,2,6,8,10] for x in self.showArgs['plots']]):
            self.setMass()
        # capacity
        if 11 in self.showArgs['plots']:
            self.setCapacity()
        # area
        if 12 in self.showArgs['plots']:
            self.setArea()
        # volume
        if any([x in [7,9] for x in self.showArgs['plots']]):
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
    
    
    ### per half cycle statistics methods ###
    
    def setHalfStatistics(self):
        """fetch half cycle statistics from raw file"""
        
        # fetch half statistics
        self.setHalfStatCurrent()

        self.halfStatistics = {'averageCurrent': self.halfStatCurrent}
        
        
    def getStatistics(self):
        """get half cycle battery statistics"""
        return self.halfStatistics
    
    
    def setHalfStatCurrent(self):
        """average current per half cycle"""
        
        # get current in mA
        self.query('''SELECT Current FROM Channel_Normal_Table''')
        current = np.squeeze(np.array(self.fetchall())) * 1e3
        
        # get half cycle boundaries
        self.query('''SELECT Cycle_Start,Cycle_End FROM Half_Cycle_Table''')
        halfStatPoints = np.array(self.fetchall())
        
        # calcuate average current for each half cycle ignoring rest time
        self.halfStatCurrent = np.empty((0))
        for (a,b) in halfStatPoints:
            self.halfStatCurrent = np.append(self.halfStatCurrent, 
                                             np.true_divide(current[a:b].sum(),(current[a:b]!=0).sum()))
            
        print(self.halfStatCurrent[0:6]*1e3)
    
    
    def getHalfStatCurrent(self):
        """average current per half cycle"""
        return self.halfStatCurrent
    
    
    ### per cycle statistics methods ###
    
    def setStatistics(self):
        """fetch statistics from raw file"""
        
        # fetch statistics
        self.setStatSpecificCapacity()
        self.setStatVolumetricCapacity()
        self.setStatSpecificEnergy()
        self.setStatVolumetricEnergy()
        self.setStatSpecificCurrentDensity()
        
        self.statistics = {'specificCapacity': self.statSpecificCapacity,
                           'volumetricCapacity': self.statVolumetricCapacity,
                           'specificEnergy': self.statSpecificEnergy,
                           'volumetricEnergy': self.statVolumetricEnergy,
                           'specificCurrentDensity': self.statSpecificCurrentDensity}
        
        
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
    
    
    def setStatCurrent(self):
        """average current"""
        
        self.statCurrent = np.empty((0,2))
        for i in self.halfStatCurrent:
            charge = 0; discharge = 0
            if i > 0:
                charge = i
            elif i < 0:
                discharge = i
    
    
    def setStatSpecificCurrentDensity(self):
        """specific current density"""
        
        # calculate average current in each half cycle
        # I = Q / t [As / s = A ]
        # [ mAh  ]
        # step time is wrong if there was rest time
        # J_mass = I / m [A/mg] * 1e6 = [mA/g]
        if self.mass is not 0:
            self.statSpecificCurrentDensity = np.abs(self.statSpecificCapacity / (self.mass))
        else:
            self.statSpecificCurrentDensity = np.zeros(self.statSpecificCapacity.shape)
            
            
    def getStatSpecificCurrentDensity(self):
        """specific current density"""
        return self.statSpecificCurrentDensity