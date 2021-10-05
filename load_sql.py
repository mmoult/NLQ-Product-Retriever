'''
Created on Oct 1, 2021

@author: Matthew Moulton
'''

import sqlite3

jewelry = [
    ["ref", "TEXT NOT NULL UNIQUE"],
    ["category", "TEXT"],
    ["price", "INTEGER"],
    ["tags", "TEXT"],
    ["description", "TEXT"],
    ["image", "TEXT"],
]
housing = [
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
]

def commitAction(action):
    con = sqlite3.connect('product_qa.db')
    cur = con.cursor()
    
    action(cur)
    
    con.commit() # Commit changes
    con.close() # close after we are done


def buildCreate(name, struct, primaryKey):
    cmd = 'CREATE TABLE "' + name + '" ('
    for attr in struct:
        cmd += '"' + attr[0] + '" ' + attr[1] + ','
    cmd += ('PRIMARY KEY("' + primaryKey + '")')
    cmd += ')'
    return cmd


def buildTables(cursor):
    cursor.execute(buildCreate("Jewelry", jewelry, jewelry[0][0]))
    cursor.execute(buildCreate("Housing", housing, housing[1][0]))


def loadTables(cursor):
    jewelry = open('Datasets/Product-QA/Datasets/cartier_catalog.csv')
    title = False
    for line in jewelry:
        if not title:
            title = True
            continue
        comps = line.split(',')
        cursor.execute('''INSERT INTO Jewelry...''')   
    jewelry.close()
    pass


if __name__ == '__main__':
    commitAction(buildTables)
    #commitAction(loadTables)
