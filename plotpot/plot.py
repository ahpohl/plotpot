# -*- coding: utf-8 -*-
import sys, os
from globals import args
import numpy as np

# import matplotlib
try:
    import matplotlib.pyplot as plt
except ImportError as error:
    print("Please install Python Matplotlib from http://matplotlib.sourceforge.net/")
    sys.exit(error)

# import smooth    
try:
    from smooth import smooth
except ImportError as error:
    print("Please download smooth.py from http://wiki.scipy.org/Cookbook/SignalSmooth")
    sys.exit(error)

# data array 
"""
0: data point
1: cycle index
2: step index
3: test time [s]
4: step time [s]
5: datetime [sec since epoch]
6: current [A]
7: voltage [V]
8: capacity [As]
9: energy [VAs]
10: dQdV [As V-1]
11: aux channel, temp. or Ece
"""
    
# Plot functions

class plot(object):

    def __init__(self, plots, data, cycles, stats, massStor):
        self.data = data
        self.cycles = cycles
        self.stats = stats
        self.massStor = massStor
        self.plots = plots     
    
    def draw(self):
        """call plotting functions"""
        
        # set current working directory
        plt.rcParams['savefig.directory'] = os.getcwd()
        
        for n in self.plots:
            if n == 1:
                self.fig_voltage_vs_capacity()
            elif n == 2:
                self.fig_voltage_current_vs_time()
            elif n == 3:
                self.fig_aux_channel_vs_time()
            elif n == 4:
                self.fig_capacity()
            elif n == 5:
                self.fig_specific_energy()
            elif n == 6:
                self.fig_volumetric_energy()
            elif n == 7:
                self.fig_efficiency()
            elif n == 8:
                self.fig_hysteresis()
            elif n == 9:
                self.fig_dQdV()
            elif n == 10:
                self.fig_c_rate()
            elif n == 11:
                self.fig_specific_current_density()
            elif n == 12:
                self.fig_area_current_density()
            elif n == 13:
                self.fig_voltage_vs_capacity2()
            else:
                sys.exit("ERROR: plot number not defined.")
        
        return

    def savefigure(self):
        """This function saves figures."""

        if args.counter:
            ext = '_ce.png'
        else:
            ext = '.png'
        
        stem = args.filename.split('.')[0]
        
        filename = {1: '_voltage_vs_capacity',
                    2: '_voltage_current_vs_time',
                    3: '_aux_channel_vs_time',
                    4: '_capacity',
                    5: '_specific_energy',
                    6: '_volumetric_energy',
                    7: '_efficiency',
                    8: '_hysteresis',
                    9: '_dqdv',
                    10: '_c_rate',
                    11: '_specific_current_density',
                    12: '_current_density',
                    13: '_voltage_vs_capacity2'}
        
        for n in self.plots:
            fig = plt.figure(n)
            plt.savefig(stem + filename[n] + ext)
           
        return
    
    def show_plots(self):
        """show plots on sceen"""
        plt.show()
        return
    
    def fig_voltage_vs_capacity(self): # data, cycles, massStor
        """plot galvanostatic profile"""
        
        fig = plt.figure(1)
        fig.canvas.set_window_title("Figure 1 - galvanostatic profile")
        ax1 = fig.add_subplot(111)
        
        for c in self.cycles:
            d = self.data[self.data[:,1]==c] # select cycle
            ch = d[d[:,2]==1] # select charge half cycle
            dc = d[d[:,2]==-1] # select discharge hafl cycle
            ch = ch[:-1] # discard last data point, zero capacity
            dc = dc[:-1] # discard last data point, zero capacity
            
            with np.errstate(invalid='ignore'):
                ax1.plot(ch[:,8]/(3.6e-3*self.massStor['mass']), ch[:,7], 'k-', label='charge')
                ax1.plot(dc[:,8]/(3.6e-3*self.massStor['mass']), dc[:,7], 'k-', label='discharge')
    
        ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]')
        ax1.set_ylabel('Voltage [V]')
    
        return
    
    def fig_voltage_current_vs_time(self): # data
        """Voltage and current vs. time plot"""
          
        fig = plt.figure(2)
        fig.canvas.set_window_title("Figure 2 - voltage, current vs. time")
        plt.subplots_adjust(left=0.11, right=0.87, top=0.92, bottom=0.10)
        plt.rc('legend', numpoints=1) # change points in legend
        
        ax1 = fig.add_subplot(111)
        ax1.plot(self.data[:,3]/3600, self.data[:,7], 'k-', label='Voltage')
        ax1.set_xlabel('Time [h]')
        ax1.set_ylabel('Voltage [V]')
        ax2 = ax1.twinx()
        ax2.plot(self.data[:,3]/3600, self.data[:,6]*1e3, 'k--', label='Current')
        ax2.set_ylabel('Current [mA]')
        
        return
    
    def fig_aux_channel_vs_time(self): # data
        """auxiliary channel vs. time plot"""
    
        fig = plt.figure(3)
        fig.canvas.set_window_title("Figure 3 - auxiliary channel")
        plt.subplots_adjust(left=0.11, right=0.87, top=0.92, bottom=0.10)
        plt.rc('legend', numpoints=1) # change points in legend
        
        ax1 = fig.add_subplot(111)
        ax1.plot(self.data[:,3]/3600, self.data[:,11], 'k-', label='Auxiliary channel')
        ax1.set_xlabel('Time [h]')
        ax1.set_ylabel('Auxiliary channel')
        #ax1.legend()
        
        return
    
    def fig_capacity(self): # stats, massStor
        """capacity plot"""
        
        fig = plt.figure(4)
        fig.canvas.set_window_title("Figure 4 - specific capacity")
        plt.rc('legend', numpoints=1, fontsize=12) # change points in legend
    
        # specific capacity
        ax1 = fig.add_subplot(111)
        ax1.plot(self.stats[:,0], self.stats[:,5], 'ko-', label='charge')
        ax1.plot(self.stats[:,0], np.abs(self.stats[:,6]), 'kD-', label='discharge')
        ax1.set_xlabel('Cycle')
        ax1.set_ylabel('Specific capacity [mAh g$^{-1}$]')
        
        # Shrink current axis's height by 10% on the bottom
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    
        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=False, shadow=False, ncol=2)
    
        # set ylim
        lim = plt.ylim()
        plt.ylim(ymin=0, ymax=lim[1])
        
        return
    
    def fig_specific_energy(self): # stats, massStor
        """energy plot per mass""" 
    
        fig = plt.figure(5)
        fig.canvas.set_window_title("Figure 5 - specific energy")
        plt.rc('legend', numpoints=1, fontsize=12) # change points in legend
    
        # specific energy
        ax2 = fig.add_subplot(111)
        ax2.plot(self.stats[:,0], self.stats[:,7], 'ko-', label='charge')
        ax2.plot(self.stats[:,0], np.abs(self.stats[:,8]), 'kD-', label='discharge')
        ax2.set_xlabel('Cycle')
        ax2.set_ylabel('Specific energy [Wh kg$^{-1}$]')
        
        # Shrink current axis's height by 10% on the bottom
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    
        # Put a legend below current axis
        ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=False, shadow=False, ncol=2)
       
        # set ylim
        lim = plt.ylim()
        plt.ylim(ymin=0, ymax=lim[1])
     
        return

    def fig_volumetric_energy(self): # stats, massStor
        """energy plot per volume""" 
    
        fig = plt.figure(6)
        fig.canvas.set_window_title("Figure 6 - volumetric energy density")
        plt.rc('legend', numpoints=1, fontsize=12) # change points in legend
    
        # specific energy in Wh/L
        ax2 = fig.add_subplot(111)
        ax2.plot(self.stats[:,0], self.stats[:,9], 'ko-', label='charge')
        ax2.plot(self.stats[:,0], np.abs(self.stats[:,10]), 'kD-', label='discharge')
        ax2.set_xlabel('Cycle')
        ax2.set_ylabel('Volumetric energy [Wh L$^{-1}$]')
        
        # Shrink current axis's height by 10% on the bottom
        box = ax2.get_position()
        ax2.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
    
        # Put a legend below current axis
        ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=False, shadow=False, ncol=2)
       
        # set ylim
        lim = plt.ylim()
        plt.ylim(ymin=0, ymax=lim[1])
     
        return
    
    def fig_efficiency(self): # stats
        """coulombic efficiency plot"""
    
        fig = plt.figure(7)
        fig.canvas.set_window_title("Figure 7 - coulombic efficiency")
        plt.rc('legend', numpoints=1) # change points in legend
       
        # coulombic efficiency
        ax3 = fig.add_subplot(111)
        ax3.plot(self.stats[:,0], self.stats[:,16]*100, 'ks-')
        ax3.set_xlabel('Cycle')
        ax3.set_ylabel('Coulombic efficiency [%]')
        
        return
    
    def fig_hysteresis(self): # stats
        """average voltage and hysteresis plot"""
    
        fig = plt.figure(8)
        fig.canvas.set_window_title("Figure 8 - voltage hysteresis")
        plt.subplots_adjust(left=0.11, right=0.87, top=0.92, bottom=0.10)
        plt.rc('legend', numpoints=1, fontsize=12) # change points in legend
       
        # voltage hysteresis
        ax4 = fig.add_subplot(111)
        
        p1 = ax4.plot(self.stats[:,0], self.stats[:,11], 'ko--', label='charge voltage')
        p2 = ax4.plot(self.stats[:,0], self.stats[:,12], 'kD--', label='discharge voltage')
        p3 = ax4.plot(self.stats[:,0], self.stats[:,15], 'ks-', label='hysteresis')
        ax4.set_xlabel('Cycle')
        ax4.set_ylabel('Voltage [V]')
        
        # set ylim
        lim = plt.ylim()
        plt.ylim(ymin=0, ymax=lim[1])
        
        # Shrink current axis's height by 10% on the bottom
        box = ax4.get_position()
        ax4.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        
        # Put a legend below current axis
        lines = p1+p2+p3
        plt.legend(lines, [l.get_label() for l in lines], loc='upper center', 
                   bbox_to_anchor=(0.5, -0.12), fancybox=False, shadow=False, ncol=3)
        
        return
    
    def fig_dQdV(self): # data, cycles
        """cyclovoltammogram from galvanostatic self.cycles
        7: voltage
        8: capacity
        10: dQdV
        """
        
        fig = plt.figure(9)
        fig.canvas.set_window_title("Figure 9 - differential capacity")
        ax1 = fig.add_subplot(111)
        
        dictLevel = {'0': 0, '1': 3, '2': 5, '3': 9, '4': 15} # level odd integer >= 3
        level = dictLevel[str(args.smooth)]
        lim = level / 2.0 # float division 
        
        for cyc in self.cycles:
            ch = self.data[np.logical_and(self.data[:,1] == cyc, self.data[:,2] == 1)]
            dc = self.data[np.logical_and(self.data[:,1] == cyc, self.data[:,2] == -1)]
            
            # skip last two data points
            ch = ch[:-2]
            dc = dc[:-2]
            
            dc[:,10] = -dc[:,10] # dQdV negative on discharge
            
            if ch.shape[0] > 0:
                if level > 0:
                    ych = smooth(ch[:,10], window_len=level, window='hamming')
                    ax1.plot(ch[:,7], ych[lim:-lim], 'k-', label='')
                # disable smooth
                else:
                    ax1.plot(ch[:,7], ch[:,10], 'k-', label='')
                
            if dc.shape[0] > 0:
                if level > 0:
                    ydc = smooth(dc[:,10], window_len=level, window='hamming')
                    ax1.plot(dc[:,7], ydc[lim:-lim], 'k-', label='')
                else:
                    ax1.plot(dc[:,7], dc[:,10], 'k-', label='')
                
        ax1.set_xlabel('Voltage [V]')
        ax1.set_ylabel('dQ/dV [As V$^{-1}$]')
    
        return
    
    def fig_c_rate(self): # stats, massStor
        """C-rate vs. cycle number"""
        
        fig = plt.figure(10)
        fig.canvas.set_window_title("Figure 10 - C-rate")
        plt.subplots_adjust(left=0.11, right=0.87, top=0.92, bottom=0.10)
        plt.rc('legend', numpoints=1, fontsize=12) # change points in legend
       
        ax1 = fig.add_subplot(111)
        p1 = ax1.plot(self.stats[:,0], self.stats[:,21], 'ko-', label='charge')
        p2 = ax1.plot(self.stats[:,0], np.abs(self.stats[:,22]), 'kD-', label='discharge')
        
        ax1.set_xlabel('Cycle number')
        ax1.set_ylabel('x in C x$^{-1}$ [h]')
        
        # Shrink current axis's height by 10% on the bottom
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        
        # Put a legend below current axis
        lines = p1+p2
        plt.legend(lines, [l.get_label() for l in lines], loc='upper center', 
                   bbox_to_anchor=(0.5, -0.12), fancybox=False, shadow=False, ncol=3)
    
        # set ylim
        #lim = plt.ylim()
        #plt.ylim(ymin=0, ymax=lim[1])
        
        return
    
    def fig_specific_current_density(self): # stats, massStor
        """Specific current density vs. cycle number"""
        
        fig = plt.figure(11)
        fig.canvas.set_window_title("Figure 11 - specific current")
        plt.subplots_adjust(left=0.11, right=0.87, top=0.92, bottom=0.10)
        plt.rc('legend', numpoints=1, fontsize=12) # change points in legend
       
        ax1 = fig.add_subplot(111)
        p1 = ax1.plot(self.stats[:,0], self.stats[:,17], 'ko-', label='charge')
        p2 = ax1.plot(self.stats[:,0], np.abs(self.stats[:,18]), 'kD-', label='discharge')
        
        ax1.set_xlabel('Cycle number')
        ax1.set_ylabel('Specific current density [mA g$^{-1}$]')
        
        # Shrink current axis's height by 10% on the bottom
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        
        # Put a legend below current axis
        lines = p1+p2
        plt.legend(lines, [l.get_label() for l in lines], loc='upper center', 
                   bbox_to_anchor=(0.5, -0.12), fancybox=False, shadow=False, ncol=3)
    
        # set ylim
        #lim = plt.ylim()
        #plt.ylim(ymin=0, ymax=lim[1])
        
        return
    
    def fig_area_current_density(self):
        """Specific current density vs. cycle number"""
        
        fig = plt.figure(12)
        fig.canvas.set_window_title("Figure 12 - current per electrode area")
        plt.subplots_adjust(left=0.14, right=0.87, top=0.92, bottom=0.10)
        plt.rc('legend', numpoints=1, fontsize=12) # change points in legend
       
        ax1 = fig.add_subplot(111)
        p1 = ax1.plot(self.stats[:,0], self.stats[:,19], 'ko-', label='charge')
        p2 = ax1.plot(self.stats[:,0], np.abs(self.stats[:,20]), 'kD-', label='discharge')
        
        ax1.set_xlabel('Cycle number')
        ax1.set_ylabel('Current density [mA cm$^{-2}$]')
        
        # Shrink current axis's height by 10% on the bottom
        box = ax1.get_position()
        ax1.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
        
        # Put a legend below current axis
        lines = p1+p2
        plt.legend(lines, [l.get_label() for l in lines], loc='upper center', 
                   bbox_to_anchor=(0.5, -0.12), fancybox=False, shadow=False, ncol=3)
    
        # set ylim
        #lim = plt.ylim()
        #plt.ylim(ymin=0, ymax=lim[1])
        
        return
    
    def fig_voltage_vs_capacity2(self): # data, cycles, massStor
        """plot galvanostatic profile (circle)"""
        
        fig = plt.figure(13)
        fig.canvas.set_window_title("Figure 13 - galvanostatic profile")
        ax1 = fig.add_subplot(111)
        
        for c in self.cycles:
            d = self.data[self.data[:,1]==c] # select cycle
            ch = d[d[:,2]==1] # select charge half cycle
            dc = d[d[:,2]==-1] # select discharge hafl cycle
            ch = ch[:-1] # discard last data point, zero capacity
            dc = dc[:-1] # discard last data point, zero capacity
            
            with np.errstate(invalid='ignore'):
                ax1.plot((-1*ch[:,8]+np.abs(dc[-1:,8]))/(3.6e-3*self.massStor['mass']), ch[:,7], 'k-', label='charge')
                ax1.plot(np.abs(dc[:,8])/(3.6e-3*self.massStor['mass']), dc[:,7], 'k-', label='discharge')
    
        ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]')
        ax1.set_ylabel('Voltage [V]')
    
        return