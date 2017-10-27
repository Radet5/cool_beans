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
        try:
            decoded = json.loads(payload)
        except ValueError:
            print("ERROR: Invalid JSON object recieved")
            decoded = {"type": -1}

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
            data = {"custId":cust_id, "custData": getCustData(cust_id, c), "coffeeData":getCoffeeData(c),\
                    "grindData":getGrindData(c)}
            print data
            json_data = {"type":1, "data":data}
        elif decoded['type'] == 2:
            data = decoded['data']
            cust_id = data['cust_id']
            registerPurchase(cust_id, data['coffee_id'], data['grind_id'], data['weight'], c)
            conn.commit()
            data = {"custId":cust_id, "custData": getCustData(cust_id, c), "coffeeData":getCoffeeData(c),\
                    "grindData":getGrindData(c)}
            print data
            json_data = {"type":1, "data":data}
        elif decoded['type'] == 3:
            data = decoded['data']
            print registerCustomer("Bell", "Dave", c)
            conn.commit()
            json_data = {"type":2, "data":[]}
        elif decoded['type'] == -1:
            json_data = {"type":-1}

        self.sendMessage(json.dumps(json_data).encode('utf8'))

if __name__ == "__main__":

    log.startLogging(sys.stdout)
    root = File(".")

    ip = socket.gethostbyname(socket.gethostname())
        
    websocket_string = "ws://" + str(ip) + ":8080"
    factory0 = WebSocketServerFactory(websocket_string)
    factory0.protocol = NameSearchProtocol
    resource0 = WebSocketResource(factory0)

    root.putChild(u"ws0", resource0)

    site = Site(root)
    reactor.listenTCP(8080, site)
    reactor.run()
