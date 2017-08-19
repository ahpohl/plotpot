# -*- coding: utf-8 -*-
import os
import zipfile, tempfile, shutil
#import csv
import numpy as np

# ignore division by zero errors
np.seterr(divide='ignore')

# export class
class Export(object):
    
    def __init__(self, args, data, cycles, stats, massStor):
        self.data = data
        self.cycles = cycles
        self.stats = stats
        self.massStor = massStor
        self.expStats = self._calcStatistics()
        self.args = args
        
    def getStatistics(self):
        return self.expStats
    
    def dumpArray(self, fh, array, formatstring="%f", delimiter=',', header=''):
        if formatstring == '%f':
            formatspec = []
            f = 0
            while True:
                if f == array.shape[1]:
                    break
                else:
                    formatspec.append(formatstring)
                f += 1
        else:
            formatspec = formatstring.split(' ')
        if header != '':
            fh.write(header)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                if array[i,j] == None:
                    array[i,j] = 0
                if j == array.shape[1]-1:
                    fh.write(formatspec[j] % (array[i,j]))
                else:
                    fh.write(formatspec[j] % (array[i,j])+delimiter)
            fh.write("\n")
        return
    
    def calcStatistics(self):
        # *** statistics ***
        
        """
        stats (stats array):
        0: cycle index
        1: cycle start
        2: cycle end
        3: charge time [s]
        4: discharge time [s]    
        5: charge capacity [As]
        6: discharge capacity [As]
        7: charge energy [VAs]
        8: discharge energy [VAs]
        9: average charge voltage [V]
        10: average discharge voltage [V]
        11: voltage hysteresis [V]
        12: coulombic efficiency
        """
        
        """
        extended stats (export array):
        0: cycle index
        1: cycle start
        2: cycle end
        3: charge time [s]
        4: discharge time [s]    
        5: charge capacity [mAh/g]
        6: discharge capacity [mAh/g]
        7: specific charge energy [Wh/kg]
        8: specific discharge energy [Wh/kg]
        9: volumetric charge energy [Wh/L]
        10: volumetric discharge energy [Wh/L]
        11: average charge voltage [V]
        12: average discharge voltage [V]
        13: average charge current [A]
        14: average discharge current [A]
        15: voltage hysteresis [V]
        16: coulombic efficiency [%]
        17: specific charge current density [mA/g]
        18: specific discharge current density [mA/g]
        19: area charge current density [mA/cm-2]
        20: area discharge current density [mA/cm-2]
        21: charge c-rate [h]
        22: discharge c-rate [h]
        """
        
        # copy cycle index, start, end, time(c) and time(d) to export array 
        export = self.stats[:,:5] # [0,1,2,3,4]
        
        # *** extend array ***
        
        # convert capacity from As to mAh/g [5,6]
        export = np.c_[export, self.stats[:,5:7]] # [5,6]
        if self.massStor['mass'] == 0:
            export[:,5] = 0
            export[:,6] = 0
        else:
            export[:,5] = export[:,5] / (3.6e-3 * self.massStor['mass'])
            export[:,6] = export[:,6] / (3.6e-3 * self.massStor['mass'])
                  
        # convert energy from Ws to Wh/kg
        export = np.c_[export, self.stats[:,7:9]] # [7,8]
        if self.massStor['mass'] == 0:
            export[:,7] = 0
            export[:,8] = 0
        else:        
            export[:,7] = export[:,7] / (3.6e-3 * self.massStor['mass'])
            export[:,8] = export[:,8] / (3.6e-3 * self.massStor['mass'])
        
        # convert energy from Ws to Wh/L
        # 1 h = 3600 s, volume in µL
        export = np.c_[export, self.stats[:,7:9]] # [9,10]
        if self.massStor['volume'] == 0:
            export[:,9] = 0
            export[:,10] = 0
        else:    
            export[:,9] = export[:,9] / (3.6e-3 * self.massStor['volume'])
            export[:,10] = export[:,10] / (3.6e-3 * self.massStor['volume'])
            
        # copy average voltage
        export = np.c_[export, self.stats[:,9:11]] # [11,12]
                           
        # calculate average current for each cycle
        # I = Q / t [As / s = A ]
        # step time is wrong if there was rest time
        try:
            export = np.c_[export, self.stats[:,5] / self.stats[:,3]] # charge [13]
            export = np.c_[export, self.stats[:,6] / self.stats[:,4]] # discharge [14]
        except ZeroDivisionError as e:
            print("Warning: %s" % e)
            
        
        
        # copy coulombic efficienty and voltage hysteresis
        export = np.c_[export, self.stats[:,11:13]] # [15,16]
        
        # calculate specific current density
        # J_mass = I / m [A/mg] * 1e6 = [mA/g]
        if self.massStor['mass'] == 0:
            export = np.c_[export, np.zeros((export.shape[0], 2))]
        else:
            export = np.c_[export, export[:,13] / self.massStor['mass'] * 1e6] # [17]
            export = np.c_[export, export[:,14] / self.massStor['mass'] * 1e6] # [18]
        
        # calculate area current density
        # J_Area = I / A [ A / cm² ] * 1e3 = [mA/cm²]
        if self.massStor['area'] == 0:
            export = np.c_[export, np.zeros((export.shape[0], 2))]
        else:
            export = np.c_[export, export[:,13] / self.massStor['area'] * 1e3] # [19]
            export = np.c_[export, export[:,14] / self.massStor['area'] * 1e3] # [20]
        
        # calculate theoretical capacity
        # C = m * Ctheo [mg * mAh/g *1e-3 = Ah]
        cap_th = self.massStor['mass'] * self.massStor['cap'] * 1e-6
        
        # calculate C-rate / x
        # x = C / I [Ah / A = h]
        try:
            export = np.c_[export, cap_th / export[:,13]] # [21]
            export = np.c_[export, cap_th / export[:,14]] # [22]
        except ZeroDivisionError as e:
            print("Warning: %s" % e)     
        
        return export
    
    def writeDataTable(self):
        
        with open(self.args.filename.split('.')[0]+'_data.csv', 'w') as fh:
            header = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                "data_point", "cycle_index", "step_index", 
                "test_time", "step_time", "datetime", 
                "current", "voltage", "capacity", 
                "energy", "dQ/dV", "aux_channel")
            fh.write(header)
            header = ",,,%s,%s,%s,%s,%s,%s,%s,%s,\n" % (
                "s", "s", "s", "A", "V", "As", "Ws", "As/V")
            fh.write(header)        
            self.__dump_array(fh, self.data, '%d %d %d %f %f %f %e %f %f %f %f %f')
            fh.close()
    
    def writeStatisticsTable(self):
        
        # calculate mass loading
        if self.massStor['area'] == 0:
            loading = 0
        else:
            # m / A = [ mg / cm² ]
            loading = self.massStor['mass'] / self.massStor['area']
        
        with open(self.args.filename.split('.')[0]+'_statistics.csv', 'w') as fh:
        
            # export massStor
            header = """Mass,Capacity,Area,Volume,Loading
mg,mAh/g,cm²,µL,mg/cm²\n"""
            fh.write(header)
            
            dat = "%.2f,%.2f,%.2f,%.2f,%.2f\n" % (
                    self.massStor['mass'], 
                    self.massStor['cap'], 
                    self.massStor['area'], 
                    self.massStor['volume'], 
                    loading)
            fh.write(dat)
            
            # write statistics
            header = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    "cycle_index", "start", "end",
                    "time(c)", "time(d)", 
                    "capacity(c)", "capacity(d)", 
                    "energy(c)", "energy(d)",
                    "energy(c)", "energy(d)",
                    "Vav(c)", "Vav(d)",
                    "current(c)", "current(d)",
                    "efficiency", "hysteresis",
                    "density(c)", "density(d)",
                    "density(c)", "density(d)",
                    "c-rate(c)", "c-rate(d)")
            fh.write(header)
            
            units = ",,,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                    "s", "s", "mAh/g", "mAh/g", "Wh/kg",
                    "Wh/kg", "Wh/L", "Wh/L", "V", "V", "A", "A", "%", "V",
                    "mA/g", "mA/g", "mA/cm²", "mA/cm²", "h", "h")
            fh.write(units)
            
            self.__dump_array(fh, self.expStats, "%d %d %d %f %f %f %f %f %f %f %f %f %f %e %e %f %f %f %f %f %f %f %f")
            fh.close()
          
    def writeVoltageProfile(self):
        
        # convert from As to mAh/g
        if self.massStor['mass'] == 0:
            self.data[:,8] = 0
        else:
            self.data[:,8] = self.data[:,8] / (3.6e-3 * self.massStor['mass'])
            
        cwd = os.getcwd() # save current directory
        os.chdir(tempfile.gettempdir()) # change to tmp dir
        filestem = self.args.filename.split('.')[0] # create filename
        if not os.path.exists(filestem):
            os.makedirs(filestem) # create directory
        path = os.path.abspath(filestem) # change to directory
        os.chdir(path)
        
        # loop over cycles
        for c in self.cycles:
            d = self.data[self.data[:,1]==c] # select cycle
            ch = d[d[:,2]==1] # select charge half cycle
            dc = d[d[:,2]==-1] # select discharge hafl cycle
            ch = ch[:-1] # discard last data point, zero capacity
            dc = dc[:-1] # discard last data point, zero capacity
                
            # charg
            if ch.size:
                header = """# cycle %d
# charge
# mass %.2f mg
# %-12s %-12s %-12s
# %-12s %-12s %-12s\n""" % (c, self.massStor['mass'], "capacity", "voltage", "dQ/dV", "mAh/g", "V", "As/V")
                cyclename = filestem+'_%03d_charge.txt' % c
                fh = open(cyclename, 'w')
                fh.write(header)
                for i in range(ch.shape[0]):
                    line = "%12.6f %12.6f %12.6f\n" % (ch[i,8], ch[i,7], ch[i,10])
                    fh.write(line)
                fh.close()
                
            # discharge
            if dc.size:
                header = """# cycle %d
# discharge
# mass %.2f mg
# %-12s %-12s %-12s
# %-12s %-12s %-12s\n""" % (c, self.massStor['mass'], "capacity", "voltage", "dQ/dV", "mAh/g", "V", "As/V")
                cyclename = filestem+'_%03d_discharge.txt' % c
                fh = open(cyclename, 'w')
                fh.write(header)
                for i in range(dc.shape[0]):
                    line = "%12.6f %12.6f %12.6f\n" % (dc[i,8], dc[i,7], dc[i,10])
                    fh.write(line)
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
        
        return