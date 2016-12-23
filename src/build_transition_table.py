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

#TODO: MAYBE. MIGHT NOT BE REUSABLE: rework addName into a searchTree function
#       which returns info nessecary to add name in right place
#TODO: modify these functions to use SQL dtatbase
def addName(tree, name):
    """Returns NULL
        Adds name to tree"""
    print "\nEnroling: "+name+"\n"
    state = 0
    for depth, input_char in enumerate(name):
        print "\nDepth: "+str(depth)+", State: "+str(state)+\
              ", Input: "+input_char

        nxt = selectInput(tree, state, input_char)
        #Check if there is a transition entry from current state using current
        # input. If so: follow the transition to next state
        if nxt:
            state = nxt[0]['next']
            print "Transition exists for: "+input_char+"\n"
        else:
            cur_state = selectState(tree, state)
            new_state_id = sorted(tree, key=lambda s: s['state'],\
                                  reverse=True)[0]['state']+1
            #If only one entry for current state:
            if len(cur_state) == 1:
                print "LEAF NODE: POSSIBLE COLLISION"
                #Weird work around for dealing with state 0
                if not cur_state[0]['results']:
                    tree.append({'input':input_char, 'state':state, 'prev':'',\
                                 'results':[], 'next':new_state_id})
                    tree.append({'input':'', 'state':new_state_id,\
                                 'prev':state, 'results':[name], 'next':''})
                    return
                #Same last name, so multiple results in one leaf.
                # SHOULD eventually RECORD THE CUSTOMER ID's HERE
                elif cur_state[0]['results'][0] == name:
                    print "COllISION!"
                    cur_state[0]['results'].append(name)
                    return
 # TODO: Detect and handle Ash-Ashley / Atkins-Akinson bug
 #BROKEN ATTEMPTS:
 #              elif len(cur_state[0]['results'][0]) < len(name):
 #                  print "Ya Ol Shorty!\n"
 #                  tree.append({'input':'', 'state':new_state_id, 'next':'',\
 #                               'prev':state,\
 #                               'results':cur_state[0]['results'][:]})
 #                  cur_state[0]['input'] = cur_state[0]['results'][0][depth]
 #                  cur_state[0]['next'] = new_state_id
 #                  cur_state[0]['results'] = []
##                  new_state_id += 1
##                  tree.append({'input':name[depth+1], 'state':state,\
 #                               'next':new_state_id,\
 #                               'prev':cur_state[0]['prev'], 'results':[]})
##                  tree.append({'input':'', 'state':new_state_id, 'next':'',\
 #                               'prev':state, 'results':[name]})
##                  return

                #If there's not a transition for current input AND there is no
                # collision then current leaf needs to be moved down to next
                # depth level and a transition entered. Also need to insert
                # current entry and record the transition entry for it
                #TODO: MAYBE this is where the Ashley bug should be fixed,
                # doesn't have a way to handle when there are no more letters
                # in current entry name
                else:
                    print "Need to branch!\n"
                    tree.append({'input':'', 'state':new_state_id, 'next':'',\
                                 'prev':state,\
                                 'results':cur_state[0]['results'][:]})
                    cur_state[0]['input'] = cur_state[0]['results'][0][depth]
                    cur_state[0]['next'] = new_state_id
                    cur_state[0]['results'] = []
                    new_state_id += 1
                    tree.append({'input':input_char, 'state':state,\
                                 'next':new_state_id, 'prev':cur_state[0]['prev'],\
                                 'results':[]})
                    tree.append({'input':'', 'state':new_state_id, 'next':'',\
                                 'prev':state, 'results':[name]})
                    return 
            #If there are multiple transitions from current state, but none are
            # for the current input then we need to add a transition for
            # current input and then insert name
            elif len(cur_state) > 1:
                print "NOT IN TREE\n"
                tree.append({'input':input_char, 'state':state,\
                             'prev':cur_state[0]['prev'], 'results':[],\
                             'next':new_state_id})
                tree.append({'input':'', 'state':new_state_id, 'prev':state,\
                             'results':[name], 'next':''})
                return

def graph(tree):
    """Returns a string which can be used by dot to create a directed graph of
        the transition table"""
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
    print "\n\n"+tabulate(transition_table, headers="keys",\
                          tablefmt="fancy_grid")+"\n\n"
    for row in names[1:24]:
        enrollee = row['last_name'].lower()
        addName(transition_table, enrollee)
    
    print "\n\n"+tabulate(transition_table, headers="keys",\
                          tablefmt="fancy_grid")+"\n\n"


    tree_graph = graph(transition_table)
    with open("../data/graph.dot", "w") as dot_file:
        dot_file.write(tree_graph)
