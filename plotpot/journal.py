# -*- coding: utf-8 -*-
import os,sys
import datetime
import csv
import numpy as np
from plotpot.dbmanager import DbManager
  

class Journal(DbManager):
    """class for manipulating the journal"""
    
    def __init__(self, args, showArgs=None, electrode=None):
        self.args = args
        self.journalPath = self.getJournalPath()
        super().__init__(self.journalPath)
        self.createSchema()
        
        # battery processing
        if (showArgs and electrode) is not None:
            self.showArgs = showArgs
            self.bat = DbManager(showArgs['dataFile'])
            self.setBatFileCount()
            self.setBatDate()
            self.setBatProperties()
            
            # set electrode type
            if electrode is "we":
                self.electrode = "working"
            elif electrode is "ce":
                self.electrode = "counter"
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
        

    ### journal methods ###

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
            fh = open(journalFullPath, "r")
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
            
    
    def display(self):
        listOfVars = ["row_ID", "File_Name", "Mass", "Capacity", "Area", "Volume",
                      "File_Size", "Data_Points", "Start_DateTime", "Device", "Electrode", "Comments"]
        select_query = '''SELECT {0} FROM Journal_Table'''.format(','.join(listOfVars))
        self.query(select_query)
        data = self.fetchall()
        
        # convert secs since epoch into ctime
        data = [list(x) for x in data]
        for i in range(len(data)):
            data[i][8] = str(datetime.datetime.fromtimestamp(data[i][8])) # sec since epoch
             
        # output sql query
        header = ("id", "file name", "mass [mg]", "C [mAh/g]", "A [cm²]", "V [µL]",
                  "file size", "data points", "yyyy-mm-dd hh:mm:ss", "device", "electrode", "comment")
        if len(data) > 0:
            self.__printSql(data, header)
        print("Journal file: %s." % self.journalPath)
        
    
    def export(self):
        """export journal to csv file"""
        pass
    
    
    def deleteRow(self, row):
        """delete row from journal table"""
        select_query = '''SELECT Row_ID FROM Journal_Table WHERE rowid = {0}'''.format(row)
        delete_query = '''DELETE FROM Journal_Table WHERE rowid = {0}'''.format(row)
        
        # check if row with rowid exists
        self.query(select_query)
        data = self.fetchone()
        
        if data is None:
            rc = "Row id %d does not exist in journal." % row
        else:
            self.query(delete_query)
            rc = "Row id %d deleted from journal." % row
            
        return rc
    
    
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


    def setBatProperties(self, mass = 0, theoCapacity = 0, area = 0, volume = 0):
        """set battery properties"""
        self.mass = mass
        self.theoCapacity = theoCapacity
        self.area = area
        self.volume = volume
        
        
    def getBatProperties(self):
        """get battery properties"""
        return self.mass, self.theoCapacity, self.area, self.volume    


    def searchBatProperties(self):
        """search plotpot-journal.dat for existing battery and set properties"""
        
        self.query('''
                   SELECT Mass,Capacity,Area,Volume FROM Journal_Table WHERE 
                   File_Name = "{0}" AND Start_DateTime = {1} AND Electrode = "{2}"'''.format(
                        self.args.filename,
                        self.batDate,
                        self.electrode))
        properties = self.fetchone()
        if properties is None:
            self.mass = 0; self.theoCapacity = 0; self.area = 0; self.volume = 0
        else:
            self.mass = properties[0]; self.theoCapacity = properties[1]
            self.area = properties[2]; self.volume = properties[3]
    

    def updateBatProperties(self):
        """update properties in journal and battery"""
        
        # update journal
        self.query('''
            UPDATE Journal_Table 
            SET Mass = {0}, Capacity = {1}, Area = {2}, Volume = {3}
            WHERE File_Name = "{4}" AND Start_DateTime = {5} AND Electrode = "{6}"'''.format(
                    self.mass, 
                    self.theoCapacity,
                    self.area,
                    self.volume,
                    self.args.filename,
                    self.batDate,
                    self.electrode))
        
        # update battery
        self.bat.query('''
            UPDATE Global_Table 
            SET Mass = {0}, Capacity = {1}, Area = {2}, Volume = {3}
            WHERE rowid = 1'''.format(
                    self.mass, 
                    self.theoCapacity,
                    self.area,
                    self.volume))
        

    def insertBat(self):
        """insert battery into journal table"""
        listOfVars = ["File_Name", "File_Size", "Start_DateTime", "Data_Points", "Device", "Comments", "Mass", "Capacity", "Area", "Volume"]
        insert_query = '''INSERT INTO Journal_Table ({0}) VALUES ({1})'''.format((','.join(listOfVars)), ','.join('?'*len(listOfVars)))
        self.query(insert_query, dataSql)
        print("INFO: Created new record in journal file.")
        
        
    def exportBat(self, fileNameDate):
        listOfVars = ["File_Name", "Mass", "Capacity", "Area", "Volume", "File_Size", "Data_Points", "Start_DateTime", "Comments"]
        select_query = '''SELECT {0} FROM Journal_Table WHERE File_Name = ? AND Start_DateTime = ?'''.format(','.join(listOfVars))
        self.query(select_query, fileNameDate)
        dataSql = self.fetchone()
        dataSql = list(dataSql)
        dataSql[7] = str(datetime.datetime.fromtimestamp(dataSql[7])) # sec since epoch
        
        fh = open(self.args.filename.split('.')[0]+'_journal.csv', 'w')
        header = "%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                "file_name", "mass", 
                "capacity", "area", "volume", "file_size", 
                "data_points", "start_datetime", 
                "comments")
        units = ",%s,%s,%s,%s\n" % ("mg", "mAh/g", "cm²", "µL")
        
        fh.write(header)
        fh.write(units)
        writer = csv.writer(fh)
        writer.writerow(dataSql)
        fh.close()