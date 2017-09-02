import csv
from tabulate import tabulate
import sqlite3

def dict_factory(db_curs, row):
    d = {}
    for idx, col in enumerate(db_curs.description):
        d[col[0]] = row[idx]
    return d

def getCustData(cust_id, db_curs):
    db_curs.execute('SELECT * FROM purchase JOIN coffee ON purchase_coffee_id = coffee_id JOIN grind ON purchase_grind_id = grind_id WHERE purchase_cust_id = ?', (str(cust_id),))
    return db_curs.fetchall()

def getCoffeeData(db_curs):
    db_curs.execute('SELECT * FROM coffee')
    return db_curs.fetchall()

def getGrindData(db_curs):
    db_curs.execute('SELECT * FROM grind')
    return db_curs.fetchall()

def getTransitionTable(db_curs):
    db_curs.execute('SELECT * FROM transition')
    transition_table = []
    rows = db_curs.fetchall()
    if len (rows) == 0: return []
    for row in rows:
        transition_table.append({'state': row['transition_state'],\
                      'input':row['transition_input'],\
                      'next':row['transition_next'],\
                      'prev':row['transition_prev'], 'results':[]})
    db_curs.execute('SELECT result_transition_id, cust_id, cust_last_name\
                     FROM result JOIN cust\
                        ON result_cust_id = cust_id')
    rows = db_curs.fetchall()
    if len (rows) == 0: return transition_table
    for row in rows:
        trans_id = row['result_transition_id']-1
        cust_id = row['cust_id']
        name = str(row['cust_last_name'])
        transition_table[trans_id]['results'].append((name, cust_id))
    return transition_table
        

def registerPurchase(cust_id, coffee_id, grind_id, weight, db_curs):
    db_curs.execute('INSERT INTO purchase (purchase_cust_id, purchase_coffee_id,\
                     purchase_grind_id, purchase_weight) VALUES (?,?,?,?)',(str(cust_id), str(coffee_id), str(grind_id), str(weight)))

def registerCustomer(last_name, first_name, db_curs):
    transition_table = getTransitionTable(db_curs)
    return tabulate(transition_table, headers="keys",tablefmt="grid")

def recurse(trans_id, db_curs):
    db_curs.execute('SELECT *  FROM transition\
                     WHERE transition_state = ?', (str(trans_id),))
    rows = db_curs.fetchall()
#   print tabulate(rows, headers="keys", tablefmt="grid")
    results = []
    for row in rows:
        nxt = row['transition_next']
        results.append(row['transition_id'])
        results = results + recurse(nxt, db_curs)
    return filter(None, results)

    
def search(name, db_curs):
    if name:
        name = name.lower()
#       print name[0]
        db_curs.execute('SELECT * FROM transition WHERE transition_state = 0 AND\
                         transition_input = ?', name[0])
        rows = db_curs.fetchall()
        nxt = []
        results = []
        if len (rows) == 0: return []
        for row in rows: 
#           print row
            nxt.append(row['transition_next'])
            results.append(row['transition_id'])
#           print nxt[-1]
#       print ""
        
        for letter in name[1:]:
#           print letter
            db_curs.execute('SELECT * FROM transition WHERE transition_state = \
                             ? AND transition_input = ?', (nxt[-1], letter))
            rows = db_curs.fetchall()
#           print tabulate(rows, headers="keys", tablefmt="grid")
            for row in rows:
                nxt.append(row['transition_next'])
                results.append(row['transition_id'])

#       print ""
#       print nxt[-1]
        results = results + recurse(nxt[-1], db_curs)

#       print results

        cust_list = []
        for trans_id in results:
            db_curs.execute('SELECT cust_last_name, cust_first_name, cust_id FROM result JOIN cust ON result_cust_id = cust_id WHERE result_transition_id = ?',(str(trans_id),))
            rows = db_curs.fetchall()
            cust_list = cust_list + rows
#       print tabulate(cust_list, headers="keys", tablefmt="grid")
        return cust_list


if __name__ == "__main__":

    sqlite_file = '../data/cust_db.sqlite'

    #Connect
    conn = sqlite3.connect(sqlite_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    print "blank search"
    search("", c)

    print "search bur"
    cust_list = search("bur", c)
    print tabulate(cust_list, headers="keys", tablefmt="grid")

#   print "\n\nsearch b"
#   search("b", c)

    conn.close()
