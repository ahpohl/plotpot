# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 20:08:57 2017

@author: geapoh
"""
import sys
import argparse, textwrap

def main():
    
    # create the top-level parser
    parser = argparse.ArgumentParser(
            description="""
            Plotpot is a Python module that plots potentiostatic data imported with
            Convpot. It keeps a journal with meta information for later use.""",
            epilog="""
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
              13  Specific capacity (circle plot)"""
    )
    
    parser.add_argument('-V', '--version', action='version', version='version-git')
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
    
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "plot" command
    parser_plot = subparsers.add_parser('plot', help='plot help')
    
    parser_plot.add_argument('filename', help="data file name")
    
    parser_plot.add_argument('-p', '--plot', default='1', metavar='N',
                    help="select plot, default %(default)s")
    parser_plot.add_argument('-s', '--smooth', type=int, choices=range(1,5),
                    metavar='N', help="smooth level %(choices)s") # window length
    
    # mutually exclusive arguments for plot command
    group_select = parser_plot.add_mutually_exclusive_group()
    
    group_select.add_argument('-c', '--cycles', metavar='N',
                    help="select cycles")
    group_select.add_argument('-t', '--time', metavar='N',
                    help="select time in hours")
    group_select.add_argument('-d', '--data', metavar='N',
                    help="select data points")
    
    # create the parser for the "journal" command
    parser_b = subparsers.add_parser('journal', help='journal help')
    
    parser_b.add_argument("--show", action="store_true",
                    help="show the journal table")
    parser_b.add_argument("--delete", type=int, metavar='ID',
                    help="delete a row from journal")
    
    args = parser.parse_args()
    
    return
    
if __name__ == '__main__':
    main()