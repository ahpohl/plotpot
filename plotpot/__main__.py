# -*- coding: utf-8 -*-

import sys
import argparse
from distutils.spawn import find_executable
from plotpot.plotpot import Plotpot

# check if prerequisites are installed
try:
    from plotpot.__version__ import version
except ImportError as error:
    print("Package not installed with pip.")
    sys.exit(error)
    
try:
    import numpy as np
except ImportError as error:
    print("Please install Python Numpy from http://numpy.scipy.org/")
    sys.exit(error)
    
try:
    import matplotlib.pyplot as plt
except ImportError as error:
    print("Please install Python Matplotlib from http://matplotlib.sourceforge.net/")
    sys.exit(error)
    
convpot_program = find_executable("convpot")
if not convpot_program:
    print("Please install Convpot from https://github.com/ahpohl/convpot/")
    sys.exit()

def main():
    
    # parse command line options
    parser = argparse.ArgumentParser(usage='%(prog)s [-h] [options] filename',
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description="""Plotpot is a Python module that plots potentiostatic data automatically imported
with Convpot. It keeps a journal with meta information such as mass of active
material, capacity etc. for later use.""",
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
                    help="data file name")
    parser.add_argument('-V', '--version', action='version', version=version)
    parser.add_argument('-v', '--verbose', action='store_true',
                    help="be more verbose")
    parser.add_argument('-D', '--debug', action='store_true',
                    help="show debug messages")
    parser.add_argument('-q', '--quiet', action='store_true',
                    help="do not display plots")
    parser.add_argument('-e', '--export', action='store_true',
                    help="export data, statistics and figures")
    parser.add_argument('-f', '--force', action='store_true',
                    help="skip up-to-date check")
    parser.add_argument('-b', '--biologic-ce', action='store_true',
                    help="use Biologic counter electrode potential")
    
    # plot group
    group_plot = parser.add_argument_group("plot arguments")
    
    group_plot.add_argument('-p', '--plot', default='1',
                    help="select plots, default %(default)s")
    group_plot.add_argument('-s', '--smooth', type=int, choices=range(1,5),
                    help="smooth level") # window length
    
    # mutually exclusive arguments in plot group
    group_filter = group_plot.add_mutually_exclusive_group()
    
    group_filter.add_argument('-c', '--cycles',
                    help="select cycles")
    group_filter.add_argument('-t', '--time',
                    help="select time in hours")
    group_filter.add_argument('-d', '--data',
                    help="select data points")
    
    # journal group
    group_journal = parser.add_argument_group("journal arguments")
    
    group_journal.add_argument("--journal", action="store_true",
                    help="show the journal table")
    group_journal.add_argument("--delete", type=int,
                    help="delete a row id from journal")
    
    args = parser.parse_args()

    # print usage if no filename is given
    if not (args.filename or args.journal):
        parser.print_usage()
        parser.exit()
        
    # run main program
    Plotpot(args)

    return

if __name__ == '__main__':
    main()

