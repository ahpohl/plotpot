# -*- coding: utf-8 -*-

import sys
import argparse, textwrap
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
    
    # create the top-level parser
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent("""
            Plotpot is a Python module that plots potentiostatic data imported with
            Convpot. It keeps a journal with meta information for later use.""")
    )
            
    epilog=textwrap.dedent("""
            available plot types:
            =====================
               1  Voltage vs. specific capacity
               2  Voltage + current vs. time
               3  Temperature vs. time
               4  Specific capacity [mAh/g]
               5  Specific energy [Wh/kg]
               6  Volumetric energy [Wh/L] 
               7  Coulombic efficiency
               8  Mean voltages and hysteresis
               9  dQ/dV
              10  C-rate
              11  Specific current density [mA/g]
              12  Current density [mA/cm²]
              13  Specific capacity (circle plot)""")
 
    # optional top level arguments
    parser.add_argument('-V', '--version', action='version', version='version-git')
    parser.add_argument('-v', '--verbose', action='store_true',
                    help="be more verbose")
    parser.add_argument('-D', '--debug', action='store_true',
                    help="show debug messages")

    # create sub-command
    subparsers = parser.add_subparsers(title='available commands', metavar='') 

    # create the parser for the "plot" command
    parser_plot = subparsers.add_parser('plot', help='create plots')

    # positional plot argument
    parser_plot.add_argument('filename', help="data file name")    
    
    # optional plot arguments
    parser_plot.add_argument('-q', '--quiet', action='store_true',
                    help="do not display plots")
    parser_plot.add_argument('-e', '--export', action='store_true',
                    help="export data, statistics and figures")
    parser_plot.add_argument('-f', '--force', action='store_true',
                    help="skip up-to-date check")
    parser_plot.add_argument('-b', '--bio-ce', action='store_true',
                    help="Biologic counter electrode")
    parser_plot.add_argument('-p', '--plot', default='1', metavar='N',
                    help="select plot")
    parser_plot.add_argument('-s', '--smooth', type=int, choices=range(1,5),
                    metavar='N', help="smooth level [%(choices)s]") # window length
    
    # mutually exclusive arguments for plot command
    group_select = parser_plot.add_mutually_exclusive_group()
    
    group_select.add_argument('-c', '--cycles', metavar='N',
                    help="select cycles")
    group_select.add_argument('-t', '--time', metavar='N',
                    help="select time in hours")
    group_select.add_argument('-d', '--data', metavar='N',
                    help="select data points")   
    
    # create the parser for the "journal" command
    parser_journal = subparsers.add_parser('journal', help='manipulate journal')
    
    #parser_journal.add_argument('-s', '--show', action="store_true",
    #                help="show the journal table")
    
    parser_journal.add_argument('-d', '--del', type=int, metavar='ID',
                    help="delete a row from journal")
    
    # parse command line arguments
    args = parser.parse_args()
        
    # run main program
    #Plotpot(args)

    return

if __name__ == '__main__':
    main()