import socket
import _thread as thread
import time
import sys
import pickle
from enum import Enum

class KokuMessageType(Enum):
    GET_ADDR = 1
    ADDR = 2
    GET_DATA = 3
    DATA = 4

class KokuStruct():
    def __init__(self):
        self.data = []
        self.type = 0

class KokuNetwork():
    def __init__(self, typ, publicKey, signature, port = 55555):
        self.ip = ''
        self.PORT = port
        self.type = typ #client / miner
        self.__publicKey = publicKey
        self.__signature = signature
        self.knownPeers = []
        self.peersSoc = {}
        self.Init()

    def Init(self):
        self.serverSoc = None
        self.serverStatus = 0
        self.buffsize = 1024
        if self.serverSoc != None:
            self.serverSoc.close()
            self.serverSoc = None
            self.serverStatus = 0
        serveraddr = (self.ip, self.PORT)
        try:
            self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSoc.bind(serveraddr)
            self.serverSoc.listen(5)
            thread.start_new_thread(self.listenPeers,())
            self.serverStatus = 1
        except Exception as inst:
            print(type(inst))
            print(inst.args) 
        pass

    def sendMessage(self, ip, msg):
        pass

    def broadcastMessage(self, type, msg):
        if self.serverStatus == 0:
          return
        if msg == '':
            return
        for client in self.peersSoc.values():
          koku = KokuStruct()
          koku.arr = msg
          koku.type = type
          client.send(pickle.dumps(koku))

    def listenPeers(self):
        while 1:
          clientsoc, clientaddr = self.serverSoc.accept()
          self.addPeer(clientsoc, clientaddr)
          thread.start_new_thread(self.handlePeerInteractions, (clientsoc, clientaddr))
        self.serverSoc.close()

    def handlePeerInteractions(self, clientsoc, clientaddr):
        while 1:
            try:
                data = clientsoc.recv(self.buffsize)
                if not data:
                    continue
                self.handleKokuProtocol(data)
            except:
                continue
        clientsoc.close()
        self.removePeer(clientaddr)

    def handleKokuProtocol(self, data):
        kokuStruct = pickle.loads(data)
        msgType = KokuStruct.type
        if msgType == KokuMessageType.GET_ADDR:
            self.broadcastMessage(msgType + 1, self.knownPeers)
        if msgType == KokuMessageType.ADDR:
            for peer in kokuStruct.data:
                self.addPeerAndConnect(peer)
        if msgType == KokuMessageType.GET_DATA:
            self.broadcastMessage(msgType + 1, 'lol')
        if msgType == KokuMessageType.DATA:
            print('Not implemented')

    def removePeer(self, clientaddr):
        self.peersSoc.pop(clientaddr, None)

    def addPeer(self, peerSoc, peerIp):
        self.knownPeers.append(peerIp)
        self.peersSoc[peerIp] = peerSoc

    def addPeerAndConnect(self, peerIp, peerPort = 55555):
        if self.serverStatus == 0:
          return
        clientaddr = (peerIp, peerPort)
        print('client_addr = ', clientaddr)
        if (peerIp in self.knownPeers):
            return
        try:
            print('Ok adding')
            clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsoc.connect(clientaddr)
            self.addPeer(clientsoc, peerIp)
            thread.start_new_thread(self.handlePeerInteractions, (clientsoc, clientaddr))
        except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows 
            x, y = inst.args
            print('x =', x)
            print('y =', y)

    def closeAll(self):
        for peer in self.peersSoc.values():
            peer.close()
        self.serverSoc.close()

def main():
    p = KokuNetwork('miner', 'lol', 'lol', int(sys.argv[2]))

    time.sleep(3)
    p.addPeerAndConnect(sys.argv[1], int(sys.argv[3]))
    for i in range(3):
        p.broadcastMessage(KokuMessageType.GET_ADDR, p.knownPeers)
        time.sleep(1)
        p.addPeerAndConnect(sys.argv[1], int(sys.argv[3]))
        print('sending')
        print('known type:', type(p.knownPeers))
        #print('pickle dump:', pickle.dumps(p.knownPeers))
        print('arr', p.knownPeers)

    p.closeAll()

if __name__ == '__main__':
  main()
