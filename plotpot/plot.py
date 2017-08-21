# -*- coding: utf-8 -*-
import sys, os
import numpy as np
import matplotlib.pyplot as plt
from plotpot.data import Data

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

class Plot(Data):

    def __init__(self, args):
        self.args = args
        
        # call Data base class constructor
        super().__init__(args)
        
        # import variables from base class Data
        self.plots = self.getPlots()
        self.cycles = self.getCycles()
        self.data = self.getData()
        self.stats = self.getStatistics()
        self.metaInfo = self.getMetaInfo()

    
    def drawPlots(self):
        """call plotting functions"""
        
        # set current working directory
        plt.rcParams['savefig.directory'] = os.getcwd()
        
        for n in self.plots:
            if n == 1:
                self.figVoltageCapacity()
            elif n == 2:
                self.figVoltageCurrentTime()
            elif n == 3:
                self.figAuxChannelTime()
            elif n == 4:
                self.figCapacity()
            elif n == 5:
                self.figSpecificEnergy()
            elif n == 6:
                self.figVolumetricEnergy()
            elif n == 7:
                self.figEfficiency()
            elif n == 8:
                self.figHysteresis()
            elif n == 9:
                self.figDQDV()
            elif n == 10:
                self.figCRate()
            elif n == 11:
                self.figSpecificCurrentDensity()
            elif n == 12:
                self.figAreaCurrentDensity()
            elif n == 13:
                self.figVoltageCapacityCircle()
            else:
                sys.exit("ERROR: Plot number not defined.")
        

    def saveFigure(self):
        """This function saves figures."""

        if self.args.counter:
            ext = '_ce.png'
        else:
            ext = '.png'
        
        stem = self.args.filename.split('.')[0]
        
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
           
    
    def showPlots(self):
        """show plots on sceen"""
        plt.show()
        
    
    def figVoltageCapacity(self): # data, cycles, massStor
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
    
    
    def figVoltageCurrentTime(self): # data
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
        
    
    def figAuxChannelTime(self): # data
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
        
    
    def figCapacity(self): # stats, massStor
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
        
    
    def figSpecificEnergy(self): # stats, massStor
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
     

    def figVolumetricEnergy(self): # stats, massStor
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
     
    
    def figEfficiency(self): # stats
        """coulombic efficiency plot"""
    
        fig = plt.figure(7)
        fig.canvas.set_window_title("Figure 7 - coulombic efficiency")
        plt.rc('legend', numpoints=1) # change points in legend
       
        # coulombic efficiency
        ax3 = fig.add_subplot(111)
        ax3.plot(self.stats[:,0], self.stats[:,16]*100, 'ks-')
        ax3.set_xlabel('Cycle')
        ax3.set_ylabel('Coulombic efficiency [%]')
        
    
    def figHysteresis(self): # stats
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
        
    
    def figDQDV(self): # data, cycles
        """cyclovoltammogram from galvanostatic self.cycles
        7: voltage
        8: capacity
        10: dQdV
        """
        
        fig = plt.figure(9)
        fig.canvas.set_window_title("Figure 9 - differential capacity")
        ax1 = fig.add_subplot(111)
        
        # translate smooth level to window length
        dictLevel = {'1': 5, '2': 11, '3': 17, '4': 23} # level odd integer
        
        for cyc in self.cycles:
            ch = self.data[np.logical_and(self.data[:,1] == cyc, self.data[:,2] == 1)]
            dc = self.data[np.logical_and(self.data[:,1] == cyc, self.data[:,2] == -1)]
            
            # skip last two data points
            ch = ch[:-2]
            dc = dc[:-2]
            
            dc[:,10] = -dc[:,10] # dQdV negative on discharge
            
            if ch.shape[0] > 0:
                if self.args.smooth:
                    level = dictLevel[str(self.args.smooth)]
                    ych = self.smooth(ch[:,10], window_len=level, window='hamming')
                    ax1.plot(ch[:,7], ych, 'k-', label='')
                # disable smooth
                else:
                    ax1.plot(ch[:,7], ch[:,10], 'k-', label='')
                
            if dc.shape[0] > 0:
                if self.args.smooth:
                    level = dictLevel[str(self.args.smooth)]
                    ydc = self.smooth(dc[:,10], window_len=level, window='hamming')
                    ax1.plot(dc[:,7], ydc, 'k-', label='')
                else:
                    ax1.plot(dc[:,7], dc[:,10], 'k-', label='')
                
        ax1.set_xlabel('Voltage [V]')
        ax1.set_ylabel('dQ/dV [As V$^{-1}$]')
    
    
    def figCRate(self): # stats, massStor
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
        

    def figSpecificCurrentDensity(self): # stats, massStor
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
        
    
    def figAreaCurrentDensity(self):
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
        
    
    def figVoltageCapacityCircle(self): # data, cycles, massStor
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
    
    
    def smooth(self, x, window_len=11, window='hanning'):
        """smooth.py from http://wiki.scipy.org/Cookbook/SignalSmooth
        smooth the data using a window with requested size.
        
        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal 
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.
        
        input:
            x: the input signal 
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.
    
        output:
            the smoothed signal
            
        example:
    
        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)
        
        see also: 
        
        np.hanning, np.hamming, np.bartlett, np.blackman, np.convolve
        scipy.signal.lfilter
     
        TODO: the window parameter could be the window itself if an array instead of a string
        """
    
        if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")
    
        if x.size < window_len:
            raise ValueError("Input vector needs to be bigger than window size.")
    
        if window_len<3:
            return x
    
        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError("Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
    
        s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
        
        if window == 'flat': #moving average
            w=np.ones(window_len,'d')
        else:
            w=eval('np.'+window+'(window_len)')
    
        y=np.convolve(w/w.sum(),s,mode='valid')
        
        # make 'y output lengtj' == 'y input length'
        return y[(window_len//2):-(window_len//2)] # "//" integer division e.g. 15//2 = 7
    
    