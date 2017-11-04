#!/usr/bin/python2

import sqlite3

sqlite_file = '../data/cust_db.sqlite'

#Connect
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

#Create table
c.execute('CREATE TABLE cust (cust_id INTEGER PRIMARY KEY ASC,\
                              cust_last_name TEXT NOT NULL,\
                              cust_first_name TEXT NOT NULL,\
                              cust_email TEXT)')

c.execute('CREATE TABLE coffee (coffee_id INTEGER PRIMARY KEY ASC,\
                                coffee_name TEXT NOT NULL,\
                                coffee_desc TEXT)')

c.execute('CREATE TABLE grind (grind_id INTEGER PRIMARY KEY ASC,\
                               grind_desc TEXT)')

c.execute('CREATE TABLE purchase (purchase_id INTEGER PRIMARY KEY ASC,\
                                  purchase_cust_id INTEGER NOT NULL,\
                                  purchase_date TEXT DEFAULT CURRENT_TIMESTAMP,\
                                  purchase_coffee_id INTEGER NOT NULL,\
                                  purchase_grind_id INTEGER NOT NULL,\
                                  purchase_weight REAL NOT NULL,\
                                  FOREIGN KEY(purchase_cust_id)\
                                    REFERENCES cust(cust_id),\
                                  FOREIGN KEY(purchase_coffee_id)\
                                    REFERENCES coffee(coffee_id),\
                                  FOREIGN KEY(purchase_grind_id)\
                                    REFERENCES grind(grind_id))')

c.execute('CREATE TABLE claim (claim_id INTEGER PRIMARY KEY ASC,\
                                  claim_cust_id INTEGER NOT NULL,\
                                  purchase_date TEXT DEFAULT CURRENT_TIMESTAMP,\
                                  claim_coffee_id INTEGER NOT NULL,\
                                  claim_grind_id INTEGER NOT NULL,\
                                  purchase_weight REAL NOT NULL,\
                                  FOREIGN KEY(claim_cust_id)\
                                    REFERENCES cust(cust_id),\
                                  FOREIGN KEY(claim_coffee_id)\
                                    REFERENCES coffee(coffee_id),\
                                  FOREIGN KEY(claim_grind_id)\
                                    REFERENCES grind(grind_id))')

c.execute('CREATE TABLE transition (transition_id INTEGER PRIMARY KEY ASC,\
                                    transition_input CHARACTER,\
                                    transition_state INTEGER NOT NULL,\
                                    transition_prev INTEGER,\
                                    transition_next INTEGER)')

c.execute('CREATE TABLE result (result_id INTEGER PRIMARY KEY ASC,\
                                result_transition_id INTEGER NOT NULL,\
                                result_cust_id INTEGER NOT NULL,\
                                FOREIGN KEY(result_transition_id)\
                                    REFERENCES transition(transition_id),\
                                FOREIGN KEY(result_cust_id)\
                                    REFERENCES cust(cust_id))')

conn.commit()
conn.close()
