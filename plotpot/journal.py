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
    
    def __init__(self, args, showArgs=None, electrode=None):
        self.args = args
        self.journalPath = self.getJournalPath()
        super().__init__(self.journalPath)
        self.createSchema()
        self.setData()
        
        # battery processing
        if (showArgs and electrode) is not None:
            self.showArgs = showArgs
            self.bat = DbManager(showArgs['dataFile'])
            self.setBatFileCount()
            self.setBatDate()
            self.setBatPoints()
            self.setBatFileSize()
            self.setBatDevice()
            self.setBatComment()
            self.setBatProperties()
            
            # set electrode type
            if electrode is "we":
                self.batElectrode = "working"
            elif electrode is "ce":
                self.batElectrode = "counter"
            else:
                sys.exit("ERROR: Unknown electrode %s" % electrode)
            
            
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

    def getJournalPath(self):
        """create journal database in program directory or path specified with
           PLOTPOT_JOURNAL environment variable if the file does not exist
           already"""
        
        journalPath = os.environ.get('PLOTPOT_JOURNAL')
        journalFile = "plotpot-journal.dat"
        
        if journalPath:
            journalFullPath = os.path.join(journalPath, journalFile)
        else:
            home = os.getenv('USERPROFILE') or os.getenv('HOME')
            journalFullPath = os.path.join(home, journalFile)
            
        # check if journal file exists
        try:
            open(journalFullPath, "r")
        except IOError as e:
            print(e)
            create = input("Do you want to create a new journal file (Y,n)? ")
            if create == 'n':
                sys.exit()
                
        return journalFullPath
    
        
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
            Row_ID INTEGER,
            File_ID INTEGER,
            File_Name TEXT,
            Device TEXT,
            File_Size INTEGER,
            Start_DateTime INTEGER,
            Data_Points INTEGER,
            Comments TEXT)''')
       
        
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
            
            
    def display(self):
        """display journal table on screen"""
        header = ("id", "file name", "m [mg]", "C [mAh/g]", "A [cm²]", "V [µL]", "L [mg/cm²]",
                  "file size", "data points", "yyyy-mm-dd hh:mm:ss", "device", "electrode", "comment")
        if len(self.data) > 0:
            self.__printSql(self.data, header)
        print('''Journal file: "%s".''' % self.journalPath)
        
        
    def export(self):
        """export journal table to csv file"""
        journalCSV = self.journalPath[:-3]+"csv"
        header = ",".join(["id", "file name", "mass", "capacity", "area", "volume", "loading",
                  "file size", "data points", "date", "device", "electrode", "comment"])+"\n"
        header += ",".join(["", "", "mg", "mAh/g", "cm²", "µL", "mg/cm²", "", "", "", "", "", ""])+"\n"
        with open(journalCSV, "w") as fh:
            writer = csv.writer(fh)
            fh.write(header)
            writer.writerows(self.data)
            fh.close()
        print('''Journal export written to "%s".''' % journalCSV)
        
    
    def deleteRow(self, row):
        """delete row from journal table"""
        select_query = '''SELECT Row_ID FROM Journal_Table WHERE rowid = {0}'''.format(row)
        delete_query = '''DELETE FROM Journal_Table WHERE rowid = {0}'''.format(row)
        
        # check if row with rowid exists
        self.query(select_query)
        data = self.fetchone()
        
        if data is None:
            print("INFO: Row ID %d does not exist." % row)
        else:
            self.query(delete_query)
            print("INFO: Row ID %d deleted." % row)
            
    
    ### journal methods ###

    def setData(self):
        """fetch journal table"""
        
        try:
            self.setID()
            self.setFileName()
            self.setMass()
            self.setTheoCapacity()
            self.setArea()
            self.setVolume()
            self.setLoading()
            self.setFileSize()
            self.setPoints()
            self.setDate()
            self.setDevice()
            self.setElectrode()
            self.setComments()
            
        except sqlite3.OperationalError as e:
            self.upgradeSchema()
            sys.exit("INFO: Upgraded journal database schema.")
            
        self.data = zip(self.id, self.fileName, self.mass, self.theoCapacity,
                        self.area, self.volume, self.loading, self.fileSize,
                        self.points, self.date, self.device, self.electrode,
                        self.comments)
            
            
    def getData(self):
        """fetch journal table"""
        return self.data
    
    
    def setID(self):
        """row ID"""
        self.query('''SELECT row_ID FROM Journal_Table''')
        self.id = list(map(itemgetter(0),self.fetchall()))
        

    def getID(self):
        """row ID"""
        return self.id
    
    
    def setFileName(self):
        """file name"""
        self.query('''SELECT File_Name FROM Journal_Table''')
        self.fileName = list(map(itemgetter(0),self.fetchall()))
        

    def getFileName(self):
        """file name"""
        return self.fileName
    

    def setFileSize(self):
        """file size"""
        self.query('''SELECT File_Size FROM Journal_Table''')
        self.fileSize = list(map(itemgetter(0),self.fetchall()))
        

    def getFileSize(self):
        """file size"""
        return self.fileSize
            

    def setPoints(self):
        """data points"""
        self.query('''SELECT Data_Points FROM Journal_Table''')
        self.points = list(map(itemgetter(0),self.fetchall()))
        

    def getPoints(self):
        """data points"""
        return self.points
    

    def setDate(self):
        """battery creation date"""
        self.query('''SELECT Start_DateTime FROM Journal_Table''')
        self.date = [str(datetime.datetime.fromtimestamp(x[0])) for x in self.fetchall()]
        

    def getDate(self):
        """battery creation date"""
        return self.date


    def setDevice(self):
        """device"""
        self.query('''SELECT Device FROM Journal_Table''')
        self.device = list(map(itemgetter(0),self.fetchall()))
        

    def getDevice(self):
        """device"""
        return self.device
    
    
    def setElectrode(self):
        """working or counter electrode"""
        self.query('''SELECT Electrode FROM Journal_Table''')
        self.electrode = list(map(itemgetter(0),self.fetchall()))
        

    def getElectrode(self):
        """working or counter electrode"""
        return self.electrode
    
    
    def setComments(self):
        """comment"""
        self.query('''SELECT Comments FROM Journal_Table''')
        self.comments = list(map(itemgetter(0),self.fetchall()))
        

    def getComments(self):
        """comment"""
        return self.comments
    
    
    def setMass(self):
        """mass in mg"""
        self.query('''SELECT Mass FROM Journal_Table''')
        self.mass = list(map(itemgetter(0),self.fetchall()))
        

    def getMass(self):
        """mass in mg"""
        return self.mass
    
    
    def setTheoCapacity(self):
        """theoretical capacity in mAh/g"""
        self.query('''SELECT Capacity FROM Journal_Table''')
        self.theoCapacity = list(map(itemgetter(0),self.fetchall()))
        

    def getTheoCapacity(self):
        """theoretical capacity in mAh/g"""
        return self.theoCapacity


    def setArea(self):
        """area in cm²"""
        self.query('''SELECT Area FROM Journal_Table''')
        self.area = list(map(itemgetter(0),self.fetchall()))
        

    def getArea(self):
        """area in cm²"""
        return self.area


    def setVolume(self):
        """volume in µL"""
        self.query('''SELECT Volume FROM Journal_Table''')
        self.volume = list(map(itemgetter(0),self.fetchall()))
        

    def getVolume(self):
        """volume in µL"""
        return self.volume
    
    
    def setLoading(self):
        """mass loading in mg/cm²"""
        self.query('''SELECT Loading FROM Journal_Table''')
        self.loading = list(map(itemgetter(0),self.fetchall()))
        

    def getLoading(self):
        """mass loading in mg/cm²"""
        return self.loading
        
    
    ### battery methods ###

    def setBatFileCount(self):
        """number of files used to create battery"""
        self.bat.query('''SELECT Count(*) FROM File_Table''')
        self.batFileCount = self.bat.fetchone()[0]
        
        
    def getBatFileCount(self):
        """number of files used to create battery"""
        return self.batFileCount


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


    def searchBatProperties(self):
        """search plotpot-journal.dat for existing battery and set properties"""
        
        self.query('''
                   SELECT Mass,Capacity,Area,Volume,Loading FROM Journal_Table WHERE 
                   File_Name = "{0}" AND Start_DateTime = {1} AND Electrode = "{2}"'''.format(
                        self.args.filename,
                        self.batDate,
                        self.batElectrode))
        properties = self.fetchone()
        if properties is None:
            self.mass = 0; self.theoCapacity = 0; self.area = 0; self.volume = 0; self.loading = 0
            self.insertBat()
        else:
            self.mass = properties[0]; self.theoCapacity = properties[1]
            self.area = properties[2]; self.volume = properties[3]
            self.loading = properties[4]
    

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
                    self.args.filename,
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
        self.query(insert_query, (self.args.filename, self.batFileSize, self.batDate, self.batPoints,
                                  self.batDevice, self.batElectrode, self.batComment,
                                  self.mass, self.theoCapacity, self.area, self.volume, self.loading))
        #print("INFO: Created new record in journal file.")