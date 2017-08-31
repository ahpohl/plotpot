# -*- coding: utf-8 -*-
import argparse, textwrap
from plotpot.__version__ import version
from plotpot.plotpot import Plotpot

def main():
    
    # create the top-level parser
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent("""
            Plotpot is a Python module that plots potentiostatic data imported with
            Convpot. It keeps a journal with meta information for later use."""),
            epilog="""For more help see page of sub-command:\n    %(prog)s <command> -h"""
    )
 
    # optional top level arguments
    parser.add_argument('-V', '--version', action='version', version=version)
    parser.add_argument('-v', '--verbose', action='count',
                    help="be more verbose")

    # create sub-command
    subparsers = parser.add_subparsers(title='available commands', metavar='',
                    dest='subcommand') 

    # create the parser for the "plot" command
    parser_show = subparsers.add_parser('show',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            help='show plots',
            description=textwrap.dedent("""
            available plot types:
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
    )
    
    # positional plot argument
    parser_show.add_argument('filename', help="data file name")    
    
    # optional plot arguments
    parser_show.add_argument('-q', '--quiet', action='store_true',
                    help="do not show plots")
    parser_show.add_argument('-e', '--export', action='store_true',
                    help="export data, statistics and figures")
    parser_show.add_argument('-f', '--force', action='store_true',
                    help="skip up-to-date check")
    parser_show.add_argument('-p', '--plot', default='1', metavar='N',
                    help="select plot type")
    parser_show.add_argument('-s', '--smooth', type=int, choices=range(1,5),
                    metavar='N', help="smooth dQ/dV plot [%(choices)s]") # window length
    
    # mutually exclusive arguments for plot command
    group_select = parser_show.add_mutually_exclusive_group()
    
    group_select.add_argument('-c', '--cycles', metavar='N',
                    help="select cycles")
    group_select.add_argument('-t', '--time', metavar='N',
                    help="select time [in hours]")
    group_select.add_argument('-d', '--data', metavar='N',
                    help="select data points")   
    
    # create the parser for the "journal" command
    parser_journal = subparsers.add_parser('journal', help='manipulate journal')
    
    parser_journal.add_argument('-d', '--delete', type=int, metavar='ID',
                    help="delete a row from journal")
    
    # parse command line
    args = parser.parse_args()
    
    # print help if no subcommand is given
    if args.subcommand is None:
        parser.print_help()
    
    # run main program
    Plotpot(args)

    return

if __name__ == '__main__':
    main()