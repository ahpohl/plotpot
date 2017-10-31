# -*- coding: utf-8 -*-
import os,sys
import datetime
import csv
import numpy as np
import sqlite3
from operator import itemgetter
from plotpot.dbmanager import DbManager
  

class Journal(DbManager):
    """class for manipulating the journal"""
    
    def __init__(self, args, globalArgs=None, electrode="working"):
        self.args = args
        self.globalArgs = globalArgs
        self.batElectrode = electrode
        self.setJournalPath()
        super().__init__(self.journalPath)
        self.createSchema()
        self.setJournal()
        self.setMergeFiles()
        
        if self.args.subcommand == "show" or self.args.subcommand == "merge":
            self.bat = DbManager(self.globalArgs["dataFileName"])
            self.setBattery()
            if not self.searchBatProperties():
                self.insertBat()
                if self.batFileCount > 1:
                    self.copyBatteryFiles()
                    
                    
    ### internal methods ###
            
    def __isColumn(self, table, column):
        select_query = '''PRAGMA table_info({0})'''.format(table)
        self.query(select_query)
        resultSql = self.fetchall()
        for row in resultSql:
            isColumn = False;
            if row[1] == column:
                isColumn = True;
                break
        return isColumn


    def __printSql(self, data, header):
        """format journal table"""
        
        # determine len of each column
        lensHeader = [len(x) for x in header]
        lensData = []
        for i in data:
            lensData.append([len(str(x)) for x in i])
        lensData.append(lensHeader)
        lensArray = np.array(lensData)
        colWidths = np.amax(lensArray, axis=0) # get max in each column
        
        formats = []
        for i in colWidths:
            formats.append("%%-%ds" % i)
        pattern = "| "+" | ".join(formats)+" |"
        separator ="+-"+"-+-".join(['-' * n for n in colWidths])+"-+"

        # output on screen
        print(separator)
        print(pattern % header)
        print(separator)
        
        for row in data:
            print(pattern % tuple(row))
        print(separator)
        

    ### general methods ###

    def setJournalPath(self):
        """create journal database in program directory or path specified with
           PLOTPOT_JOURNAL environment variable if the file does not exist
           already"""
        
        self.journalPath = os.environ.get('PLOTPOT_JOURNAL')
        journalFile = "plotpot-journal.dat"
        
        if self.journalPath:
            self.journalPath = os.path.join(self.journalPath, journalFile)
        else:
            home = os.getenv('USERPROFILE') or os.getenv('HOME')
            self.journalPath = os.path.join(home, journalFile)
            
        # check if journal file exists
        try:
            open(self.journalPath, "r")
        except IOError as e:
            print(e)
            create = input("Do you want to create a new journal file (Y,n)? ")
            if create == 'n':
                sys.exit()
                
    
    def getJournalPath(self):
        """return journal path"""
        return self.journalPath
    
        
    def createSchema(self):
        # create schema
        self.query('''CREATE TABLE IF NOT EXISTS Journal_Table (
            Row_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            File_Name TEXT,
            Device TEXT,
            File_Size INTEGER,
            Start_DateTime INTEGER,
            Data_Points INTEGER,
            Comments TEXT,
            Mass DOUBLE DEFAULT 0,
            Capacity DOUBLE DEFAULT 0,
            Area DOUBLE DEFAULT 0,
            Volume DOUBLE DEFAULT 0,
            Loading DOUBLE DEFAULT 0,
            Electrode TEXT)''')
        
        self.query('''CREATE TABLE IF NOT EXISTS Merge_Table (
            Row_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Merge_ID INTEGER,
            File_ID INTEGER,
            File_Name TEXT,
            Device TEXT,
            Plot_Type TEXT,
            File_Size INTEGER,
            Start_DateTime INTEGER,
            Data_Points INTEGER,
            Test_Time DOUBLE,
            Comment TEXT,
            FOREIGN KEY(Merge_ID) REFERENCES Journal_Table(Row_ID) ON DELETE CASCADE)''')
       
        
    def upgradeSchema(self):
        """upgrade journal database schema"""
        
        # table upgrade: test if Global_Table exists ***
        self.query('''SELECT name FROM sqlite_master WHERE type="table" AND name="Global_Table" ''')
        resultSql = self.fetchone()
        if resultSql != None:
            # copy entries from Global_Table to Journal_Table
            self.query('''INSERT INTO Journal_Table (
                File_Name,File_Size,Data_Points,Comments,Start_DateTime,Mass,Capacity) SELECT 
                File_Name,File_Size,Data_Points,Comments,Start_DateTime,Mass,Capacity 
                FROM Global_Table''')
            # delete Global_Table
            self.query('''DROP TABLE IF EXISTS Global_Table''')
            print("Global_Table renamed to Journal_Table.")
            
        # update mass and capacity columns
        if not self.__isColumn("Journal_Table", "Volume"):
            self.query('''UPDATE Journal_Table SET Mass = ROUND(Mass*1e3,2), Capacity = ROUND(Capacity*1e3,2)''')
            print("Columns Mass and Capacity multiplied by 1000.")
            
        # table upgrade: create volume column in Journal_Table if column does not exist
        if not self.__isColumn("Journal_Table", "Volume"):
            self.query('''ALTER TABLE Journal_Table ADD COLUMN Volume DOUBLE DEFAULT 0''')
            print("Column Volume created.")
            
        # add device column
        if not self.__isColumn("Journal_Table", "Device"):
            self.query('''ALTER TABLE Journal_Table ADD COLUMN Device TEXT''')
            self.query('''UPDATE Journal_Table SET Device = ""''')
            self.query('''UPDATE Journal_Table SET Device = "Arbin BT2000" WHERE File_Name LIKE "%.res"''')
            self.query('''UPDATE Journal_Table SET Device = "Gamry Interface 1000" WHERE File_Name LIKE "%.DTA"''')
            self.query('''UPDATE Journal_Table SET Device = "Biologic VMP3" WHERE File_Name LIKE "%.mpt"''')
            self.query('''UPDATE Journal_Table SET Device = "Ivium CompactStat" WHERE File_Name LIKE "%.idf"''')
            self.query('''UPDATE Journal_Table SET Device = "Zahner IM6" WHERE File_Name LIKE "%.txt"''')
            self.query('''UPDATE Journal_Table SET Device = "merged" WHERE File_Name LIKE "%.sqlite"''')
            print("Column Device created.")
            
        # add electrode column
        if not self.__isColumn("Journal_Table", "Electrode"):
            self.query('''ALTER TABLE Journal_Table ADD COLUMN Electrode''')
            self.query('''UPDATE Journal_Table SET Electrode = "working"''')
            print("Column Electrode created.")
            
        # add loading column
        if not self.__isColumn("Journal_Table", "Loading"):
            self.query('''ALTER TABLE Journal_Table ADD COLUMN Loading DOUBLE DEFAULT 0''')
            print("Column Loading created.")
            
    
    ### journal table methods ###

    def setJournal(self):
        """fetch journal table"""
        
        try:
            self.setJournalID()
            self.setJournalFileName()
            self.setJournalMass()
            self.setJournalTheoCapacity()
            self.setJournalArea()
            self.setJournalVolume()
            self.setJournalLoading()
            self.setJournalFileSize()
            self.setJournalPoints()
            self.setJournalDate()
            self.setJournalDevice()
            self.setJournalElectrode()
            self.setJournalComments()
            
        except sqlite3.OperationalError as e:
            print(e)
            self.upgradeSchema()
            sys.exit("INFO: Upgraded journal database schema.")
            
        self.journal = list(zip(self.journalID, self.journalFileName, self.journalMass, self.journalTheoCapacity,
                             self.journalArea, self.journalVolume, self.journalLoading, self.journalFileSize,
                             self.journalPoints, self.journalDate, self.journalDevice, self.journalElectrode,
                             self.journalComments))
            
            
    def getJournal(self):
        """fetch journal table"""
        return self.journal
            
            
    def displayJournal(self):
        """display journal table on screen"""
        header = ("id", "file name", "m [mg]", "C [mAh/g]", "A [cm²]", "V [µL]", "L [mg/cm²]",
                  "file size", "data points", "yyyy-mm-dd hh:mm:ss", "device", "electrode", "comment")
        if len(self.journal) > 0:
            self.__printSql(self.journal, header)
        print('''Journal file: "%s".''' % self.journalPath)
        
        
    def exportJournal(self):
        """export journal table to csv file"""
        journalCSV = self.journalPath.split('.')[0]+".csv"
        header = ",".join(["id", "file name", "mass", "capacity", "area", "volume", "loading",
                  "file size", "data points", "date", "device", "electrode", "comment"])+"\r\n"
        header += ",".join(["", "", "mg", "mAh/g", "cm²", "µL", "mg/cm²", "", "", "", "", "", ""])+"\r\n"
        with open(journalCSV, "w", encoding='utf-8') as fh:
            fh.write(header)
            writer = csv.writer(fh)
            writer.writerows(self.journal)
            fh.close()
        print('''Journal export written to "%s".''' % journalCSV)
    
    
    def deleteJournalRow(self):
        """delete row from journal table"""
        select_query = '''SELECT Row_ID FROM Journal_Table WHERE rowid = {0}'''.format(self.args.journalDelete)
        delete_query = '''DELETE FROM Journal_Table WHERE rowid = {0}'''.format(self.args.journalDelete)
        
        # check if row with rowid exists
        self.query(select_query)
        data = self.fetchone()
        
        if data is None:
            print("INFO: Row ID %d does not exist." % self.args.journalDelete)
        else:
            self.query(delete_query)
            print("INFO: Row ID %d deleted." % self.args.journalDelete)
            

    def setJournalID(self):
        """row ID"""
        self.query('''SELECT row_ID FROM Journal_Table''')
        self.journalID = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalID(self):
        """row ID"""
        return self.journalID
    
    
    def setJournalFileName(self):
        """file name"""
        self.query('''SELECT File_Name FROM Journal_Table''')
        self.journalFileName = list(map(itemgetter(0),self.fetchall()))
        

    def getFileName(self):
        """file name"""
        return self.journalFileName
    

    def setJournalFileSize(self):
        """file size"""
        self.query('''SELECT File_Size FROM Journal_Table''')
        self.journalFileSize = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalFileSize(self):
        """file size"""
        return self.journalFileSize
            

    def setJournalPoints(self):
        """data points"""
        self.query('''SELECT Data_Points FROM Journal_Table''')
        self.journalPoints = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalPoints(self):
        """data points"""
        return self.journalPoints
    

    def setJournalDate(self):
        """battery creation date"""
        self.query('''SELECT Start_DateTime FROM Journal_Table''')
        self.journalDate = [str(datetime.datetime.fromtimestamp(x[0])) for x in self.fetchall()]
        

    def getJournalDate(self):
        """battery creation date"""
        return self.journalDate


    def setJournalDevice(self):
        """device"""
        self.query('''SELECT Device FROM Journal_Table''')
        self.journalDevice = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalDevice(self):
        """device"""
        return self.journalDevice
    
    
    def setJournalElectrode(self):
        """working or counter electrode"""
        self.query('''SELECT Electrode FROM Journal_Table''')
        self.journalElectrode = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalElectrode(self):
        """working or counter electrode"""
        return self.journalElectrode
    
    
    def setJournalComments(self):
        """comment"""
        self.query('''SELECT Comments FROM Journal_Table''')
        self.journalComments = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalComments(self):
        """comment"""
        return self.journalComments
    
    
    def setJournalMass(self):
        """mass in mg"""
        self.query('''SELECT Mass FROM Journal_Table''')
        self.journalMass = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalMass(self):
        """mass in mg"""
        return self.journalMass
    
    
    def setJournalTheoCapacity(self):
        """theoretical capacity in mAh/g"""
        self.query('''SELECT Capacity FROM Journal_Table''')
        self.journalTheoCapacity = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalTheoCapacity(self):
        """theoretical capacity in mAh/g"""
        return self.journalTheoCapacity


    def setJournalArea(self):
        """area in cm²"""
        self.query('''SELECT Area FROM Journal_Table''')
        self.journalArea = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalArea(self):
        """area in cm²"""
        return self.journalArea


    def setJournalVolume(self):
        """volume in µL"""
        self.query('''SELECT Volume FROM Journal_Table''')
        self.journalVolume = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalVolume(self):
        """volume in µL"""
        return self.journalVolume
    
    
    def setJournalLoading(self):
        """mass loading in mg/cm²"""
        self.query('''SELECT Loading FROM Journal_Table''')
        self.journalLoading = list(map(itemgetter(0),self.fetchall()))
        

    def getJournalLoading(self):
        """mass loading in mg/cm²"""
        return self.journalLoading
    
    
   ### journal merge table methods ### 
    
    def displayMergeFiles(self):
        """display merged files for battery in journal"""
        
        # test if battery exists and is a merged file
        self.query('''SELECT Device FROM Journal_Table WHERE row_ID = {0}'''.format(self.args.journalShow))
        result = self.fetchone()
        if not result:
            sys.exit("INFO: Row ID %d does not exist." % self.args.journalShow)
        if not result[0] == "merged":
            sys.exit("INFO: Row ID %d is not a merged file." % self.args.journalShow)
            
        # display merge files table
        header = ("id", "file name", "device", "plot", "size", "date",
                  "points", "test time", "comment")
        files = [x[1:] for x in self.mergeFiles if x[0] == self.args.journalShow]
        if len(files) > 0:
            self.__printSql(files, header)
            
            
    def exportMergeFiles(self):
        """export merge files table"""
        mergeCSV = self.journalPath.split('.')[0]+".csv"
        header = ','.join(["row", "id", "file name", "device", "plot", "size", "date",
                  "points", "test time", "comment"])+"\r\n"
        if len(self.mergeFiles) > 0:
            with open(mergeCSV, "a", encoding='utf-8') as fh:
                fh.write("\r\n"+header)
                writer = csv.writer(fh)
                writer.writerows(self.mergeFiles)
                fh.close()
        

    def setMergeFiles(self):
        """fetch merged table"""
        
        self.setMergeID()
        self.setMergeFileID()
        self.setMergeFileName()
        self.setMergeDevice()
        self.setMergePlot()
        self.setMergeFileSize()
        self.setMergeDate()
        self.setMergePoints()
        self.setMergeTestTime()
        self.setMergeComment()
        
        self.mergeFiles = list(zip(self.mergeID, self.mergeFileID, self.mergeFileName, self.mergeDevice,
                                   self.mergePlot, self.mergeFileSize, self.mergeDate,
                                   self.mergePoints, self.mergeTestTime, self.mergeComment))
        
        
    def getMergeFiles(self):
        """return merged files table"""
        return self.mergeFiles
        
        
    def setMergeID(self):
        """merge id"""
        self.query('''SELECT Merge_ID FROM Merge_Table''') 
        self.mergeID = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergeID(self):
        """merge id"""
        return self.mergeID    

    
    def setMergeFileID(self):
        """file id"""
        self.query('''SELECT File_ID FROM Merge_Table''')
        self.mergeFileID = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergeFileID(self):
        """file id"""
        return self.mergeFileID
    

    def setMergeFileName(self):
        """file name"""
        self.query('''SELECT File_Name FROM Merge_Table''')
        self.mergeFileName = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergeFileName(self):
        """file id"""
        return self.mergeFileName
    

    def setMergeDevice(self):
        """device"""
        self.query('''SELECT Device FROM Merge_Table''')
        self.mergeDevice = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergeDevice(self):
        """device"""
        return self.mergeDevice
    

    def setMergePlot(self):
        """plot type"""
        self.query('''SELECT Plot_Type FROM Merge_Table''')
        self.mergePlot = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergePlot(self):
        """plot type"""
        return self.mergePlot
    
    
    def setMergeFileSize(self):
        """file size"""
        self.query('''SELECT File_Size FROM Merge_Table''')
        self.mergeFileSize = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergeFileSize(self):
        """file size"""
        return self.mergeFileSize
    

    def setMergeDate(self):
        """battery creation date"""
        self.query('''SELECT Start_DateTime FROM Merge_Table''')
        timestamp = list(map(itemgetter(0),self.fetchall()))
        self.mergeDate = [datetime.datetime.fromtimestamp(x) for x in timestamp]
        

    def getMergeDate(self):
        """battery creation date"""
        return self.mergeDate
    
    
    def setMergePoints(self):
        """data points"""
        self.query('''SELECT Data_Points FROM Merge_Table''')
        self.mergePoints = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergePoints(self):
        """data points"""
        return self.mergePoints
    
    
    def setMergeTestTime(self):
        """test time in hours"""
        self.query('''SELECT Test_Time FROM Merge_Table''')
        testtime = list(map(itemgetter(0),self.fetchall()))
        self.mergeTestTime = [round(x/3.6e3,2) for x in testtime]
        
    
    def getMergeTestTime(self):
        """test time in hours"""
        return self.mergeTestTime
    
    
    def setMergeComment(self):
        """comment"""
        self.query('''SELECT Comment FROM Merge_Table''')
        self.mergeComment = list(map(itemgetter(0),self.fetchall()))
        
    
    def getMergeComment(self):
        """comment"""
        return self.mergeComment
    
    
    ### battery methods ###
    
    def copyBatteryFiles(self):
        """copy battery file table in journal merge table"""
        listOfVars = ["Merge_ID", "File_ID", "File_Name", "Device", "Plot_Type", "File_Size", "Start_DateTime",
                      "Data_Points", "Test_Time", "Comment"]
        select_query = '''SELECT {0} FROM File_Table'''.format(','.join(listOfVars[1:]))
        self.bat.query(select_query)
        filesTable = [list(x) for x in self.bat.fetchall()]
        # fetch row id 
        self.query('''SELECT max(row_ID) FROM Journal_Table''') 
        row_id = self.fetchone()[0]
        mergeTable = [[row_id]+x for x in filesTable]
        insert_query = '''INSERT INTO Merge_Table ({0}) VALUES ({1})'''.format(
                (','.join(listOfVars)), ','.join('?'*len(listOfVars)))
        self.querymany(insert_query, mergeTable)    


    def searchBatProperties(self):
        """search plotpot-journal.dat for existing battery and set properties"""
        
        self.query('''
                   SELECT Mass,Capacity,Area,Volume,Loading FROM Journal_Table WHERE 
                   File_Name = "{0}" AND Start_DateTime = {1} AND Electrode = "{2}"'''.format(
                        self.batFileName,
                        self.batDate,
                        self.batElectrode))
        properties = self.fetchone()
        # battery not found in journal
        if properties is None:
            return False
        # fetch battery properties from journal
        else:
            self.mass = properties[0]; self.theoCapacity = properties[1]
            self.area = properties[2]; self.volume = properties[3]
            self.loading = properties[4]
            return True
            

    def updateBatProperties(self):
        """update properties in journal and battery"""
        
        # update journal
        self.query('''
            UPDATE Journal_Table 
            SET Mass = {0}, Capacity = {1}, Area = {2}, Volume = {3}, Loading = {4}
            WHERE File_Name = "{5}" AND Start_DateTime = {6} AND Electrode = "{7}"'''.format(
                    self.mass, 
                    self.theoCapacity,
                    self.area,
                    self.volume,
                    self.loading,
                    self.batFileName,
                    self.batDate,
                    self.batElectrode))
        
        # update battery
        self.bat.query('''
            UPDATE Global_Table 
            SET Mass = {0}, Capacity = {1}, Area = {2}, Volume = {3}, Loading = {4}
            WHERE rowid = 1'''.format(
                    self.mass, 
                    self.theoCapacity,
                    self.area,
                    self.volume,
                    self.loading))
        

    def insertBat(self):
        """insert battery into journal table"""
        listOfVars = ["File_Name", "File_Size", "Start_DateTime", "Data_Points", 
                      "Device", "Electrode", "Comments", "Mass", "Capacity", "Area", "Volume", "Loading"]
        insert_query = '''INSERT INTO Journal_Table ({0}) VALUES ({1})'''.format(
                (','.join(listOfVars)), ','.join('?'*len(listOfVars)))
        
        self.query(insert_query, self.battery)
        #print("INFO: Created new record in journal file.")


    def setBatProperties(self, mass = 0, theoCapacity = 0, area = 0, volume = 0, loading = 0):
        """set battery properties"""
        self.mass = mass
        self.theoCapacity = theoCapacity
        self.area = area
        self.volume = volume
        self.loading = loading
        
        
    def getBatProperties(self):
        """get battery properties"""
        return self.mass, self.theoCapacity, self.area, self.volume, self.loading        

    
    def setBattery(self):
        """battery details"""
        
        self.setBatFileName()
        self.setBatFileCount()
        self.setBatIsFullCell()        
        self.setBatFileSize()
        self.setBatDate()
        self.setBatPoints()
        self.setBatDevice()
        self.setBatComment()
        self.setBatProperties()
        
        self.battery = [self.batFileName, self.batFileSize, self.batDate, self.batPoints,
                        self.batDevice, self.batElectrode, self.batComment,
                        self.mass, self.theoCapacity, self.area, self.volume, self.loading]
        
        
    def getBattery(self):
        """return battery details"""
        return self.battery
    
    
    def setBatFileName(self):
        """set file name of battery"""
    
        if self.args.subcommand == "show":
            self.batFileName = self.args.showFileName
            
        elif self.args.subcommand == "merge":
           self.batFileName = self.globalArgs['dataFileName'] 
            
    
    def getBatFileName(self):
        """return filename of the battery"""
        return self.batFileName
        

    def setBatFileCount(self):
        """number of files used to create battery"""
        self.bat.query('''SELECT Count(*) FROM File_Table''')
        self.batFileCount = self.bat.fetchone()[0]
        
        
    def getBatFileCount(self):
        """number of files used to create battery"""
        return self.batFileCount
    
    
    def setBatIsFullCell(self):
        """test if voltage2 column is not zero"""
        self.bat.query('''SELECT Voltage2 FROM Channel_Normal_Table''')
        self.batIsFullCell = np.any(np.array(self.bat.fetchall()))
    
    
    def getBatIsFullCell(self):
        """return boolean if full or half cell"""
        return self.isFullCell
    

    def setBatDate(self):
        """battery creation date"""
        # merged file
        if self.batFileCount > 1:
            self.bat.query('''SELECT DateTime FROM Global_Table''')
        # single file
        else:
            self.bat.query('''SELECT Start_DateTime FROM File_Table''')
        self.batDate = self.bat.fetchone()[0]
        
        
    def getBatDate(self):
        """battery creation date"""
        return self.batDate
    
    
    def setBatFileSize(self):
        """raw data file size"""
        self.bat.query('''SELECT File_Size FROM Global_Table''')
        self.batFileSize = self.bat.fetchone()[0]
        
    
    def getBatFileSize(self):
        """raw data file size"""
        return self.batFileSize
    

    def setBatPoints(self):
        """data points"""
        self.bat.query('''SELECT Data_Points FROM Global_Table''')
        self.batPoints = self.bat.fetchone()[0]
        
    
    def getBatPoints(self):
        """data points"""
        return self.batPoints


    def setBatDevice(self):
        """device"""
        self.bat.query('''SELECT Device FROM Global_Table''')
        self.batDevice = self.bat.fetchone()[0]
        
    
    def getBatDevice(self):
        """device"""
        return self.batDevice

        
    def setBatComment(self):
        """comment"""
        if self.batFileCount > 1:
            self.batComment = ""
        else:
            self.bat.query('''SELECT Comment FROM File_Table''')
            self.batComment = self.bat.fetchone()[0]  
        
    
    def getBatComment(self):
        """comment"""
        return self.batComment