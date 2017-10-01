# -*- coding: utf-8 -*-
import os,sys
import datetime
import csv
import numpy as np
from plotpot.dbmanager import DbManager
  

class Journal(DbManager):
    """class for manipulating the journal"""
    
    def __init__(self, args):
        self.args = args
        self.journalPath = self.getJournalPath()
        super().__init__(self.journalPath)
        self.createJournal()
        self.setMetaInfo()
        

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
    
        
    def createJournal(self):
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
            Volume DOUBLE DEFAULT 0)''')
        
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
            self.query('''update Journal_Table set device = ""''')
            self.query('''UPDATE Journal_Table SET device = "Arbin BT2000" WHERE File_Name LIKE "%.res"''')
            self.query('''UPDATE Journal_Table SET device = "Gamry Interface 1000" WHERE File_Name LIKE "%.DTA"''')
            self.query('''UPDATE Journal_Table SET device = "Biologic VMP3" WHERE File_Name LIKE "%.mpt"''')
            self.query('''UPDATE Journal_Table SET device = "Ivium CompactStat" WHERE File_Name LIKE "%.idf"''')
            self.query('''UPDATE Journal_Table SET device = "Zahner IM6" WHERE File_Name LIKE "%.txt"''')
            self.query('''UPDATE Journal_Table SET device = "merged" WHERE File_Name LIKE "%.sqlite"''')
            print("Column Device created.")
            
            
    def deleteRowJournalTable(self, row):
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
            
    
    def printJournalTable(self):
        listOfVars = ["row_ID", "File_Name", "Mass", "Capacity", "Area", "Volume", "File_Size", "Data_Points", "Start_DateTime", "Device", "Comments"]
        select_query = '''SELECT {0} FROM Journal_Table'''.format(','.join(listOfVars))
        self.query(select_query)
        data = self.fetchall()
        header = ("id", "file name", "mass [mg]", "C [mAh/g]", "A [cm²]", "V [µL]", "file size", "data points", "yyyy-mm-dd hh:mm:ss", "device", "comment")
        
        # convert mass to mg, cap to mAh/g and secs since epoch into ctime
        data = [list(x) for x in data]
        for i in range(len(data)):
            data[i][8] = str(datetime.datetime.fromtimestamp(data[i][8])) # sec since epoch
             
        # output sql query
        if len(data) > 0:
            self.__printSql(data, header)
        
        print("Journal file: %s." % self.journalPath)
    
    
    def insertRowJournalTable(self, dataSql):
        """insert row into journal table"""
        listOfVars = ["File_Name", "File_Size", "Start_DateTime", "Data_Points", "Device", "Comments", "Mass", "Capacity", "Area", "Volume"]
        insert_query = '''INSERT INTO Journal_Table ({0}) VALUES ({1})'''.format((','.join(listOfVars)), ','.join('?'*len(listOfVars)))
        self.query(insert_query, dataSql)
        print("INFO: Created new record in journal file.")
        
    
    def insertRowMergeTable(self, dataSql):
        """insert row into Merge_Table"""
        listOfVars = ["Row_ID", "File_ID", "File_Name", "File_Size", "Data_Points", "Comments", "Start_DateTime", "Device"]
        insert_query = '''INSERT INTO Merge_Table ({0}) VALUES ({1})'''.format((','.join(listOfVars)), ','.join('?'*len(listOfVars)))
        self.query(insert_query, dataSql)
        
        
    def writeJournalEntry(self, fileNameDate):
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

        
    def searchJournalTable(self, fileNameDate):
        # search plotpot-journal.dat if battery exists in file
        listOfVars = ["Mass", "Capacity", "Area", "Volume"]
        select_query = '''SELECT {0} FROM Journal_Table WHERE File_Name = "{1}" AND Start_DateTime = {2}'''.format(','.join(listOfVars), fileNameDate[0], fileNameDate[1])
        self.query(select_query)
        return self.fetchone()

        
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

    
    def __Template(self, key, attribute, unit):
          
        if self.metaInfo[key] == 0:
            while True:
                try:
                    self.metaInfo[key] = float(input("Please give %s in [%s]: " % (attribute, unit)))
                    break
                except ValueError as e:
                    continue
        else:
            print("INFO: Found old record %s %s %s in journal." % (attribute, str(self.metaInfo[key]), unit))
            choice = input("Do you want to use it [Y/n]? ")
            if choice == 'n':
                while True:
                    try:
                        self.metaInfo[key] = float(input("Please give new %s in [%s]: " % (attribute, unit)))
                        break
                    except ValueError as e:
                        continue

    def setMass(self):       
        self.__Template("mass", "mass", "mg")


    def setCapacity(self):        
        self.__Template("cap", "capacity", "mAh/g")

    
    def setArea(self):        
        self.__Template("area", "area of the electrode", "cm²")


    def setVolume(self):        
        self.__Template("volume", "volume of electrode", "µL")
        
    
    def setMetaInfo(self, mass = 0, capacity = 0, area = 0, volume = 0):
        """store mass and capacity in dict
           mass: active mass [mg]
           cap: theoretical capacity [mAh/g]
           area: electrode area [cm²]
           volume: volume of electrode [µL]"""

        self.metaInfo = {'mass': mass, 
                    'cap': capacity, 
                    'area': area, 
                    'volume': volume}
    
    
    def getMetaInfo(self):
        """return dict with meta info"""
        return self.metaInfo
    
    
    def tupleMetaInfo(self):
        """return a tuple with meta info values"""
        return (self.metaInfo['mass'], self.metaInfo['cap'], self.metaInfo['area'], self.metaInfo['volume'])
    
    
    def updateMetaInfo(self, fileNameDate):
        """update meta info of journal entry"""
        update_query = '''
            UPDATE Journal_Table 
            SET Mass = {0}, Capacity = {1}, Area = {2}, Volume = {3}
            WHERE File_Name = "{4}" AND Start_DateTime = {5}'''.format(
                    self.metaInfo['mass'], 
                    self.metaInfo['cap'],
                    self.metaInfo['area'],
                    self.metaInfo['volume'],
                    fileNameDate[0],
                    fileNameDate[1])
            
        self.query(update_query)
        

    def askMetaInfo(self, plots):
        """ask questions and update meta info"""
        if any([x in [1,4,5,11] for x in plots]):
            self.setMass()
        if 10 in plots:
            self.setCapacity()
        if any([x in [12] for x in plots]):
            self.setArea()
        if 6 in plots:
            self.setVolume()