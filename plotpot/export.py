# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 22:08:49 2017

@author: Alexander Pohl
"""

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
        if self.metaInfo['area'] == 0:
            loading = 0
        else:
            # m / A = [ mg / cm² ]
            loading = self.metaInfo['mass'] / self.metaInfo['area']
        
        with open(self.args.filename.split('.')[0]+'_statistics.csv', 'w') as fh:
        
            # export metaInfo
            header = """Mass,Capacity,Area,Volume,Loading
mg,mAh/g,cm²,µL,mg/cm²\n"""
            fh.write(header)
            
            dat = "%.2f,%.2f,%.2f,%.2f,%.2f\n" % (
                    self.metaInfo['mass'], 
                    self.metaInfo['cap'], 
                    self.metaInfo['area'], 
                    self.metaInfo['volume'], 
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
        if self.metaInfo['mass'] == 0:
            self.data[:,8] = 0
        else:
            self.data[:,8] = self.data[:,8] / (3.6e-3 * self.metaInfo['mass'])
            
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
# %-12s %-12s %-12s\n""" % (c, self.metaInfo['mass'], "capacity", "voltage", "dQ/dV", "mAh/g", "V", "As/V")
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
# %-12s %-12s %-12s\n""" % (c, self.metaInfo['mass'], "capacity", "voltage", "dQ/dV", "mAh/g", "V", "As/V")
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
        
        
    def export(self, metaInfo):
        """process --export option"""
        self.metaInfo = metaInfo
        self.writeStatisticsTable()
        self.writeDataTable()
        self.writeVoltageProfile()
        self.writeMergeFileSummary()
        