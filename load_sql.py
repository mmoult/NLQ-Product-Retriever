'''
Created on Oct 1, 2021

@author: Matthew Moulton
'''

import sqlite3

def commitAction(action):
    con = sqlite3.connect('product_qa.db')
    cur = con.cursor()
    
    action(cur)
    
    con.commit() # Commit changes
    con.close() # close after we are done


def buildTables(cursor):
    cursor.execute('''
        CREATE TABLE "Jewelry" (
            "ref" INTEGER NOT NULL UNIQUE,
            "category" TEXT,
            "price" INTEGER,
            "tags" TEXT,
            "description" TEXT,
            "image" TEXT,
            PRIMARY KEY("ref")
        )''')
    cursor.execute('''
        CREATE TABLE "Housing" (
            "suburb" TEXT,
            "address" TEXT NOT NULL,
            "rooms" INTEGER,
            "type" TEXT,
            "price" INTEGER NOT NULL,
            "method" TEXT,
            "distance" NUMERIC,
            "postcode" INTEGER,
            "bedrooms" INTEGER,
            "bathrooms" INTEGER,
            "cars" INTEGER,
            "landsize" INTEGER,
            "building_area" INTEGER,
            "year_built" INTEGER,
            "council" TEXT,
            "latitude" NUMERIC,
            "longitude" NUMERIC,
            "region" TEXT,
            "property_count" INTEGER,
            PRIMARY KEY("address")
        )''')


def loadTables(cursor):
    #cursor.execute('''INSERT INTO Jewelry...''')
    pass


if __name__ == '__main__':
    commitAction(buildTables)
    commitAction(loadTables)
