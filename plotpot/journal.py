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
        
        
    def setMetaInfo(self, mass = 0, capacity = 0, area = 0, volume = 0):
        """store mass and capacity in dict
           mass: active mass [mg]
           cap: theoretical capacity [mAh/g]
           area: electrode area [cm²]
           volume: volume of electrode [µL]"""

        self.massStor = {'mass': mass, 
                         'cap': capacity, 
                         'area': area, 
                         'volume': volume}
        
    
    def getMetaInfo(self):
        return self.massStor


    def getJournalPath(self):
        """create journal database in program directory or path specified with
           PLOTPOT_JOURNAL environment variable if the file does not exist
           already"""
        
        journalPath = os.environ.get('PLOTPOT_JOURNAL')
        journalFile = "plotpot-journal.dat"
        
        if journalPath:
            journalFullPath = os.path.join(journalPath, journalFile)
        else:
            journalFullPath = os.path.join(os.path.dirname(sys.argv[0]), journalPath)
            
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
            row_ID INTEGER PRIMARY KEY AUTOINCREMENT,
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
            
            
    def deleteRow(self, table, row):
        select_query = '''SELECT row_id FROM {0} WHERE rowid = {1}'''.format(table, row)
        delete_query = '''DELETE FROM {0} WHERE rowid = {1}'''.format(table, row)
        
        # check if row with rowid exists
        self.query(select_query)
        data = self.fetchone()
        
        if data is None:
            print("Row id %d does not exist in journal." % row)
        else:
            self.query(delete_query)
            print("Row id %d deleted from journal." % row)
    
    
    def printJournal(self, table):
        listOfVars = ["row_ID", "File_Name", "Mass", "Capacity", "Area", "Volume", "File_Size", "Data_Points", "Start_DateTime", "Device", "Comments"]
        select_query = '''SELECT {0} FROM {1}'''.format(','.join(listOfVars), table)
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
    
    
    def insertRow(self, table, dataSql, massStor):
        listOfVars = ["File_Name", "File_Size", "Data_Points", "Comments", "Start_DateTime", "Device", "Mass", "Capacity", "Area", "Volume"]
        insert_query = '''INSERT INTO {0} ({1}) VALUES ({2})'''.format(table,
               (','.join(listOfVars)), ','.join('?'*len(listOfVars)))
        self.query(insert_query, (dataSql[1:7] + (massStor['mass'],) + (massStor['cap'],) + (massStor['area'],) + (massStor['volume'],)))
        print("INFO: Created new record in journal file.")
    
    
    def updateColumn(self, table, column, value, dataSql):
        update_query = '''UPDATE {0} SET {1} = {2} WHERE File_Name = "{3}" AND Start_DateTime = {4}'''.format(table, column, value, dataSql[1], dataSql[5])
        self.query(update_query)

        
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

        
    def searchJournal(self, fileNameDate):
        # search arbin.cfg if battery exists in file
        listOfVars = ["rowid", "File_Name", "File_Size", "Data_Points", "Comments", "Start_DateTime", "Mass", "Capacity", "Area", "Volume"]
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
          
        if self.massStor[key] == 0:
            while True:
                try:
                    self.massStor[key] = float(input("Please give %s in [%s]: " % (attribute, unit)))
                    break
                except ValueError as e:
                    continue
        else:
            print("INFO: Found old record %s %s %s in journal." % (attribute, str(self.massStor[key]), unit))
            choice = input("Do you want to use it [Y/n]? ")
            if choice == 'n':
                while True:
                    try:
                        self.massStor[key] = float(input("Please give new %s in [%s]: " % (attribute, unit)))
                        break
                    except ValueError as e:
                        continue

    def getMass(self):       
        self.__Template("mass", "mass", "mg")


    def getCapacity(self):        
        self.__Template("cap", "capacity", "mAh/g")

    
    def getArea(self):        
        self.__Template("area", "area of the electrode", "cm²")


    def getVolume(self):        
        self.__Template("volume", "volume of electrode", "µL")