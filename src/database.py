import string
from src.domains import Domain

class Table(object):
    def __init__(self, name:Domain, primKey:int, idxCol:[int], *args):
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


motorcycles = Table(Domain.MOTORCYCLE, None, [0],
    [["name"], "TEXT"],
    [["price"], "NUMERIC", ['$']],
    [["year"], "INTEGER", ['year', 'yr', 'yrs']],
    [["seller"], "TEXT"],
    [["owner"], "INTEGER", ['owner']],
    [["mileage"], "NUMERIC", ['mile', 'miles', 'mi']],
    [["show_price"], "INTEGER"]
)
jewelry = Table(Domain.JEWELRY, 0, [1, 2],
    [["ref"], "TEXT NOT NULL UNIQUE"],
    [["category"], "TEXT"],
    [["title"], "TEXT"],
    [["price"], "NUMERIC", ['$']],
    [["tags"], "TEXT"],
    [["description"], "TEXT"],
    [["image"], "TEXT"]
)
jobs = Table(Domain.JOB, 0, [1],
    [["id"], "INTEGER NOT NULL UNIQUE"],
    [["title"], "TEXT NOT NULL"],
    [["description"], "TEXT"],
    [["rating"], "NUMERIC"], # [0,5], -1
    [["company"], "TEXT"],
    [["location"], "TEXT"],
    [["hq"], "TEXT"],
    [["founded"], "INTEGER", ['year', 'yr', 'yrs']], # year
    [["owner"], "TEXT"], # Company, Government
    [["industry"], "TEXT"],
    [["sector"], "TEXT"],
    [["competitors"], "TEXT"],
    [["easy_apply"], "TEXT"], # TRUE, FALSE, -1
    [["salary_min"], "INTEGER", ['$'], 'salary_max'],
    [["salary_max"], "INTEGER", ['$'], 'salary_min'],
    [["size_min"], "INTEGER", ['people'], 'size_max'],
    [["size_max"], "INTEGER", ['people'], 'size_min'],
    [["revenue_min"], "INTEGER", ['$'], 'revenue_max'],
    [["revenue_max"], "INTEGER", ['$'], 'revenue_min']
)
furniture = Table(Domain.FURNITURE, 0, [2],
    [["id"], "INTEGER NOT NULL UNIQUE"],
    [["name"], "TEXT"],
    [["category"], "TEXT"],
    [["price"], "NUMERIC NOT NULL", ['$']],
    [["old_price"], "TEXT"],
    [["sellable"], "TEXT"], # TRUE, FALSE
    [["link"], "TEXT"],
    [["other_colors"], "TEXT"], # Yes, No
    [["description"], "TEXT"],
    [["designer"], "TEXT"],
    [["depth"], "NUMERIC", ['inch', 'inches', 'in']],
    [["height"], "NUMERIC", ['inch', 'inches', 'in']],
    [["width"], "NUMERIC", ['inch', 'inches', 'in']]
)
housing = Table(Domain.HOUSING, None, [3],
    [["suburb"], "TEXT"],
    [["address"], "TEXT NOT NULL"],
    [["rooms"], "INTEGER", ['room', 'rooms']],
    [["type"], "TEXT"],
    [["price"], "NUMERIC NOT NULL", ['$']],
    [["method"], "TEXT"],
    [["date"], "TEXT"],
    [["distance"], "NUMERIC"], 
    [["postcode"], "INTEGER"],
    [["bedrooms"], "INTEGER", ['bedroom', 'bedrooms']],
    [["bathrooms"], "INTEGER", ['bathroom', 'bathrooms']],
    [["cars"], "INTEGER"],
    [["landsize", "size"], "INTEGER", ['sq ft', 'square feet', 'ft^2']],
    [["area"], "INTEGER"],
    [["year"], "INTEGER", ['year', 'yr', 'yrs']],
    [["council"], "TEXT"],
    [["latitude"], "NUMERIC"],
    [["longitude"], "NUMERIC"],
    [["region"], "TEXT"],
    [["property_count"], "INTEGER"]
)
cars = Table(Domain.CAR, 0, [4, 5], # both the make and the model are type 1
    [["id"], "INTEGER NOT NULL UNIQUE"],
    [["region"], "TEXT NOT NULL"],
    [["price"], "NUMERIC NOT NULL", ['$']],
    [["year"], "INTEGER", ['year', 'yr', 'yrs']],
    [["manufacturer"], "TEXT"],
    [["model"], "TEXT"],
    [["condition"], "TEXT"],
    [["cylinders"], "INTEGER", ['cylinder', 'cylinders', 'cyl']],
    [["fuel"], "TEXT"], # gas, diesel, hybrid, electric
    [["odometer", "mileage"], "INTEGER", ['mile', 'miles', 'mi']],
    [["title_status", "title"], "TEXT"], # clean, rebuilt, salvage
    [["transmission"], "TEXT"], # manual, automatic
    [["drive"], "TEXT"], # fwd, rwd, 4wd
    [["size"], "TEXT"],
    [["type"], "TEXT"],
    [["paint_color", "paint", "color"], "TEXT"],
    [["state"], "TEXT"]
)

def execute(sqlCmd:string):
    import sqlite3
    from pathlib import Path
    con = sqlite3.connect(str(Path(__file__).parent) + "/../product_qa.db")
    cur = con.cursor()
    result = cur.execute(sqlCmd)
    ls = list(result)
    con.close()
    return ls


def query(table:Table, attrList:[int], where:string):
    cmd = "SELECT "
    # Here we need to build the list of attribute names
    first = True
    for attr in attrList:
        if first:
            first = False
        else:
            cmd += ", "
        cmd += table.dat[attr][0][0]
    if attrList == []:
        cmd += "*"
    
    cmd += " FROM " + table.name.value + " WHERE " + where + ";"
    #print(cmd)
    return execute(cmd)


def getTable(domain:Domain) -> Table:
    if domain == Domain.MOTORCYCLE:
        return motorcycles
    elif domain == Domain.JEWELRY:
        return jewelry
    elif domain == Domain.JOB:
        return jobs
    elif domain == Domain.FURNITURE:
        return furniture
    elif domain == Domain.HOUSING:
        return housing
    elif domain == Domain.CAR:
        return cars
    else:
        return None
