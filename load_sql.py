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
    ["price", "INTEGER"],
    ["tags", "TEXT"],
    ["description", "TEXT"],
    ["image", "TEXT"]
)
housing = Table("Housing", 1,
    ["suburb", "TEXT"],
    ["address", "TEXT NOT NULL"],
    ["rooms", "INTEGER"],
    ["type", "TEXT"],
    ["price", "INTEGER NOT NULL"],
    ["method", "TEXT"],
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


def buildCreate(table:Table):
    cmd = 'CREATE TABLE "' + table.name + '" ('
    for attr in table.dat:
        cmd += '"' + attr[0] + '" ' + attr[1] + ','
    cmd += ('PRIMARY KEY("' + table.dat[table.primKey][0] + '")')
    cmd += ')'
    return cmd


def buildTables(cursor):
    cursor.execute(buildCreate(jewelry))
    cursor.execute(buildCreate(housing))


def splitWithStrings(line: string) -> [string]:
    
    pass

def unfinishedString(line:string) -> bool:
    start = 0
    unfinished = False
    while True:
        try:
            start = line.index('"', start)
            # if the index immediately before is a \, then this has been escaped
            if start > 1 and line[start - 1] != '\\':
                unfinished = not unfinished
        except ValueError:
            # Occurs when no more ". Stop looking.
            break
    return unfinished


def loadTables(cursor, table:Table):
    jewelry = open('Datasets/Product-QA/Datasets/cartier_catalog.csv')
    title = False   
    sumLine = '' # this is what we will use when an entry spans several lines
    unfinished = False
    for line in jewelry:
        if not title:
            title = True
            continue
        
        sumLine += line
        # If there are an even number of non-escaped ", then we know that the line is done
        unfinished = unfinishedString(line) ^ unfinished
        if unfinished:
            continue # get the next line to continue what we have
        
        # If we are here, the line is considered finished
        comps = splitWithStrings(line)
        cursor.execute('''INSERT INTO Jewelry...''')   
    jewelry.close()
    pass


if __name__ == '__main__':
    commitAction(buildTables)
    #commitAction(loadTables)
