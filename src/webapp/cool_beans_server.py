import sys
import sqlite3
import json
from twisted.web.static import File
from twisted.python import log
from twisted.web.server import Site
from twisted.internet import reactor

from autobahn.twisted.websocket import WebSocketServerFactory, \
        WebSocketServerProtocol

from autobahn.twisted.resource import WebSocketResource

from search_trans_table import search
from search_trans_table import dict_factory

sqlite_file = 'data/cust_db.sqlite'
conn = sqlite3.connect(sqlite_file)
conn.row_factory = dict_factory
c = conn.cursor()

class NameSearchProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("CustSearchConn: {}".format(request))

    def onMessage(self, payload, isBinary):
        if len(payload) > 0:
            cust_list = search(payload, c)
            data = []
            for row in cust_list:
                data.append(row)
#           print data
            self.sendMessage(json.dumps(data).encode('utf8'))
#           print html
            print(payload)
        else:
            self.sendMessage("[]".encode('utf8'))

class CustomerDataRequestProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print("CustDataConn: {}".format(request))

    def onMessage(self, payload, isBinary):
        text = "Well... they ARE a customer with id = "  + str(payload)
        self.sendMessage(text.encode('utf8'))

if __name__ == "__main__":

    log.startLogging(sys.stdout)
    root = File(".")

    factory0 = WebSocketServerFactory(u"ws://192.168.0.6:8080")
    factory0.protocol = NameSearchProtocol
    resource0 = WebSocketResource(factory0)

    factory1 = WebSocketServerFactory(u"ws://192.168.0.6:8080")
    factory1.protocol = CustomerDataRequestProtocol
    resource1 = WebSocketResource(factory1)

    root.putChild(u"ws0", resource0)
    root.putChild(u"ws1", resource1)

    site = Site(root)
    reactor.listenTCP(8080, site)
    reactor.run()
