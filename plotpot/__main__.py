# -*- coding: utf-8 -*-

import sys
import argparse
from plotpot.__init__ import __version__

### check if prerequisites numpy, scipy and matplotlib are installed.
def check_prerequisites():
    
    # import numpy
    try:
        import numpy as np
    except ImportError as error:
        print("Please install Python Numpy from http://numpy.scipy.org/")
        sys.exit(error)
        
    # import matplotlib
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        print("Please install Python Matplotlib from http://matplotlib.sourceforge.net/")
        sys.exit(error)
    
    # import smooth    
    try:
        from plotpot import smooth
    except ImportError as error:
        print("Please download smooth.py from http://wiki.scipy.org/Cookbook/SignalSmooth")
        sys.exit(error)

def main():
    
    # check prerequisities
    try:
        check_prerequisites()
    except:
        sys.exit()
    
    # parse command line options
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] [options] filename',
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description="""The script plots data from Arbin (*.res), Biologic (*.mpt), Ivium (*.idf)
    and Gamry (*.DTA) potentiostats. It has the capability to select cycles 
    to be plotted and save images of the plots in PNG format. The results can
    be exported in csv format for plotting in external programs like Origin 
    or Excel. Cycles can be split into separate files using the --zip option.""",
                    epilog="""explanation of the --plot option:
      1   Voltage vs. specific capacity
      2   Voltage + current vs. time
      3   Auxiliary channel vs. time
      4   Specific capacity [mAh/g]
      5   Specific energy [Wh/kg]
      6   Volumetric energy [Wh/L] 
      7   Coulombic efficiency
      8   Mean voltages and hysteresis
      9   dQ/dV
      10  C-rate
      11  Specific current density [mA/g]
      12  Current density [mA/cm²]
      13  Specific capacity (circle)""")
    
    parser.add_argument('filename', nargs='?', default=None,  # make filename optional
                    help="Name of data file")
    parser.add_argument('-V', '--version', action='version', version=__version__)
    
    parser.add_argument('--debug', action='store_true',
                    help="turn on debugging")
    parser.add_argument('-q', '--quiet', action='store_true',
                    help="do not show plots")
    parser.add_argument('-v', '--verbose', action='store_true',
                    help="be more verbose")
    parser.add_argument('-b', '--counter', action='store_true',
                    help="use Biologic counter electrode potential")
    parser.add_argument('-e', '--export', action='store_true',
                    help="export data, statistics and figures")
    parser.add_argument('-f', '--force', action='store_true',
                    help="overwrite sqlite file if up to date")
    
    # plot group
    group_plot = parser.add_argument_group("plot arguments")
    
    group_plot.add_argument('-p', '--plot', default='1',
                    help="select plots, [4-5,7,]{%(default)s}")
    group_plot.add_argument('-o', '--smooth', default=0, type=int, choices=range(0,5),
                    help="smooth level {%(default)s}, off") # Hamming window length
    
    # mutually exclusive arguments in plot group
    group_filter = group_plot.add_mutually_exclusive_group()
    
    group_filter.add_argument('-c', '--cycles',
                    help="select cycles, [1,]5")
    group_filter.add_argument('-t', '--time',
                    help="select time [h], [0,]8")
    group_filter.add_argument('-d', '--data',
                    help="select data points, [1,]100")
    
    # journal group
    group_journal = parser.add_argument_group("arguments for arbin.cfg database")
    
    group_journal.add_argument("--journal", action="store_true",
                    help="select journal table")
    group_journal.add_argument("--config", action="store_true",
                    help="select config table")
    group_journal.add_argument("--delete", type=int,
                    help="delete row")
    group_journal.add_argument("--insert", action="store_true",
                    help="insert row")
    
    args = parser.parse_args()

    # print usage if no filename is given
    if not args.filename and not args.journal:
        parser.print_usage()
        parser.exit()

    return

if __name__ == '__main__':
    main()

