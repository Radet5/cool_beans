import csv
from tabulate import tabulate
import sqlite3

from build_transition_table import initializeTree
from build_transition_table import addName
from build_transition_table import graph
from build_transition_table import insertCustRowIntoDb
from build_transition_table import insertTransitionTableRowIntoDb

with open('../data/customer_list.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', skipinitialspace=True)
    names = sorted(reader, key=lambda n: n['last_name'])
    sqlite_file = '../data/cust_db.sqlite'

    #Connect
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()


    print "\n\nEnroling: "+names[0]['last_name'].lower()
    insertCustRowIntoDb(names[0], c)
    conn.commit()
    transition_table = initializeTree(names[0]['last_name'].lower(), c.lastrowid)
    print "\n\n"+tabulate(transition_table, headers="keys",\
                          tablefmt="grid")+"\n\n"
    for row in names[1:]:
        enrollee = row['last_name'].lower()
        cust_id = insertCustRowIntoDb(row, c)
        conn.commit()
        addName(transition_table, enrollee, cust_id)
    
    print "\n\n"+tabulate(transition_table, headers="keys",\
                          tablefmt="grid")+"\n\n"

    for row in transition_table: 
        insertTransitionTableRowIntoDb(row, c)
        conn.commit()

    conn.close()
    tree_graph = graph(transition_table)
    with open("../data/graph.dot", "w") as dot_file:
        dot_file.write(tree_graph)
