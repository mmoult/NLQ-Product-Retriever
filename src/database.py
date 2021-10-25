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
        cmd += table.dat[attr][0]
    if attrList == []:
        cmd += "*"
    
    cmd += " FROM " + table.name + " WHERE " + where + ";"
    #print(cmd)
    return execute(cmd)