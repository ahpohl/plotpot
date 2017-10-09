# -*- coding: utf-8 -*-
import sys, os
import numpy as np
import matplotlib.pyplot as plt
from plotpot.data import Data


class Plot(object):

    def __init__(self, args, showArgs, bat):
        self.args = args
        self.showArgs = showArgs
        self.bat = bat
        
    
    def drawPlots(self):
        """call plotting functions"""

        # set current working directory
        plt.rcParams['savefig.directory'] = os.getcwd()
        
        # set plot range according to show arguments cycles, time and points
        self.setPlotRange()
        
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
            plt.figure(n)
            plt.savefig(stem + suffix[n] + ext)
           
    
    def showPlots(self):
        """show plots on sceen"""
        plt.show()
    

    def setPlotRange(self):
        """set plot range according to show arguments cycles, time and points"""
        
        # get indices of full cycle limits
        if self.bat.showArgs['cycles'] is not None:
            # convert cycles to zero based index
            self.c = (self.bat.showArgs['cycles'][0]-1, self.bat.showArgs['cycles'][1])
            # get indices of half cycle limits
            # convert full cycles into half cycles (with zero based index)
            self.h = ((2*(self.bat.showArgs['cycles'][0])-1)-1, 2*(self.bat.showArgs['cycles'][1]))
            #self.h = (2*self.c[0]-1, 2*self.c[1])
            # get indices of data point limits
            self.p = (self.bat.statPoints[self.c[0]:self.c[1]].flatten()[0],
                      self.bat.statPoints[self.c[0]:self.c[1]].flatten()[-1])
        
        # get indices with --time argument
        elif self.bat.showArgs['time'] is not None:
            # get indices of data point limits
            self.p = np.searchsorted(self.bat.testTime, self.bat.showArgs['time'])
            # get indices of half cycle limits
            self.h = np.searchsorted(self.bat.halfStatPoints[:,1], self.p)
            self.h[1] += 1 
            # get indices of full cycle limits
            self.c = np.searchsorted(self.bat.statPoints[:,1], self.p)
            self.c[1] += 1
            
        # get indices with --data argument
        elif self.bat.showArgs['points'] is not None:
            # get indices of data point limits
            self.p = self.bat.showArgs['points']
            # get indices of half cycle limits
            self.h = np.searchsorted(self.bat.halfStatPoints[:,1], self.p)
            self.h[1] += 1 
            # get indices of full cycle limits
            self.c = np.searchsorted(self.bat.statPoints[:,1], self.p)
            self.c[1] += 1
            
        # no range argument given
        else:
            self.c = (0, len(self.bat.statCycles))
            self.h = (0, len(self.bat.halfStatCycles))
            self.p = (0, len(self.bat.points))
            
        if self.args.verbose:
            print("Full cycles: %d-%d, Half cycles: %d-%d, Data Points: %d-%d" 
                  % (self.c[0], self.c[1], self.h[0], self.h[1], self.p[0], self.p[1]))
        
        
    ### plot methods ###
    
    def figVoltageCapacity(self):
        """plot galvanostatic profile"""

        # half cell
        if not self.bat.isFullCell:
            fig = plt.figure(1)
            fig.canvas.set_window_title("Figure 1 - galvanostatic profile")
            
            # working electrode plot
            ax1 = fig.add_subplot(111)
            #ax1.autoscale(axis='x', tight='tight')
            ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]', fontsize=12)
            ax1.set_ylabel('Voltage [V]', fontsize=12)
            
            # loop over half cycles
            for (a,b) in self.bat.halfStatPoints[self.h[0]:self.h[1]]:
                if a < self.p[0]: a = self.p[0]
                if b > self.p[1]: b = self.p[1]
                ax1.plot(self.bat.we.capacity[a:b], self.bat.we.voltage[a:b], 'k-')
    
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
            for (a,b) in self.bat.halfStatPoints[self.h[0]:self.h[1]]:
                if a < self.p[0]: a = self.p[0]
                if b > self.p[1]: b = self.p[1]
                ax1.plot(self.bat.we.capacity[a:b], self.bat.we.voltage[a:b], 'k-')
                ax2.plot(self.bat.ce.capacity[a:b], self.bat.ce.voltage[a:b], 'k-')                

        fig.tight_layout()
        
    
    def figVoltageCapacityCircle(self):
        """plot galvanostatic profile (circle)"""
        
        # half cell
        if not self.bat.isFullCell:
            fig = plt.figure(2)
            fig.canvas.set_window_title("Figure 2 - galvanostatic profile (circle)")
            
            # working electrode plot
            ax1 = fig.add_subplot(111)
            #ax1.autoscale(axis='x', tight='tight')
            ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]', fontsize=12)
            ax1.set_ylabel('Voltage [V]', fontsize=12)
            
            # loop over half cycles
            curCap = 0; prevCap = 0
            for ((a,b),h) in zip(self.bat.halfStatPoints[self.h[0]:self.h[1]], self.bat.halfStatCycles[self.h[0]:self.h[1]]):
                if a < self.p[0]: a = self.p[0]
                if b > self.p[1]: b = self.p[1]
                curCap = self.bat.we.capacity[b-1]
                if h % 2 == 0:
                    ax1.plot(self.bat.we.capacity[a:b], self.bat.we.voltage[a:b], 'k-')
                else:
                    ax1.plot(-1*self.bat.we.capacity[a:b]+prevCap, self.bat.we.voltage[a:b], 'k-')
                prevCap = curCap
                
        # full cell
        else:
            fig = plt.figure(2, figsize=(12,6))
            fig.canvas.set_window_title("Figure 2 - full cell galvanostatic profile (circle)")
            
            # working electrode
            ax1 = fig.add_subplot(121)
            ax1.autoscale(axis='x', tight='tight')
            ax1.set_xlabel('Specific capacity [mAh g$^{-1}$]', fontsize=12)
            ax1.set_ylabel('WE potential [V]', fontsize=12)
    
            # counter electrode
            ax2 = fig.add_subplot(122)
            ax2.autoscale(axis='x', tight='tight')
            ax2.set_xlabel('Specific capacity [mAh g$^{-1}$]', fontsize=12)
            ax2.set_ylabel('CE potential [V]', fontsize=12)
            
            
            # loop over half cycles
            curCap = []; prevCap = [0,0]
            for ((a,b),h) in zip(self.bat.halfStatPoints[self.h[0]:self.h[1]], self.bat.halfStatCycles[self.h[0]:self.h[1]]):
                if a < self.p[0]: a = self.p[0]
                if b > self.p[1]: b = self.p[1]
                curCap = [self.bat.we.capacity[b-1], self.bat.ce.capacity[b-1]]
                if h % 2 == 0:
                    ax1.plot(self.bat.we.capacity[a:b], self.bat.we.voltage[a:b], 'k-')
                    ax2.plot(self.bat.ce.capacity[a:b], self.bat.ce.voltage[a:b], 'k-')
                else:
                    ax1.plot(-1*self.bat.we.capacity[a:b]+prevCap[0], self.bat.we.voltage[a:b], 'k-')
                    ax2.plot(-1*self.bat.ce.capacity[a:b]+prevCap[1], self.bat.ce.voltage[a:b], 'k-')
                prevCap = curCap
        
        fig.tight_layout()
        
        
    def figVoltageCurrent(self):
        """Voltage and current vs. time plot"""
        
        # half cell
        if not self.bat.isFullCell:       
            fig = plt.figure(3, figsize=(10,5))
            fig.canvas.set_window_title("Figure 3 - voltage, current vs. time")

            # working electrode plot
            ax1 = fig.add_subplot(111)
            ax1.autoscale(axis='x', tight='tight')
            ax1.set_xlabel('Time [h]', fontsize=12)
            ax1.set_ylabel('Voltage [V]', fontsize=12)
            ax2 = ax1.twinx()
            ax2.autoscale(axis='x', tight='tight')
            ax2.set_ylabel('Current [mA]', fontsize=12)
           
            ax1.plot(self.bat.testTime[self.p[0]:self.p[1]], 
                     self.bat.we.voltage[self.p[0]:self.p[1]], 'k-', label='voltage')
            ax2.plot(self.bat.testTime[self.p[0]:self.p[1]], 
                     self.bat.current[self.p[0]:self.p[1]], 'k--', label='current')
            
        # full cell
        else:
            fig = plt.figure(3, figsize=(10,8))
            fig.canvas.set_window_title("Figure 3 - full cell voltage, current vs. time")
            
            # working electrode plot
            ax1 = fig.add_subplot(211)
            ax1.autoscale(axis='x', tight='tight')
            ax1.set_xlabel('Time [h]', fontsize=12)
            ax1.set_ylabel('WE potential [V]', fontsize=12)
            ax2 = ax1.twinx()
            ax2.autoscale(axis='x', tight='tight')
            ax2.set_ylabel('Current [mA]', fontsize=12)
           
            ax1.plot(self.bat.testTime[self.p[0]:self.p[1]], 
                     self.bat.we.voltage[self.p[0]:self.p[1]], 'k-', label='voltage')
            ax2.plot(self.bat.testTime[self.p[0]:self.p[1]], 
                     self.bat.current[self.p[0]:self.p[1]], 'k--', label='current')
            
            # counter electrode plot
            ax3 = fig.add_subplot(212)
            ax3.autoscale(axis='x', tight='tight')
            ax3.set_xlabel('Time [h]', fontsize=12)
            ax3.set_ylabel('CE potential [V]', fontsize=12)
            ax4 = ax3.twinx()
            ax4.autoscale(axis='x', tight='tight')
            ax4.set_ylabel('Current [mA]', fontsize=12)
           
            ax3.plot(self.bat.testTime[self.p[0]:self.p[1]], 
                     self.bat.ce.voltage[self.p[0]:self.p[1]], 'k-', label='voltage')
            ax4.plot(self.bat.testTime[self.p[0]:self.p[1]], 
                     -1*self.bat.current[self.p[0]:self.p[1]], 'k--', label='current')
        
        fig.tight_layout()
        

    def figTemperature(self):
        """auxiliary channel vs. time plot"""
    
        fig = plt.figure(4, figsize=(10,5))
        fig.canvas.set_window_title("Figure 4 - temperature")
        
        ax1 = fig.add_subplot(111)
        ax1.autoscale(axis='x', tight='tight')
        ax1.set_xlabel('Time [h]', fontsize=12)
        ax1.set_ylabel('Temperature [°C]', fontsize=12)

        ax1.plot(self.bat.testTime[self.p[0]:self.p[1]], 
                 self.bat.temperature[self.p[0]:self.p[1]], 'k-')
        
        fig.tight_layout()
        
        
    def figDQDV(self):
        """cyclovoltammogram from galvanostatic cycles"""

        # translate smooth level to window length (odd integer)
        level = 0
        if self.args.smooth:
            level = (self.args.smooth-1) * 6 + 5
            
        # half cell
        if not self.bat.isFullCell:
            fig = plt.figure(5)
            fig.canvas.set_window_title("Figure 5 - differential capacity")
            
            # working electrode
            ax1 = fig.add_subplot(111)
            ax1.set_xlabel('Voltage [V]', fontsize=12)
            ax1.set_ylabel('dQ/dV [As V$^{-1}$]', fontsize=12) 
            
            # loop over half cycles
            for ((a,b),s) in zip(self.bat.halfStatPoints[self.h[0]:self.h[1]], self.bat.halfStatStep[self.h[0]:self.h[1]]):
                if a < self.p[0]: a = self.p[0]
                if b > self.p[1]: b = self.p[1]

                if s > 0 and (self.args.smooth is not None):
                    ax1.plot(self.smooth(self.bat.we.voltage[a:b], window_len=level, window='hamming'),
                             self.smooth(self.bat.we.dqdv[a:b], window_len=level, window='hamming'), 'k-')
                elif s > 0:
                    ax1.plot(self.bat.we.voltage[a:b], self.bat.we.dqdv[a:b], 'k-')
                elif s < 0 and (self.args.smooth is not None):
                    ax1.plot(self.smooth(self.bat.we.voltage[a:b], window_len=level, window='hamming'),
                             self.smooth(-1*self.bat.we.dqdv[a:b], window_len=level, window='hamming'), 'k-')
                elif s < 0:
                    ax1.plot(self.bat.we.voltage[a:b], -1*self.bat.we.dqdv[a:b], 'k-')
                else:
                    sys.exit("ERROR: rest cycles not supported")
                    
        # full cell
        else:
            fig = plt.figure(5, figsize=(12,6))
            fig.canvas.set_window_title("Figure 5 - full cell differential capacity")
            
            # working electrode
            ax1 = fig.add_subplot(121)
            ax1.set_xlabel('WE potential [V]', fontsize=12)
            ax1.set_ylabel('dQ/dV [As V$^{-1}$]', fontsize=12)
            
            # counter electrode
            ax2 = fig.add_subplot(122)
            ax2.set_xlabel('CE potential [V]', fontsize=12)
            ax2.set_ylabel('dQ/dV [As V$^{-1}$]', fontsize=12)
                    
            # loop over half cycles
            for ((a,b),s) in zip(self.bat.halfStatPoints[self.h[0]:self.h[1]], self.bat.halfStatStep[self.h[0]:self.h[1]]):
                if a < self.p[0]: a = self.p[0]
                if b > self.p[1]: b = self.p[1]

                if s > 0 and (self.args.smooth is not None):
                    ax1.plot(self.smooth(self.bat.we.voltage[a:b], window_len=level, window='hamming'),
                             self.smooth(self.bat.we.dqdv[a:b], window_len=level, window='hamming'), 'k-')
                    ax2.plot(self.smooth(self.bat.ce.voltage[a:b], window_len=level, window='hamming'),
                             self.smooth(self.bat.ce.dqdv[a:b], window_len=level, window='hamming'), 'k-')
                elif s > 0:
                    ax1.plot(self.bat.we.voltage[a:b], self.bat.we.dqdv[a:b], 'k-')
                    ax2.plot(self.bat.ce.voltage[a:b], self.bat.ce.dqdv[a:b], 'k-')
                elif s < 0 and (self.args.smooth is not None):
                    ax1.plot(self.smooth(self.bat.we.voltage[a:b], window_len=level, window='hamming'),
                             self.smooth(-1*self.bat.we.dqdv[a:b], window_len=level, window='hamming'), 'k-')
                    ax2.plot(self.smooth(self.bat.ce.voltage[a:b], window_len=level, window='hamming'),
                             self.smooth(-1*self.bat.ce.dqdv[a:b], window_len=level, window='hamming'), 'k-')
                elif s < 0:
                    ax1.plot(self.bat.we.voltage[a:b], -1*self.bat.we.dqdv[a:b], 'k-')
                    ax2.plot(self.bat.ce.voltage[a:b], -1*self.bat.ce.dqdv[a:b], 'k-')
                else:
                    sys.exit("ERROR: rest cycles not supported")
                    
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
    
    