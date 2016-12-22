import csv
from tabulate import tabulate

def initializeTree(name):
    return [{'state':0, 'input':name[0], 'next':1, 'prev':'', 'results':[]},
            {'state':1, 'input':'', 'next':'', 'prev':0, 'results':[name]}]

def selectState(tree, state):
    """Returns a list of Dicts
    Returns all entries with state == state"""
    return [entry for entry in tree if entry['state'] == state]

def selectInput(tree, state, input_char):
    """Returns a list of dicts
    Returns all entries with state == state AND input == input_char"""
    sel = selectState(tree, state)
    return [entry for entry in sel if entry['input'] == input_char]

def addName(tree, name):
    print "\nEnroling: "+name+"\n"
    state = 0
    for depth, input_char in enumerate(name):
        print "\nDepth: "+str(depth)+", State: "+str(state)+", Input: "+input_char

        nxt = selectInput(tree, state, input_char)
        if nxt:
            state = nxt[0]['next']
            print "Transition exists for: "+input_char+"\n"
        else:
            cur_state = selectState(tree, state)
            new_state_id = sorted(tree, key=lambda s: s['state'], reverse=True)[0]['state']+1
            if len(cur_state) == 1:
                print "LEAF NODE: POSSIBLE COLLISION"
                if not cur_state[0]['results']:
                    tree.append({'input':input_char, 'state':state, 'prev':'', 'results':[], 'next':new_state_id})
                    tree.append({'input':'', 'state':new_state_id, 'prev':state, 'results':[name], 'next':''})
                    return
                elif cur_state[0]['results'][0] == name:
                    print "COllISION!"
                    cur_state[0]['results'].append(name)
                    return
                elif len(cur_state[0]['results'][0]) < len(name):
                    print "Ya Ol Shorty!\n"
                    tree.append({'input':'', 'state':new_state_id, 'next':'', 'prev':state, 'results':cur_state[0]['results'][:]})
                    cur_state[0]['input'] = cur_state[0]['results'][0][depth]
                    cur_state[0]['next'] = new_state_id
                    cur_state[0]['results'] = []
#                   new_state_id += 1
#                   tree.append({'input':name[depth+1], 'state':state, 'next':new_state_id, 'prev':cur_state[0]['prev'], 'results':[]})
#                   tree.append({'input':'', 'state':new_state_id, 'next':'', 'prev':state, 'results':[name]})
#                   return
                else:
                    print "Need to branch!\n"
                    tree.append({'input':'', 'state':new_state_id, 'next':'', 'prev':state, 'results':cur_state[0]['results'][:]})
                    cur_state[0]['input'] = cur_state[0]['results'][0][depth]
                    cur_state[0]['next'] = new_state_id
                    cur_state[0]['results'] = []
                    new_state_id += 1
                    tree.append({'input':input_char, 'state':state, 'next':new_state_id, 'prev':cur_state[0]['prev'], 'results':[]})
                    tree.append({'input':'', 'state':new_state_id, 'next':'', 'prev':state, 'results':[name]})
                    return 
            elif len(cur_state) > 1:
                print "NOT IN TREE\n"
                tree.append({'input':input_char, 'state':state, 'prev':cur_state[0]['prev'], 'results':[], 'next':new_state_id})
                tree.append({'input':'', 'state':new_state_id, 'prev':state, 'results':[name], 'next':''})
                return

#           node = selectState(tree,nxt[0]['next'])
#           if node[0]['results']:
#               if node[0]['results'] == name:
#                   node[0]['results'].append(name)
#               else:
#                   break
#   print tabulate(nxt,headers="keys",tablefmt="fancy_grid")

def graph(tree):
    f = "digraph {\n"
    for row in tree:
        A = row['state']
        B = row['next']
        label = row['input']
        if B:
            f += "\t"+str(A)+" -> "+str(B)+" [label = \""+label+"\"]\n"
        else:
            f += "\t"+str(A)+" -> "+row['results'][0]+"\n"
    f += "}"
    return f

with open('../data/customer_list.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', skipinitialspace=True)
    names = sorted(reader, key=lambda n: n['last_name'])
#   names = []
#   for row in reader:
#       names.append(row)

    print "\n\nEnroling: "+names[0]['last_name'].lower()
    transition_table = initializeTree(names[0]['last_name'].lower())
    print "\n\n"+tabulate(transition_table, headers="keys",tablefmt="fancy_grid")+"\n\n"
    for row in names[1:24]:
        enrollee = row['last_name'].lower()
        addName(transition_table, enrollee)
    
    print "\n\n"+tabulate(transition_table, headers="keys",tablefmt="fancy_grid")+"\n\n"


    tree_graph = graph(transition_table)
    with open("../data/graph.dot", "w") as dot_file:
        dot_file.write(tree_graph)
