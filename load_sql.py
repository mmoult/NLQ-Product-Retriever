'''
Created on Oct 1, 2021

@author: Matthew Moulton
'''

import sqlite3
import string


class Table(object):
    def __init__(self, name:string, primKey:int, *args):
        self.name = name
        self.primKey = primKey
        self.dat = args


jewelry = Table("Jewelry", 0,
    ["ref", "TEXT NOT NULL UNIQUE"],
    ["category", "TEXT"],
    ["title", "TEXT"],
    ["price", "INTEGER"],
    ["tags", "TEXT"],
    ["description", "TEXT"],
    ["image", "TEXT"]
)
housing = Table("Housing", None,
    ["suburb", "TEXT"],
    ["address", "TEXT NOT NULL"],
    ["rooms", "INTEGER"],
    ["type", "TEXT"],
    ["price", "INTEGER NOT NULL"],
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
        cmd += '"' + attr[0] + '" ' + attr[1] + ','
    if not table.primKey is None:
        cmd += ('PRIMARY KEY("' + table.dat[table.primKey][0] + '")')
    else:
        cmd = cmd[0:len(cmd)-1] #get rid of the last comma
    cmd += ')'
    #print(cmd)
    return cmd


def buildTables(cursor):
    cursor.execute(buildCreate(jewelry))
    cursor.execute(buildCreate(housing))

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
    file = open(loc)
    title = False   
    sumLine = '' # this is what we will use when an entry spans several lines
    unfinished = False
    lineNo = -1
    for line in file:
        lineNo += 1
        if not title:
            title = True
            continue
        
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
        except sqlite3.Error:
            import traceback
            traceback.print_exc()
            print("... when trying to execute " + sqlString)
            print("... calculated from line " + str(lineNo))
            print("... which is: " + line)
    file.close()


def loadTables(cursor):
    loadTable(cursor, 'Datasets/cartier_catalog.csv', jewelry)
    loadTable(cursor, 'Datasets/melb_data.csv', housing)

##################################################################################### Main Entry

if __name__ == '__main__':
    commitAction(buildTables)
    commitAction(loadTables)
    pass
