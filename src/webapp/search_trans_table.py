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
    result_a = db_curs.fetchall()
    db_curs.execute('SELECT * FROM claim JOIN coffee ON claim_coffee_id = coffee_id JOIN grind ON claim_grind_id = grind_id WHERE claim_cust_id = ?', (str(cust_id),))
    result_b = db_curs.fetchall()
    result_a.append(result_b)
    return result_a

def getCustInfo(cust_id, db_curs):
    db_curs.execute('SELECT cust_first_name, cust_last_name, cust_notes FROM cust WHERE cust_id = ?',(cust_id,))
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

def registerClaim(cust_id, coffee_id, grind_id, weight, db_curs):
    db_curs.execute('INSERT INTO claim (claim_cust_id, claim_coffee_id,\
                     claim_grind_id, purchase_weight) VALUES (?,?,?,?)',(str(cust_id), str(coffee_id), str(grind_id), str(weight)))

def registerCustNotes(cust_id, cust_notes, db_curs):
    db_curs.execute('UPDATE cust\
                     SET cust_notes = ?\
                     WHERE cust_id = ?',(cust_notes, str(cust_id)))

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

def interactiveSearch(c):
    last_name = str(raw_input("Customer Last Name: "))
    cust_list = search(last_name, c)
    print tabulate(cust_list, headers="keys", tablefmt="grid")
    first_name = str(raw_input("\nCustomer First Name: "))
    for cust in cust_list:
        if cust[0] == last_name:
            if cust[1] == first_name:
                print "\n"
                return [cust[0], cust[1], cust[2]]
    print "\n"
    return [last_name, first_name, 0]

def registerMassPurchase(cust_id, c):
    print "Customer ID: "+ str(cust_id)
    coffees = getCoffeeData(c)
    print tabulate(coffees, headers="keys", tablefmt="grid")
    coffee = raw_input("Select Coffee: ")
    if int(coffee) > len(coffees) or int(coffee) < 1:
        print "Invalid ID"
        return
    print "\n" + coffees[int(coffee)-1][1] + "\n"
    grinds = getGrindData(c)
    print tabulate(grinds, headers="keys", tablefmt="grid")
    grind = raw_input("Select Grind: ")
    if int(grind) > len(grinds) or int(grind) < 1:
        print "Invalid ID"
        print len(grinds)
        return
    print "\n" + grinds[int(grind)-1][1] + "\n"

    weight = raw_input("Coffee Weight(0 for \"See notes\"): ")

    cust_info = getCustInfo(cust_id, c)
    print "\nRegistering purchases for " + cust_info[0][0] + " " + cust_info[0][1]
    purchase_count = raw_input("\nHow many " + coffees[int(coffee)-1][1] + " " + grinds[int(grind)-1][1] + " " + weight + "oz to register: ")
    for i in range(0, int(purchase_count)): 
        registerPurchase(cust_id, coffee, grind, weight, c)

if __name__ == "__main__":
    

    sqlite_file = 'data/cust_db.sqlite'

    #Connect
    conn = sqlite3.connect(sqlite_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    menu = {}
    menu['1']="Search"
    menu['2']="Enroll"
    menu['3']="Add Purchases"
    menu['4']="Exit"
    while True:
        cust_id = -1
        options=menu.keys()
        options.sort()
        for entry in options:
            print entry, menu[entry]

        selection=raw_input("Please Select:")
        print "\n"
        if selection =='1':
            cust = interactiveSearch(c)
            if cust[2]:
                print cust[1] + " " + cust[0] + ", ID: " + str(cust[2])
                cust_id = cust[2]
                if raw_input("If you would like to add purchases please enter 3: ") == '3':
                    registerMassPurchase(cust_id, c)
                    conn.commit()
            else: print "No such customer"
            print "\n\n"
        elif selection == '2':
            cust = interactiveSearch(c)
            if cust[2]:
                print cust[1] + " " + cust[0] + " is already enrolled!"
                if raw_input("If you would like to add purchases please enter 3: ") == '3':
                    registerMassPurchase(cust[2], c)
                    conn.commit()
            else:
                cust_id = registerCustomer(cust[0], cust[1], c)
                conn.commit()
                if raw_input("If you would like to add purchases please enter 3: ") == '3':
                    registerMassPurchase(cust_id, c)
                    conn.commit()
            print "\n\n"
        elif selection == '3':
            cid = raw_input("Please enter customer ID (or 0 to search): ")
            if cid == '0':
                cust_id = interactiveSearch(c)[2]
                if cust_id > 0:
                    registerMassPurchase(cust_id, c)
                    conn.commit()
                else:
                    print "No such customer!"
            else: 
                registerMassPurchase(cid, c)
                conn.commit()
            print "\n"
        elif selection == '4':
            break
        else:
            print "Unknown Option Selected!"


#   print "\n\nsearch b"
#   search("b", c)

    conn.close()
