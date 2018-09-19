import sys
import sqlite3
import json
import socket
import datetime
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
        WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource

from search_trans_table import search
from search_trans_table import dict_factory
from search_trans_table import getCustData
from search_trans_table import getCustName
from search_trans_table import getCoffeeData
from search_trans_table import getGrindData
from search_trans_table import registerPurchase
from search_trans_table import registerClaim
from search_trans_table import registerCustomer

sqlite_file = 'data/cust_db.sqlite'
conn = sqlite3.connect(sqlite_file)
conn.row_factory = dict_factory
c = conn.cursor()
debug = False

class NameSearchProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("SocketConn: {}".format(request))

    def buildCustPageDataJSON(self, cust_id, c):
        name_info = getCustName(cust_id, c)[0]
        cust_data = getCustData(cust_id, c)
        claims = cust_data.pop()
        claim_count = len(claims)
        earned_rewards = len(cust_data)/10
        remaining_rewards = earned_rewards - claim_count
        remaining_purch = 10 - len(cust_data)%10
        for row in cust_data:
            dattee = datetime.datetime.strptime(row['purchase_date'], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
            row['purchase_date'] = dattee.strftime("%m/%d/%Y %I:%M %p")
            row['type'] = "Paid"

        for row in claims:
            dattee = datetime.datetime.strptime(row['purchase_date'], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=5)
            row['purchase_date'] = dattee.strftime("%m/%d/%Y %I:%M %p")
            row['type'] = "Free!"

        cust_data.extend(claims)
        
        return {"custId":cust_id,\
                "firstName":name_info['cust_first_name'],\
                "lastName":name_info['cust_last_name'],\
                "custData": sorted(cust_data, key=lambda k: k['purchase_date'], reverse=True),\
                "remainingRewards": remaining_rewards,\
                "remainingPurch": remaining_purch,\
                "coffeeData":getCoffeeData(c),\
                "grindData":getGrindData(c)}

    def onMessage(self, payload, isBinary):
        if debug: print(payload)
        data = []
        try:
            decoded = json.loads(payload)
        except ValueError:
            print("ERROR: Invalid JSON object recieved")
            decoded = {"type": -1}
            data = ["Data sent to server was not valid"]

        if decoded['type'] == 0:
            s_input = decoded['data']
            if len(s_input) > 0:
                cust_list = search(s_input, c)
                data = []
                for row in cust_list:
                    data.append(row)
                json_data = {"type":0, "data":data}
            else:
                json_data = {"type":0, "data":[]}
#           print json.dumps(json_data)
        elif decoded['type'] == 1:
            cust_id = decoded['data']
            #TODO:TRYCATCH NON INT
            data = self.buildCustPageDataJSON(cust_id, c)
            if debug: print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            json_data = {"type":1, "data":data}
        elif decoded['type'] == 2:
            purch_data = decoded['data']
            cust_id = purch_data['cust_id']
            registerPurchase(cust_id, purch_data['coffee_id'], purch_data['grind_id'], purch_data['weight'], c)
            conn.commit()
            data = self.buildCustPageDataJSON(cust_id, c)
            if debug: print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            json_data = {"type":1, "data":data}
        elif decoded['type'] == 3:
            data = decoded['data']
            cust_id = registerCustomer(data['last_name'], data['first_name'], c)
            if cust_id < 0:
                print "Customer already in DB"
                json_data = {"type":-2, "cust_id":cust_id*-1,\
                  "data":["Customer already in DB. if this is definitely a different person then add a middle initial or something to the first name field to differentiate"]}
            else:
                conn.commit()
                data = self.buildCustPageDataJSON(cust_id, c)
                if debug: print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
                json_data = {"type":1, "data":data}
        elif decoded['type'] == 4:
            claim_data = decoded['data']
            cust_id = claim_data['cust_id']
            registerClaim(cust_id, claim_data['coffee_id'], claim_data['grind_id'], claim_data['weight'], c)
            conn.commit()
            data = self.buildCustPageDataJSON(cust_id, c)
            if debug: print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            json_data = {"type":1, "data":data}
        elif decoded['type'] == -1:
            json_data = {"type":-1, "data":data}

        self.sendMessage(json.dumps(json_data).encode('utf8'))

if __name__ == "__main__":

    log.startLogging(sys.stdout)
    root = File(".")

    ip = socket.gethostbyname(socket.gethostname())
#   ip = "127.0.0.1"

    websocket_string = "ws://" + str(ip) + ":8080"
    factory0 = WebSocketServerFactory(websocket_string)
    factory0.protocol = NameSearchProtocol
    resource0 = WebSocketResource(factory0)

    root.putChild(u"ws0", resource0)

    site = Site(root)
    reactor.listenTCP(8080, site)
    reactor.run()
