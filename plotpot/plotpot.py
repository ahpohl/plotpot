#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, os
import subprocess
from distutils.spawn import find_executable

# import numpy
try:
    import numpy as np
except ImportError as error:
    print("Please install Python Numpy from http://numpy.scipy.org/")
    sys.exit(error)
    
# import own files
from globals import parser,args
from plot import plot
import parse
from export import export
from data import DataSqlite
from journal import JournalSqlite

# begin main program
    
def main():
    
    # print usage if no filename is given
    if not args.filename and not args.journal:
        parser.print_usage()
        parser.exit()
        
    #disable division by zero warnings
    np.seterr(divide='ignore')
    
    # create global database in program directroy
    envCfg = os.environ.get('PLOTPOT_PATH')
    fileCfg = "plotpot-journal.dat"
    if envCfg:
        journalDbPath = os.path.join(envCfg, fileCfg)
    else:
        journalDbPath = os.path.join(os.path.dirname(sys.argv[0]), fileCfg)
        
    # check if journal file exists
    try:
        fh = open(journalDbPath, "r")
    except IOError as e:
        print(e)
        create = input("Do you want to create a new journal file (Y,n)? ")
        if create == 'n':
            sys.exit()
            
    # store mass and capacity in dict
    # mass: active mass [mg]
    # cap: theoretical capacity [mAh/g]
    # area: electrode area [cm²]
    # volume: volume of electrode [µL]
    massStor = {'mass': 0, 'cap': 0, 'area': 0, 'volume': 0}
			   
    # create journal object and schema
    journalDb = JournalSqlite(journalDbPath, massStor)
    
    # update schema if needed
    journalDb.updateSchema()
        
    # delete journal entry    
    if args.delete and args.journal:
        journalDb.deleteRow("Journal_Table", args.delete)
        journalDb.printJournal("Journal_Table")
        sys.exit()
        
    # print arbin.cfg journal file
    if args.journal:
        journalDb.printJournal("Journal_Table")
        sys.exit()
    
    # check if filename exists
    path = os.path.abspath(args.filename)
    try:
        fh = open(path, "r")
    except IOError as e:
        sys.exit(e)
        
    # execute external program to convert args[0] into sqlite file
    mdbpath = find_executable("convpot") # search path
    
    if mdbpath == None:
        mdbpath = find_executable("convpot", sys.argv[0]) # search current dir
    
    if not mdbpath:
        sys.exit("ERROR: converter program not found.")
        
    # test if mdbpath is executable
    if not os.access(mdbpath, os.X_OK):
        sys.exit("ERROR: converter program not executable.")
    
    sqlfile = path.rsplit('.')[0]+'.sqlite'
    sqlext = path.rsplit('.')[1]
    
    # create data object  
    dataDb = DataSqlite(sqlfile)
    
    # test if sqlite file needs updating
    isUpdate = dataDb.checkFileSize(sqlfile)
    
    if (isUpdate or args.force) and sqlext != "sqlite":
    
        mdbargs = []
        mdbargs.append(mdbpath)
    
        if args.verbose:
            mdbargs.append("--verbose")
    
        mdbargs.append(args.filename)
    
        try:
            subprocess.check_call(mdbargs)
        except subprocess.CalledProcessError as e:
            sys.exit(e)
        
    # parse plot option
    plots = parse.plot_option()
    
    # read file name and start datetime
    fileNameDate = dataDb.getNameAndDate()
    fileCount = dataDb.getFileCount()
    
    if fileCount > 1:
        fileNameList = list(fileNameDate)
        fileNameList[0] = args.filename
        fileNameDate = tuple(fileNameList)
    
    # search arbin.cfg if battery exists in file
    searchResult = journalDb.searchJournal(fileNameDate)
    
    # if entry not found, fetch data from data file (global or file table)
    if searchResult == None:
        journalEntry = dataDb.getFileDetails()
        
        # treat merged file different than single file
        if fileCount > 1:
            journalList = list(journalEntry)
            journalList[1] = args.filename
            journalList[6] = "merged"
            journalEntry = tuple(journalList)
          
    else:
        # get mass and capapcity from journal
        journalEntry = searchResult
        massStor['mass'] = journalEntry[6]
        massStor['cap'] = journalEntry[7]
        massStor['area'] = journalEntry[8]
        massStor['volume'] = journalEntry[9]
    
    # ask questions
    if any([x in [1,4,5,11] for x in plots]):
        journalDb.ask_mass()
    if 10 in plots:
        journalDb.ask_capacity()
    if any([x in [12] for x in plots]):
        journalDb.ask_area()
    if 6 in plots:
        journalDb.ask_volume()
        
    # update massStor
    massStor = journalDb.get_mass()
                    
    # create new record in journal file if previous record was not found, otherwise update mass
    if searchResult == None:
        journalDb.insertRow("Journal_Table", journalEntry, massStor)
    else:
        journalDb.updateColumn("Journal_Table", "Mass", massStor['mass'], journalEntry)
        journalDb.updateColumn("Journal_Table", "Capacity", massStor['cap'], journalEntry) 
        journalDb.updateColumn("Journal_Table", "Area", massStor['area'], journalEntry)
        journalDb.updateColumn("Journal_Table", "Volume", massStor['volume'], journalEntry)       
       
    if args.time:
        # parse time option
        time_cmd = parse.range_option(args.time)
        time_cmd = [float(x) for x in time_cmd] # now list of floats
        
        # sanity checks
        if time_cmd[0] >= time_cmd[1] or len([x for x in time_cmd if x < 0]) != 0:
            sys.exit("ERROR: Time option out of range.")
        
        time_cmd = [x*3600 for x in time_cmd] # in seconds
    
    elif args.cycles:
        # parse cycles option
        cycles_cmd = parse.range_option(args.cycles)
        cycles_cmd = [int(x) for x in cycles_cmd] # now list of integers
                
        # sanity checks
        if cycles_cmd[0] > cycles_cmd[1] or len([x for x in cycles_cmd if x < 0]) != 0:
            sys.exit("ERROR: Cycles option out of range.")
            
    elif args.data:
        # parse data point option
        data_cmd = parse.range_option(args.data)
        data_cmd = [int(x) for x in data_cmd] # now list of integers
        
        #sanity checks
        if data_cmd[0] > data_cmd[1] or len([x for x in data_cmd if x < 0]) != 0:
            sys.exit("ERROR: Data option out of range.")
    
    # fetch all data
    data = dataDb.getData()
    
    if not data.any():
        data = np.zeros((1,12))
    
    if args.debug:
        print("data:")
        print(data.shape)
    
    data[:,1] = data[:,1]+1 # one based cycle index
    
    # fix discharge capacity and energy being negative
    data[:,8] = np.abs(data[:,8])
    data[:,9] = np.abs(data[:,9])

    # fetch statistics
    stats = dataDb.getStatistics()
    
    if not stats.any():
        stats = np.zeros((1,13))
    
    if args.debug:
        print("stats:")
        print(stats.shape)
        
    stats[:,0] = stats[:,0]+1 # one based cycle index
    
    # fix discharge capacity and energy being negative
    stats[:,6] = np.abs(stats[:,6])
    stats[:,8] = np.abs(stats[:,8])
    
    # get number of cycles
    numberOfCycles = np.unique(stats[:,0])
        
    # filter data according to --cycles option
    if args.cycles:
        data = data[np.logical_and(cycles_cmd[0] <= data[:,1], data[:,1] <= cycles_cmd[1])]
        stats = stats[np.logical_and(cycles_cmd[0] <= stats[:,0], stats[:,0] <= cycles_cmd[1])]
    
    # filter data according to --data option
    elif args.data:
        data = data[np.logical_and(data_cmd[0] <= data[:,0], data[:,0] <= data_cmd[1])]
        stats = stats[np.logical_and(data_cmd[0] <= stats[:,2], stats[:,1] <= data_cmd[1])]
        
    # filter data according to --time option
    elif args.time:
        data = data[np.logical_and(time_cmd[0] <= data[:,3], data[:,3] <= time_cmd[1])]    
        
    # calc extended statistics, convert units
    expStat = export(data, numberOfCycles, stats, massStor)
    statistics = expStat.get_stats()
    
    # create figures    
    fig = plot(plots, data, numberOfCycles, statistics, massStor)
    fig.draw()
                    
    # export  
    if args.export:
        print("INFO: Exporting data, statistics and figures.")
        journalDb.writeJournalEntry(fileNameDate)
        expStat.writeStatisticsTable()
        expStat.writeDataTable()
        expStat.writeVoltageProfile()
        dataDb.writeMergeFileSummary()
        fig.savefigure()
        
    # show plots if quiet option not given
    if not args.quiet:
        fig.show_plots()
    
    return

if __name__ == '__main__':
    main()
