'''
Created on Oct 1, 2021

@author: moultmat
'''

import sqlite3

if __name__ == '__main__':
    con = sqlite3.connect('product_qa.db')
    cur = con.cursor()
    '''
    cur.execute('CREATE TABLE stocks
               (date text, trans text, symbol text, qty real, price real)')
    '''
    con.commit() # Commit changes
    con.close() # close after we are done