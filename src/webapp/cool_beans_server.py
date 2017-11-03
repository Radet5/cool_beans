import sys
import sqlite3
import json
import socket
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
from search_trans_table import registerCustomer

sqlite_file = 'data/cust_db.sqlite'
conn = sqlite3.connect(sqlite_file)
conn.row_factory = dict_factory
c = conn.cursor()

class NameSearchProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("SocketConn: {}".format(request))

    def onMessage(self, payload, isBinary):
        print(payload)
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
            name_info = getCustName(cust_id, c)[0]
            data = {"custId":cust_id,\
                    "cust_first_name":name_info['cust_first_name'],\
                    "cust_last_name":name_info['cust_last_name'],\
                    "custData": getCustData(cust_id, c), "coffeeData":getCoffeeData(c),\
                    "grindData":getGrindData(c)}
            print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
            json_data = {"type":1, "data":data}
        elif decoded['type'] == 2:
            data = decoded['data']
            cust_id = data['cust_id']
            registerPurchase(cust_id, data['coffee_id'], data['grind_id'], data['weight'], c)
            conn.commit()
            name_info = getCustName(cust_id, c)[0]
            data = {"custId":cust_id,\
                    "cust_first_name":name_info['cust_first_name'],\
                    "cust_last_name":name_info['cust_last_name'],\
                    "custData": getCustData(cust_id, c), "coffeeData":getCoffeeData(c),\
                    "grindData":getGrindData(c)}
            print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
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
                name_info = getCustName(cust_id, c)[0]
                data = {"custId":cust_id,\
                        "cust_first_name":name_info['cust_first_name'],\
                        "cust_last_name":name_info['cust_last_name'],\
                        "custData": getCustData(cust_id, c), "coffeeData":getCoffeeData(c),\
                        "grindData":getGrindData(c)}
                print json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
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
