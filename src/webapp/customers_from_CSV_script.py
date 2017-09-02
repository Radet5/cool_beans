import csv
from tabulate import tabulate
import sqlite3

from build_transition_table import initializeTree
from build_transition_table import addName
from build_transition_table import graph

with open('../data/customer_list.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', skipinitialspace=True)
    names = sorted(reader, key=lambda n: n['last_name'])
#   names = []
#   for row in reader:
#       names.append(row)
    
    sqlite_file = '../data/cust_db.sqlite'

    #Connect
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()


    print "\n\nEnroling: "+names[0]['last_name'].lower()
    c.execute('INSERT INTO cust (cust_last_name, cust_first_name) VALUES (?,?)',\
              (names[0]['last_name'].lower(), names[0]['first_name'].lower()))
    conn.commit()
    transition_table = initializeTree(names[0]['last_name'].lower(), c.lastrowid)
    print "\n\n"+tabulate(transition_table, headers="keys",\
                          tablefmt="grid")+"\n\n"
    for row in names[1:]:
        enrollee = row['last_name'].lower()
        c.execute('INSERT INTO cust (cust_last_name, cust_first_name) VALUES (?,?)',\
                  (row['last_name'].lower(), row['first_name'].lower()))
        addName(transition_table, enrollee, c.lastrowid)
        conn.commit()
    
    print "\n\n"+tabulate(transition_table, headers="keys",\
                          tablefmt="grid")+"\n\n"

    for row in transition_table: 
        c.execute('INSERT INTO transition (transition_input, transition_state,\
                   transition_prev, transition_next) VALUES (?,?,?,?)',\
                  (row['input'], row['state'], row['prev'], row['next']))
        transition_row_id = c.lastrowid
        for result in row['results']:
            c.execute('INSERT INTO result (result_transition_id, result_cust_id)\
                       VALUES (?,?)', (transition_row_id, result[1]))
        conn.commit()

    conn.close()
    tree_graph = graph(transition_table)
    with open("../data/graph.dot", "w") as dot_file:
        dot_file.write(tree_graph)
