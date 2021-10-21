'''
Created on Oct 1, 2021

@author: Matthew Moulton
'''

import sqlite3
import string


class Table(object):
    def __init__(self, name:string, primKey:int, idxCol:[int], *args):
        '''
        Creates a new table that can be used with SQLite.
        @param name: the name that the table should have internally in SQL
        @param primKey: the column that should be used as the primary key of the table
        @param idxCol: the column(s) that should be used in creating the index
        @param args: the data of the table attributes. Should be in form ["attributeName", "attributeType"], ...
        '''
        self.name = name
        self.primKey = primKey
        self.idxCol = idxCol
        self.dat = args


motorcycles = Table("Motorcycles", None, [0],
    ["name", "TEXT"],
    ["price", "NUMERIC"],
    ["year", "INTEGER"],
    ["seller", "TEXT"],
    ["owner", "TEXT"],
    ["mileage", "NUMERIC"],
    ["show_price", "INTEGER"]
)
jewelry = Table("Jewelry", 0, [1],
    ["ref", "TEXT NOT NULL UNIQUE"],
    ["category", "TEXT"],
    ["title", "TEXT"],
    ["price", "NUMERIC"],
    ["tags", "TEXT"],
    ["description", "TEXT"],
    ["image", "TEXT"]
)
jobs = Table("Jobs", 0, [1],
    ["id", "INTEGER NOT NULL UNIQUE"],
    ["title", "TEXT NOT NULL"],
    ["salary", "TEXT"], # this may be problematic since the salary is in a string bucket
    ["description", "TEXT"],
    ["rating", "NUMERIC"], # [0,5], -1
    ["company", "TEXT"],
    ["location", "TEXT"],
    ["hq", "TEXT"],
    ["size", "TEXT"],
    ["founded", "INTEGER"], # year
    ["owner", "TEXT"], # Company, Government
    ["industry", "TEXT"],
    ["sector", "TEXT"],
    ["revenue", "TEXT"],
    ["competitors", "TEXT"],
    ["easy_apply", "TEXT"] # TRUE, FALSE, -1
)
furniture = Table("Furniture", 0, [2],
    ["id", "INTEGER NOT NULL UNIQUE"],
    ["name", "TEXT"],
    ["category", "TEXT"],
    ["price", "NUMERIC NOT NULL"],
    ["old_price", "TEXT"],
    ["sellable", "TEXT"], # TRUE, FALSE
    ["link", "TEXT"],
    ["other_colors", "TEXT"], # Yes, No
    ["description", "TEXT"],
    ["designer", "TEXT"],
    ["depth", "INTEGER"],
    ["height", "INTEGER"],
    ["width", "INTEGER"]
)
housing = Table("Housing", None, [3],
    ["suburb", "TEXT"],
    ["address", "TEXT NOT NULL"],
    ["rooms", "INTEGER"],
    ["type", "TEXT"],
    ["price", "NUMERIC NOT NULL"],
    ["method", "TEXT"],
    ["date", "TEXT"],
    ["distance", "NUMERIC"],
    ["postcode", "INTEGER"],
    ["bedrooms", "INTEGER"],
    ["bathrooms", "INTEGER"],
    ["cars", "INTEGER"],
    ["landsize", "INTEGER"],
    ["building_area", "INTEGER"],
    ["year_built", "INTEGER"],
    ["council", "TEXT"],
    ["latitude", "NUMERIC"],
    ["longitude", "NUMERIC"],
    ["region", "TEXT"],
    ["property_count", "INTEGER"]
)
cars = Table("Cars", 0, [4, 5], # both the make and the model are type 1
    ["id", "INTEGER NOT NULL UNIQUE"],
    ["region", "TEXT NOT NULL"],
    ["price", "NUMERIC NOT NULL"],
    ["year", "INTEGER"],
    ["manufacturer", "TEXT"],
    ["model", "TEXT"],
    ["condition", "TEXT"],
    ["cylinders", "TEXT"], # 4 cylinders, 6 cylinders, 8 cylinders, 10 cylinders, other
    ["fuel", "TEXT"], # gas, diesel, hybrid, electric
    ["odometer", "INTEGER"],
    ["title_status", "TEXT"], # clean, rebuilt, salvage
    ["transmission", "TEXT"], # manual, automatic
    ["drive", "TEXT"],
    ["size", "TEXT"],
    ["type", "TEXT"],
    ["paint_color", "TEXT"],
    ["state", "TEXT"]
)


def commitAction(action):
    con = sqlite3.connect('product_qa.db')
    cur = con.cursor()
    
    action(cur)
    
    con.commit() # Commit changes
    con.close() # close after we are done

##################################################################################### Create tables

def buildCreate(table:Table):
    cmd = 'CREATE TABLE "' + table.name + '" ('
    for attr in table.dat:
        cmd += '"' + attr[0] + '" ' + attr[1] + ', '
    
    if not table.primKey is None:
        cmd += ('PRIMARY KEY("' + table.dat[table.primKey][0] + '")')
        cmd += ') WITHOUT ROWID;'
    else:
        cmd = cmd[0:len(cmd)-2] #get rid of the last comma
        cmd += ');'
    
    #print(cmd)
    return cmd


def buildTables(cursor):
    dropCommand = 'DROP TABLE IF EXISTS '
    allTables = [motorcycles, jewelry, jobs, furniture, housing, cars]
    for table in allTables:
        cursor.execute(dropCommand + table.name)
        cursor.execute(buildCreate(table))
        # build the indexes (if any)
        if table.idxCol is not None:
            for idxC in table.idxCol: # for each of the specified indexes
                iOn = table.dat[idxC][0]
                cmd = 'CREATE INDEX idx_' + table.name + '_' + iOn + ' ON ' + table.name + '(' + iOn + ');'
                print(cmd)
                cursor.execute(cmd)

##################################################################################### Populate tables

def splitWithStrings(line: string) -> [string]:
    comps = []
    start = 0
    
    while start < len(line):
        nextDelim = line.find(',', start)
        nextStrng = line.find('"', start)
        while nextStrng > 1 and line[nextStrng - 1] == '\\':
            nextStrng = line.find('"', nextStrng+1) # this instance is escaped, so find the next
        # Verify that neither are -1, which throws off the less than comparison
        if nextDelim == -1:
            nextDelim = len(line)
        if nextStrng == -1:
            nextStrng = len(line)
        
        if nextDelim < nextStrng:
            comps.append(line[start:nextDelim])
            start = nextDelim + 1
        elif nextStrng < nextDelim:
            # find the next " that ends the string
            start = nextStrng + 1
            nextStrng = line.find('"', start)
            while nextStrng > 1 and line[nextStrng - 1] == '\\':
                nextStrng = line.find('"', nextStrng+1)
            comps.append(line[start:nextStrng])
            # now move 'start' to after the next comma (if there is one)
            ncom = line.find(',', nextStrng)
            if ncom == -1: # no more to process
                break
            start = ncom + 1
        else: # both are -1
            # In this case, there is one more non-string field (since the list cannot end on a comma)
            comps.append(line[start:(len(line)-1)])
            break
    return comps


def unfinishedString(line:string) -> bool:
    start = 0
    unfinished = False
    while True:
        try:
            start = line.index('"', start)
            # if the index immediately before is a \, then this has been escaped
            if start > 1 and line[start - 1] != '\\':
                unfinished = not unfinished
            start += 1 # since the start arg in index is inclusive
        except ValueError:
            # Occurs when no more ". Stop looking.
            break
    return unfinished


def loadTable(cursor, loc:string, table:Table):
    file = open(loc, encoding='utf-8')
    title = False   
    sumLine = '' # this is what we will use when an entry spans several lines
    unfinished = False
    entry = 0
    lineNo = 1
    for line in file:
        if not title:
            title = True
            continue
        lineNo += 1
        # We are going to trim the file to only load the first 800 entries
        if entry > 800:
            break
        
        sumLine += line
        # If there are an even number of non-escaped ", then we know that the line is done
        unfinished = unfinishedString(line) ^ unfinished
        if unfinished:
            continue # get the next line to continue what we have
        
        # If we are here, the line is considered finished
        comps = splitWithStrings(sumLine)
        sumLine = '' # reset the running line for next time
        sqlString = 'INSERT INTO ' + table.name + ' VALUES('
        first = True
        for i in range(len(comps)):
            comp = comps[i]
            if first:
                first = False
            else:
                sqlString += ', '
            # We want to see if this field should be a string. If so, it should have string chars surrounding
            if "TEXT" in table.dat[i][1]:
                if len(comp) == 0:
                    comp = '""' # default string value is nothing
                elif comp[0] != '"' or comp[-1] != '"':
                    comp = '"' + comp + '"'
            elif len(comp) == 0 and ("INTEGER" in table.dat[i][1] or "NUMBER" in table.dat[i][1]):
                comp = '-1' # default number value is -1
            sqlString += comp
        sqlString += ')'
        
        #print(sqlString)
        try:
            cursor.execute(sqlString)
            entry += 1
        except sqlite3.Error:
            import traceback
            traceback.print_exc()
            print("... when trying to execute " + sqlString)
            print("... calculated from line " + str(lineNo))
            print("... which is: " + line)
    file.close()


def loadTables(cursor):
    dataRoot = 'Datasets/'
    loadTable(cursor, dataRoot+'BIKE DETAILS.csv', motorcycles)
    loadTable(cursor, dataRoot+'cartier_catalog.csv', jewelry)
    loadTable(cursor, dataRoot+'DataScientist.csv', jobs)
    loadTable(cursor, dataRoot+'IKEA_Furniture.csv', furniture)
    loadTable(cursor, dataRoot+'melb_data.csv', housing)
    loadTable(cursor, dataRoot+'vehicles4.csv', cars)


def rectifyData(cursor):
    # There are some things about the dataset that we are going to change to make it easier to use
    # We need to:
    #    change from Swedish crowns to USD on the furniture file
    sekToUsd = str(0.12)
    cursor.execute("UPDATE " + furniture.name + " SET price = price * " + sekToUsd + ";")
    #    change from Australian dollars to USD on the housing file
    audToUsd = str(0.74)
    cursor.execute("UPDATE " + housing.name + " SET price = price * " + audToUsd + ";")
    #    change from the single character types to the full name on the housing file
    cursor.execute('UPDATE ' + housing.name + ' SET type = "house" WHERE type = "h";')
    cursor.execute('UPDATE ' + housing.name + ' SET type = "unit" WHERE type = "u";')
    cursor.execute('UPDATE ' + housing.name + ' SET type = "townhouse" WHERE type = "t";')
    #    change from m^2 to ft^2 in the housing file
    sqmToSqft = str(10.76391)
    cursor.execute("UPDATE " + housing.name + " SET landsize = landsize * " + sqmToSqft + " WHERE landsize <> -1;")
    cursor.execute("UPDATE " + housing.name + " SET building_area = building_area * " + sqmToSqft + " WHERE building_area <> -1;")
    #    change from km driven to miles driven in the motorcycles file
    kmToMi = str(0.6213712)
    cursor.execute("UPDATE " + motorcycles.name + " SET mileage = mileage * " + kmToMi + ";")
    #    change the price from Indian rupees to USD in the motorcycle file
    indianRupeeToUsd = str(0.01)
    cursor.execute("UPDATE " + motorcycles.name + " SET price = price * " + indianRupeeToUsd + ";")


##################################################################################### Main Entry

if __name__ == '__main__':
    commitAction(buildTables)
    commitAction(loadTables)
    commitAction(rectifyData)
    pass
