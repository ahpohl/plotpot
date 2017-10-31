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

    # create the parser for the "show" command
    parser_show = subparsers.add_parser('show',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            help='show plots',
            description=textwrap.dedent("""
            available plot types:
               1  Specific capacity
               2  Specific capacity (circle plot) 
               3  Voltage and current
               4  Temperature
               5  dQ/dV
               6  Specific capacity [mAh/g]
               7  Volumetric capacity [Ah/L]
               8  Specific energy [Wh/kg]
               9  Volumetric energy [Wh/L] 
              10  Specific current density [mA/g]
              11  Current density [mA/cm²]
              12  C-rate 
              13  Hysteresis
              14  Coulombic efficiency
              """)                    
    )
 
    # positional plot argument
    parser_show.add_argument('showFileName', metavar="filename", help="data file name")    
    
    # optional plot arguments
    parser_show.add_argument('-q', '--quiet', action='store_true',
                    help="do not show plots", dest="showQuiet")
    parser_show.add_argument('-e', '--export', action='store_true',
                    help="export data, statistics and figures", dest="showExport")
    parser_show.add_argument('-f', '--force', action='store_true',
                    help="skip up-to-date check", dest="showForce")
    parser_show.add_argument('-p', '--plot', default='1', metavar='N',
                    help="select plot type", dest="showPlot")
    parser_show.add_argument('-s', '--smooth', type=int, choices=range(1,6), dest="showSmooth",
                    metavar='N', help="smooth dQ/dV plot [%(choices)s]") # window length
    
    # mutually exclusive arguments for plot command
    group_select = parser_show.add_mutually_exclusive_group()
    
    group_select.add_argument('-c', '--cycles', metavar='N',
                    help="select cycles", dest="showCycles")
    group_select.add_argument('-t', '--time', metavar='N',
                    help="select time [in hours]", dest="showTime")
    group_select.add_argument('-d', '--data', metavar='N',
                    help="select data points", dest="showData") 
    
    # create the parser for the "merge" command
    parser_merge = subparsers.add_parser('merge', help='merge files')
    
    parser_merge.add_argument('mergeFileNames', metavar='file', nargs='*',
                    help="filenames of data to merge")
    parser_merge.add_argument('-l', '--list', metavar='FN',
                    dest='mergeList', help="text file with filenames")
    parser_merge.add_argument('-o', '--output', metavar='FN',
                    dest='mergeOutput', help="change output filename") 
    
    # create the parser for the "journal" command
    parser_journal = subparsers.add_parser('journal', help='display journal')

    parser_journal.add_argument('-e', '--export', action='store_true',
                    dest='journalExport', help="export journal to csv file")    
    parser_journal.add_argument('-d', '--delete', type=int, metavar='ID',
                    dest='journalDelete', help="delete a row from journal")
    parser_journal.add_argument('-s', '--show', type=int, metavar='ID',
                    dest='journalShow', help="show merged files for row")    
    
    # parse command line
    args = parser.parse_args()
    
    # print help if no subcommand is given
    if not args.subcommand:
        parser.print_help()
        parser.exit()
        
    # print merge subcommand help
    if args.subcommand == "merge" and not (args.mergeFileNames or args.mergeList):
        parser_merge.print_help()
        parser.exit()
    
    # run main program
    Plotpot(args)

    return

if __name__ == '__main__':
    main()