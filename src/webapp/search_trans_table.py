import csv
from tabulate import tabulate
import sqlite3
import datetime
from shutil import copyfile

from build_transition_table import addName
from build_transition_table import initializeTree
from build_transition_table import insertCustRowIntoDb
from build_transition_table import insertTransitionTableRowIntoDb

def dict_factory(db_curs, row):
    d = {}
    for idx, col in enumerate(db_curs.description):
        d[col[0]] = row[idx]
    return d

def getCustData(cust_id, db_curs):
    db_curs.execute('SELECT * FROM purchase JOIN coffee ON purchase_coffee_id = coffee_id JOIN grind ON purchase_grind_id = grind_id WHERE purchase_cust_id = ?', (str(cust_id),))
    return db_curs.fetchall()

def getCustName(cust_id, db_curs):
    db_curs.execute('SELECT cust_first_name, cust_last_name FROM cust WHERE cust_id = ?',(cust_id,))
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
    backup_destination = '../../data/cust_db.sqlite.bak_' + datetime.datetime.now().strftime("%Y_%m_%d_%H-%M")
    copyfile('../../data/cust_db.sqlite', backup_destination)
    low_last_name = last_name.lower()
    low_first_name = first_name.lower()
    print low_last_name
    db_curs.execute('SELECT * FROM cust WHERE cust_last_name = ?',(low_last_name,))
    rows = db_curs.fetchall()
    is_name_unique = True
    if len(rows) > 0:
        is_name_unique = False
        for row in rows:
            db_first_name = row['cust_first_name']
            if low_first_name == db_first_name:
                is_name_unique = False
                return row['cust_id'] * -1
                break
            else :
                print "Different first name"
                is_name_unique = True
    if is_name_unique:
        cust_id = insertCustRowIntoDb({'last_name':low_last_name,\
                                       'first_name':low_first_name}, db_curs)

        #TODO:FIX THIS
        #This is a hack. just completely rebuilding and reinsrting tansition_table!!
        db_curs.execute('SELECT cust_first_name, cust_last_name, cust_id\
                         FROM cust')
        rows = db_curs.fetchall()
        customers = sorted(rows, key=lambda n: n['cust_last_name'])

        transition_table = initializeTree(customers[0]['cust_last_name'], customers[0]['cust_id'])

        for row in customers[1:]:
            addName(transition_table, row['cust_last_name'], row['cust_id'])

        #delete transition table from db
        db_curs.execute('DELETE FROM transition')
        db_curs.execute('DELETE FROM result')
        for row in transition_table:
            insertTransitionTableRowIntoDb(row, db_curs)

#       transition_table = getTransitionTable(db_curs)
    #TODO: insert last name and ID into transition table
#       addName(transition_table, low_last_name, cust_id)
    #TODO: get list of rows to modify by ID along with new row
    #TODO: get list of rows to add
    #TODO: Figure out modifications/additions to results table
    #TODO: Backup old SQL transition table
    #TODO: Backup old SQL results table
    #TODO: modify SQL transition table
    #TODO: modify SQL results table
    #TODO: Check for errors

        return cust_id

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
