# -*- coding: utf-8 -*-
import sys, os
import numpy as np
import matplotlib.pyplot as plt
from plotpot.data import Data


class Plot(Data):

    def __init__(self, args):
        """Data array: 
            0: data point
            1: cycle index
            2: step index
            3: test time [s]
            4: step time [s]
            5: datetime [sec since epoch]
            6: temperature [°C]
            7: current [A]
            8: capacity [As]
            9: voltage WE [V]
            10: voltage2 CE [V]
            11: energy WE [VAs]
            12: energy2 CE [VAs]
            13: dQdV WE [As V-1]
            14: dQdV2 CE [As V-1]"""
        
        self.args = args
        # call Data base class constructor
        super().__init__(args)
        
    
    def drawPlots(self):
        """call plotting functions"""

        # set current working directory
        plt.rcParams['savefig.directory'] = os.getcwd()
        
        for n in self.plots:
            if n == 1:
                self.figVoltageCapacity()
            elif n == 2:
                self.figVoltageCapacityCircle()            
            elif n == 3:
                self.figVoltageCurrentTime()
            elif n == 4:
                self.figAuxChannelTime()
            elif n == 5:
                self.figCapacity()
            elif n == 6:
                self.figSpecificEnergy()
            elif n == 7:
                self.figVolumetricEnergy()
            elif n == 8:
                self.figEfficiency()
            elif n == 9:
                self.figHysteresis()
            elif n == 10:
                self.figDQDV()
            elif n == 11:
                self.figCRate()
            elif n == 12:
                self.figSpecificCurrentDensity()
            elif n == 13:
                self.figAreaCurrentDensity()
            else:
                sys.exit("ERROR: Plot number not defined.")
                

    def saveFigure(self):
        """This function saves figures."""

        ext = '.png'
        stem = self.args.filename.split('.')[0]
        
        filename = {1: '_voltage_vs_capacity',
                    2: '_capacity_circle',
                    3: '_voltage_current_vs_time',
                    4: '_temperature_vs_time',
                    5: '_capacity',
                    6: '_specific_energy',
                    7: '_volumetric_energy',
                    8: '_efficiency',
                    9: '_hysteresis',
                    10: '_dqdv',
                    11: '_c_rate',
                    12: '_specific_current_density',
                    13: '_current_density'}
        
        for n in self.plots:
            plt.figure(n)
            plt.savefig(stem + filename[n] + ext)
           
    
    def showPlots(self):
        """show plots on sceen"""
        plt.show()
        
        
############################################################################
#                             Data plots                                   #
############################################################################
    
    def figVoltageCapacity(self): # data, cycles, metaInfo
        """plot galvanostatic profile"""
        
        fig = plt.figure(1, figsize=(12,6))
        fig.canvas.set_window_title("Figure 1 - full cell galvanostatic profile")
        
        # working electrode plot
        ax1 = fig.add_subplot(121)
        ax1.autoscale(axis='x', tight='tight')
        ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]', fontsize=12)
        ax1.set_ylabel('WE potential [V]', fontsize=12)
        
        # counter electrode plot
        ax2 = fig.add_subplot(122)
        ax2.autoscale(axis='x', tight='tight')
        ax2.set_xlabel('Specific capacity [mAh g$^{-1}$]', fontsize=12)
        ax2.set_ylabel('CE potential [V]', fontsize=12)
        
        for c in self.cycles:
            d = self.data[self.data[:,1]==c] # select cycle
            ch = d[d[:,2]==1] # select charge half cycle
            dc = d[d[:,2]==-1] # select discharge hafl cycle
            ch = ch[:-1] # discard last data point, zero capacity
            dc = dc[:-1] # discard last data point, zero capacity
            
            with np.errstate(invalid='ignore'):
                # working electrode
                ax1.plot(ch[:,8]/(3.6e-3*self.metaInfo['mass']), ch[:,9], 'k-', label='charge')
                ax1.plot(dc[:,8]/(3.6e-3*self.metaInfo['mass']), dc[:,9], 'k-', label='discharge')
                # counter electrode
                ax2.plot(ch[:,8]/(3.6e-3*self.metaInfo['mass']), ch[:,10], 'k-', label='charge')
                ax2.plot(dc[:,8]/(3.6e-3*self.metaInfo['mass']), dc[:,10], 'k-', label='discharge')
        
        fig.tight_layout()
        
        
    def figVoltageCapacityCircle(self): # data, cycles, metaInfo
        """plot galvanostatic profile (circle)"""
        
        fig = plt.figure(13, figsize=(12,6))
        fig.canvas.set_window_title("Figure 13 - full cell galvanostatic profile")
        
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]')
        ax1.set_ylabel('WE potential [V]')

        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.set_xlabel('Specific capacity [mAh g$^{-1}$]')
        ax2.set_ylabel('CE potential [V]')
        
        for c in self.cycles:
            d = self.data[self.data[:,1]==c] # select cycle
            ch = d[d[:,2]==1] # select charge half cycle
            dc = d[d[:,2]==-1] # select discharge hafl cycle
            ch = ch[:-1] # discard last data point, zero capacity
            dc = dc[:-1] # discard last data point, zero capacity
            
            with np.errstate(invalid='ignore'):
                if dc.shape[0] > 0 and ch.shape[0] > 0:
                    # working electrode
                    ax1.plot((-1*ch[:,8]+np.abs(dc[-1:,8]))/(3.6e-3*self.metaInfo['mass']), ch[:,9], 'k-', label='charge')
                    ax1.plot(np.abs(dc[:,8])/(3.6e-3*self.metaInfo['mass']), dc[:,9], 'k-', label='discharge')
                    # counter electrode
                    ax2.plot((-1*ch[:,8]+np.abs(dc[-1:,8]))/(3.6e-3*self.metaInfo['mass']), ch[:,10], 'k-', label='charge')
                    ax2.plot(np.abs(dc[:,8])/(3.6e-3*self.metaInfo['mass']), dc[:,10], 'k-', label='discharge')
                    
        fig.tight_layout()
        
    
    def figVoltageCurrentTime(self): # data
        """Voltage and current vs. time plot"""
          
        fig = plt.figure(2, figsize=(10,8))
        fig.canvas.set_window_title("Figure 2 - full cell voltage, current vs. time")
        
        # working electrode plot
        ax1 = fig.add_subplot(311)
        ax1.autoscale(axis='x', tight='tight')
        ax1.set_ylabel('WE potential [V]', fontsize=12)
        ax1.plot(self.data[:,3]/3600, self.data[:,9], 'k-', label='Voltage')
        
        # counter electrode plot
        ax2 = fig.add_subplot(312)
        ax2.autoscale(axis='x', tight='tight')
        ax2.set_ylabel('CE potential [V]', fontsize=12)
        ax2.plot(self.data[:,3]/3600, self.data[:,10], 'k-', label='Voltage')
        
        # Current
        ax3 = fig.add_subplot(313)
        ax3.autoscale(axis='x', tight='tight')
        ax3.set_xlabel('Time [h]', fontsize=12)
        ax3.set_ylabel('Current [mA]', fontsize=12)
        ax3.plot(self.data[:,3]/3600, self.data[:,7]*1e3, 'k--', label='Current')
        
        fig.tight_layout()
        
    
    def figAuxChannelTime(self): # data
        """auxiliary channel vs. time plot"""
    
        fig = plt.figure(3)
        fig.canvas.set_window_title("Figure 3 - auxiliary channel")
        
        ax1 = fig.add_subplot(111)
        ax1.autoscale(axis='x', tight='tight')
        ax1.plot(self.data[:,3]/3600, self.data[:,6], 'k-', label='Auxiliary channel')
        ax1.set_xlabel('Time [h]', fontsize=12)
        ax1.set_ylabel('Temperature [°C]', fontsize=12)
        
        fig.tight_layout()


    def figDQDV(self): # data, cycles
        """cyclovoltammogram from galvanostatic cycles"""

        # translate smooth level to window length
        if self.args.smooth:
            dictLevel = {'1': 5, '2': 11, '3': 17, '4': 23} # level odd integer
            level = dictLevel[str(self.args.smooth)]
        
        fig = plt.figure(9, figsize=(12,6))
        fig.canvas.set_window_title("Figure 9 - full cell differential capacity")
        
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.set_xlabel('WE potential [V]', fontsize=12)
        ax1.set_ylabel('dQ/dV [As V$^{-1}$]', fontsize=12)
        
        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.set_xlabel('CE potential [V]', fontsize=12)
        ax2.set_ylabel('dQ/dV [As V$^{-1}$]', fontsize=12)
                
        for cyc in self.cycles:
            ch = self.data[np.logical_and(self.data[:,1] == cyc, self.data[:,2] == 1)]
            dc = self.data[np.logical_and(self.data[:,1] == cyc, self.data[:,2] == -1)]
            
            # skip last two data points
            ch = ch[:-2]
            dc = dc[:-2]
            
            # dQdV negative on discharge
            dc[:,13] = -dc[:,13] # WE
            dc[:,14] = -dc[:,14] # CE
            
            if ch.shape[0] > 0:
                if self.args.smooth:            
                    ych_WE = self.smooth(ch[:,13], window_len=level, window='hamming')
                    ych_CE = self.smooth(ch[:,14], window_len=level, window='hamming')
                    ax1.plot(ch[:,9], ych_WE, 'k-', label='')
                    ax2.plot(ch[:,10], ych_CE, 'k-', label='')
                else:
                    # disable smooth
                    ax1.plot(ch[:,9], ch[:,13], 'k-', label='')
                    ax2.plot(ch[:,10], ch[:,14], 'k-', label='')
                    
            if dc.shape[0] > 0:
                if self.args.smooth:
                    ydc_WE = self.smooth(dc[:,13], window_len=level, window='hamming')
                    ydc_CE = self.smooth(dc[:,14], window_len=level, window='hamming')
                    ax1.plot(dc[:,9], ydc_WE, 'k-', label='')
                    ax2.plot(dc[:,10], ydc_CE, 'k-', label='')
                else:
                    ax1.plot(dc[:,9], dc[:,13], 'k-', label='')
                    ax2.plot(dc[:,10], dc[:,14], 'k-', label='')
                    
        fig.tight_layout()

        
############################################################################
#                             Statistics plots                             #
############################################################################
   
    def figCapacity(self): # stats, metaInfo
        """capacity plot"""
        
        fig = plt.figure(4, figsize=(12,6))
        fig.canvas.set_window_title("Figure 4 - full cell specific capacity")
    
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.plot(self.fullStats[:,0], self.fullStats[:,5], 'ko-', label='charge')
        ax1.plot(self.fullStats[:,0], np.abs(self.fullStats[:,6]), 'kD-', label='discharge')
        ax1.set_xlabel('Cycle', fontsize=12)
        ax1.set_ylabel('WE specific capacity [mAh g$^{-1}$]', fontsize=12)
        ylim = ax1.get_ylim()
        ax1.set_ylim([0,ylim[1]])
        
        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.plot(self.fullStats[:,0], self.fullStats[:,5], 'ko-', label='charge')
        ax2.plot(self.fullStats[:,0], np.abs(self.fullStats[:,6]), 'kD-', label='discharge')
        ax2.set_xlabel('Cycle', fontsize=12)
        ax2.set_ylabel('CE specific capacity [mAh g$^{-1}$]', fontsize=12)
        ylim = ax2.get_ylim()
        ax2.set_ylim([0,ylim[1]])
        
        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(1, -0.09), ncol=2, fontsize=12)
        fig.tight_layout(rect=(0,0.05,1,1))
        
    
    def figSpecificEnergy(self): # stats, metaInfo
        """energy plot per mass""" 
    
        fig = plt.figure(5, figsize=(12,6))
        fig.canvas.set_window_title("Figure 5 - full cell specific energy")
    
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.plot(self.fullStats[:,0], self.fullStats[:,7], 'ko-', label='charge')
        ax1.plot(self.fullStats[:,0], np.abs(self.fullStats[:,8]), 'kD-', label='discharge')
        ax1.set_xlabel('Cycle', fontsize=12)
        ax1.set_ylabel('WE specific energy [Wh kg$^{-1}$]', fontsize=12)
        ylim = ax1.get_ylim()
        ax1.set_ylim([0,ylim[1]]) 
        
        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.plot(self.fullStats[:,0], self.fullStats[:,7], 'ko-', label='charge')
        ax2.plot(self.fullStats[:,0], np.abs(self.fullStats[:,8]), 'kD-', label='discharge')
        ax2.set_xlabel('Cycle', fontsize=12)
        ax2.set_ylabel('CE specific energy [Wh kg$^{-1}$]', fontsize=12)
        ylim = ax2.get_ylim()
        ax2.set_ylim([0,ylim[1]])
    
        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(1, -0.09), ncol=2, fontsize=12)
        fig.tight_layout(rect=(0,0.05,1,1))
     

    def figVolumetricEnergy(self): # stats, metaInfo
        """energy plot per volume""" 
    
        fig = plt.figure(6, figsize=(12,6))
        fig.canvas.set_window_title("Figure 6 - full cell volumetric energy density")
    
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.plot(self.fullStats[:,0], self.fullStats[:,9], 'ko-', label='charge')
        ax1.plot(self.fullStats[:,0], np.abs(self.fullStats[:,10]), 'kD-', label='discharge')
        ax1.set_xlabel('Cycle', fontsize=12)
        ax1.set_ylabel('WE volumetric energy [Wh L$^{-1}$]', fontsize=12)
        ylim = ax1.get_ylim()
        ax1.set_ylim([0,ylim[1]])        
        
        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.plot(self.fullStats[:,0], self.fullStats[:,9], 'ko-', label='charge')
        ax2.plot(self.fullStats[:,0], np.abs(self.fullStats[:,10]), 'kD-', label='discharge')
        ax2.set_xlabel('Cycle', fontsize=12)
        ax2.set_ylabel('CE volumetric energy [Wh L$^{-1}$]', fontsize=12)
        ylim = ax2.get_ylim()
        ax2.set_ylim([0,ylim[1]])
        
        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(1, -0.09), ncol=2, fontsize=12)
        fig.tight_layout(rect=(0,0.05,1,1))
    
    
    def figEfficiency(self): # stats
        """coulombic efficiency plot"""
    
        fig = plt.figure(7)
        fig.canvas.set_window_title("Figure 7 - coulombic efficiency")
       
        # coulombic efficiency
        ax3 = fig.add_subplot(111)
        ax3.plot(self.fullStats[:,0], self.fullStats[:,16]*100, 'ks-')
        ax3.set_xlabel('Cycle', fontsize=12)
        ax3.set_ylabel('Coulombic efficiency [%]', fontsize=12)
        
        fig.tight_layout()
        
    
    def figHysteresis(self): # stats
        """average voltage and hysteresis plot"""
    
        fig = plt.figure(8, figsize=(12,6))
        fig.canvas.set_window_title("Figure 8 - full cell voltage hysteresis")
       
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.plot(self.fullStats[:,0], self.fullStats[:,11], 'ko--', label='charge voltage')
        ax1.plot(self.fullStats[:,0], self.fullStats[:,12], 'kD--', label='discharge voltage')
        ax1.plot(self.fullStats[:,0], self.fullStats[:,15], 'ks-', label='hysteresis')
        ax1.set_xlabel('Cycle', fontsize=12)
        ax1.set_ylabel('WE potential [V]', fontsize=12)
        ylim = ax1.get_ylim()
        ax1.set_ylim([0,ylim[1]])
        
        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.plot(self.fullStats[:,0], self.fullStats[:,11], 'ko--', label='charge voltage')
        ax2.plot(self.fullStats[:,0], self.fullStats[:,12], 'kD--', label='discharge voltage')
        ax2.plot(self.fullStats[:,0], self.fullStats[:,15], 'ks-', label='hysteresis')
        ax2.set_xlabel('Cycle', fontsize=12)
        ax2.set_ylabel('CE potential [V]', fontsize=12)
        ylim = ax2.get_ylim()
        ax2.set_ylim([0,ylim[1]])
        
        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(1, -0.09), ncol=3, fontsize=12)
        fig.tight_layout(rect=(0,0.05,1,1))
        
        
    def figCRate(self): # stats, metaInfo
        """C-rate vs. cycle number"""
        
        fig = plt.figure(10)
        fig.canvas.set_window_title("Figure 10 - C-rate")
       
        ax1 = fig.add_subplot(111)
        ax1.plot(self.fullStats[:,0], self.fullStats[:,21], 'ko-', label='charge')
        ax1.plot(self.fullStats[:,0], np.abs(self.fullStats[:,22]), 'kD-', label='discharge')
        
        ax1.set_xlabel('Cycle number', fontsize=12)
        ax1.set_ylabel('x in C x$^{-1}$ [h]', fontsize=12)
    
        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=2, fontsize=12)
        fig.tight_layout(rect=(0,0.07,1,1))
        

    def figSpecificCurrentDensity(self): # stats, metaInfo
        """Specific current density vs. cycle number"""
        
        fig = plt.figure(11, figsize=(12,6))
        fig.canvas.set_window_title("Figure 11 - full cell specific current")
       
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.set_xlabel('Cycle number', fontsize=12)
        ax1.set_ylabel('WE specific current density [mA g$^{-1}$]', fontsize=12)        
        ax1.plot(self.fullStats[:,0], self.fullStats[:,17], 'ko-', label='charge')
        ax1.plot(self.fullStats[:,0], np.abs(self.fullStats[:,18]), 'kD-', label='discharge')
        
        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.set_xlabel('Cycle number', fontsize=12)
        ax2.set_ylabel('CE specific current density [mA g$^{-1}$]', fontsize=12)        
        ax2.plot(self.fullStats[:,0], self.fullStats[:,17], 'ko-', label='charge')
        ax2.plot(self.fullStats[:,0], np.abs(self.fullStats[:,18]), 'kD-', label='discharge')
        
        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(1, -0.09), ncol=3, fontsize=12)
        fig.tight_layout(rect=(0,0.05,1,1))
        
    
    def figAreaCurrentDensity(self):
        """Specific current density vs. cycle number"""
        
        fig = plt.figure(12, figsize=(12,6))
        fig.canvas.set_window_title("Figure 12 - full cell current per electrode area")
       
        # working electrode
        ax1 = fig.add_subplot(121)
        ax1.set_xlabel('Cycle number', fontsize=12)
        ax1.set_ylabel('WE current density [mA cm$^{-2}$]', fontsize=12)
        ax1.plot(self.fullStats[:,0], self.fullStats[:,19], 'ko-', label='charge')
        ax1.plot(self.fullStats[:,0], np.abs(self.fullStats[:,20]), 'kD-', label='discharge')
        
        # counter electrode
        ax2 = fig.add_subplot(122)
        ax2.set_xlabel('Cycle number', fontsize=12)
        ax2.set_ylabel('CE current density [mA cm$^{-2}$]', fontsize=12)
        ax2.plot(self.fullStats[:,0], self.fullStats[:,19], 'ko-', label='charge')
        ax2.plot(self.fullStats[:,0], np.abs(self.fullStats[:,20]), 'kD-', label='discharge')

        # Put a legend below current axis
        ax1.legend(loc='upper center', bbox_to_anchor=(1, -0.09), ncol=3, fontsize=12)
        fig.tight_layout(rect=(0,0.05,1,1))
        
    
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
    
    