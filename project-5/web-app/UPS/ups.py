#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import psycopg2
import sys
 
 
con = None
 
try:
    con = psycopg2.connect("host='localhost' dbname='postgres' user='postgres' password='passw0rd'")   
    cur = con.cursor()
    #cur.execute("CREATE TABLE Ups(Id INTEGER PRIMARY KEY, Name VARCHAR(20), Price INT)")
    cur.execute("INSERT INTO \"UPS_ups\" VALUES( DEFAULT, 1, 1, 'food', 'no description', 5, 1,1,1, 'open', 'ncnc12345')")
    #cur.execute("INSERT INTO Products VALUES(2,'Sugar',7)")
    #cur.execute("INSERT INTO Products VALUES(3,'Coffee',3)")
    #cur.execute("INSERT INTO Products VALUES(4,'Bread',5)")
    #cur.execute("INSERT INTO Products VALUES(5,'Oranges',3)")
    con.commit()
except psycopg2.DatabaseError as e:
    if con:
        con.rollback()
 
    print ('Error %s' % e)    
    sys.exit(1)
 
finally:   
    if con:
        con.close()