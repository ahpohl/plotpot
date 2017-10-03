# -*- coding: utf-8 -*-
import sys, os
import numpy as np
import matplotlib.pyplot as plt
from plotpot.data import Data


class Plot(object):

    def __init__(self, args, bat):
        self.args = args
        self.bat = bat
        
    
    def drawPlots(self):
        """call plotting functions"""

        # set current working directory
        plt.rcParams['savefig.directory'] = os.getcwd()
        
        for n in self.bat.showArgs['plots']:
            if n == 1:
                self.figVoltageCapacity()
            elif n == 2:
                self.figVoltageCapacityCircle()
            elif n == 3:
                self.figVoltageCurrent()
            elif n == 4:
                self.figTemperature()
            elif n == 5:
                self.figDQDV()
            elif n == 6:
                self.figSpecificCapacity()
            elif n == 7:
                self.figVolumetricCapacity()
            elif n == 8:
                self.figSpecificEnergy()
            elif n == 9:
                self.figVolumetricEnergy()
            elif n == 10:
                self.figSpecificCurrentDensity()
            elif n == 11:
                self.figVolumetricCurrentDensity()
            elif n == 12:
                self.figEfficiency()
            elif n == 13:
                self.figHysteresis()
            elif n == 14:
                self.figCRate()
            else:
                sys.exit("ERROR: Plot number not defined.")
        

    def saveFigure(self):
        """save plot into png image"""

        stem = self.args.filename.split('.')[0]
        ext = '.png'
        
        suffix = {1: '_voltage_vs_capacity',
                  2: '_capacity_circle',
                  3: '_voltage_current_vs_time',
                  4: '_temperature_vs_time',
                  5: '_dqdv',
                  6: '_specific_capacity',
                  7: '_volumetric_capacity',
                  8: '_specific_energy',
                  9: '_volumetric_energy',
                  10: '_specific_current_density',
                  11: '_volumetric_current_density',                 
                  12: '_efficiency',
                  13: '_hysteresis',
                  14: '_c_rate'}

        for n in self.plots:
            fig = plt.figure(n)
            plt.savefig(stem + suffix[n] + ext)
           
    
    def showPlots(self):
        """show plots on sceen"""
        plt.show()
        
    
    def figVoltageCapacity(self):
        """plot galvanostatic profile"""
        
        # half cell
        if not self.bat.isFullCell:
            fig = plt.figure(1)
            fig.canvas.set_window_title("Figure 1 - galvanostatic profile")
            
            # working electrode plot
            ax1 = fig.add_subplot(111)
            ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]', fontsize=12)
            ax1.set_ylabel('Voltage [V]', fontsize=12)
            
            # loop over half cycles
            for c in self.bat.halfStatCycles:
                capacity = self.bat.we.capacity[self.bat.halfStatPoints[c,0]:self.bat.halfStatPoints[c,1]]
                voltage = self.bat.we.voltage[self.bat.halfStatPoints[c,0]:self.bat.halfStatPoints[c,1]]
                ax1.plot(capacity, voltage, 'k-', label='half cycle')
    
        # full cell
        else:
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
        
        
             # loop over half cycles
            for c in self.bat.halfStatCycles:
                weCapacity = self.bat.we.capacity[self.bat.halfStatPoints[c,0]:self.bat.halfStatPoints[c,1]]
                weVoltage = self.bat.we.voltage[self.bat.halfStatPoints[c,0]:self.bat.halfStatPoints[c,1]]
                ax1.plot(weCapacity, weVoltage, 'k-', label='half cycle')
                
                ceCapacity = self.bat.ce.capacity[self.bat.halfStatPoints[c,0]:self.bat.halfStatPoints[c,1]]
                ceVoltage = self.bat.ce.voltage[self.bat.halfStatPoints[c,0]:self.bat.halfStatPoints[c,1]]
                ax2.plot(ceCapacity, ceVoltage, 'k-', label='half cycle')
                
        fig.tight_layout()

    
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
    
    