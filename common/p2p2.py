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
    def __init__(self, typ, configFilename = 'addr.txt', port = 55555):
        self.ip = ''
        self.PORT = port
        self.type = typ #client / miner
        self.configFilename = configFilename
        self.knownPeers = set()
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
        print('serveraddr:', serveraddr)
        try:
            self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSoc.bind(serveraddr)
            self.serverSoc.listen(5)
            self.myIpAddress = self.__getMyIpAddress()
            print("****************", self.myIpAddress)
            thread.start_new_thread(self.listenPeers,())
            self.serverStatus = 1

            with open(self.configFilename) as configFile:
                addrs = configFile.read().split()
            for addr in addrs:
                self.addPeerAndConnect(addr)

        except Exception as inst:
            print(type(inst))
            print(inst.args)
        pass

    def __getMyIpAddress(self):
        return [l for l in ([ip for ip in \
                    socket.gethostbyname_ex(socket.gethostname())[2] if not \
                    ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', \
                    53)), s.getsockname()[0], s.close()) for s in \
                    [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    def sendMessage(self, ip, msg):
        pass

    def broadcastMessage(self, type, msg):
        if self.serverStatus == 0:
          return
        for client in self.peersSoc.values():
          koku = KokuStruct()
          koku.data = msg
          koku.type = type
          client.send(pickle.dumps(koku))

    def listenPeers(self):
        while 1:
          clientsoc, clientaddr = self.serverSoc.accept()
          self.addPeer(clientsoc, clientaddr[0])
          thread.start_new_thread(self.handlePeerInteractions, (clientsoc, clientaddr))
        self.serverSoc.close()

    def handlePeerInteractions(self, clientsoc, clientaddr):
        while 1:
            try:
                data = clientsoc.recv(self.buffsize)
                if not data:
                    continue
                self.handleKokuProtocol(data)
            except Exception as inst:
                print(type(inst))    # the exception instance
                print(inst.args)     # arguments stored in .args
                print(inst)          # __str__ allows
                x, y = inst.args
                print('x =', x)
                print('y =', y)
                continue
        clientsoc.close()
        self.removePeer(clientaddr)

    def handleKokuProtocol(self, data):
        kokuStruct = pickle.loads(data)
        msgType = kokuStruct.type
        print('KokuStruct type : ', kokuStruct.type)
        print('KokuStruct data : ', kokuStruct.data)
        if msgType == KokuMessageType.GET_ADDR:
            print("GET_ADDR")
            self.broadcastMessage(KokuMessageType.ADDR, [])
        if msgType == KokuMessageType.ADDR:
            for peer in kokuStruct.data:
                self.addPeerAndConnect(peer)
                print("ADDR ", peer)
        if msgType == KokuMessageType.GET_DATA:
            self.broadcastMessage(KokuMessageType.DATA, [])
        if msgType == KokuMessageType.DATA:
            print('Not implemented')

    def removePeer(self, clientaddr):
        self.peersSoc.pop(clientaddr, None)

    def addPeer(self, peerSoc, peerIp):
        if (peerIp != self.myIpAddress):
            self.knownPeers.add(peerIp)
            self.peersSoc[peerIp] = peerSoc

    def addPeerAndConnect(self, peerIp, peerPort = 55555):
        if self.serverStatus == 0:
          return
        clientaddr = (peerIp, peerPort)
        print('client_addr = ', clientaddr)
        print('peerIp:', peerIp)
        if (peerIp in self.knownPeers):
            return
        try:
            print('Ok adding')
            clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsoc.connect(clientaddr)
            self.addPeer(clientsoc, peerIp)
            thread.start_new_thread(self.handlePeerInteractions, (clientsoc, clientaddr))
        except Exception as inst:
            print('AddPeerAndConnect')
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
    p = KokuNetwork('miner')

    time.sleep(3)
    p.addPeerAndConnect(sys.argv[1], int(sys.argv[3]))
    for i in range(3):
        p.broadcastMessage(KokuMessageType.GET_ADDR, [])
        time.sleep(1)
        p.addPeerAndConnect(sys.argv[1], int(sys.argv[3]))
        print('sending')
        print('known type:', type(p.knownPeers))
        #print('pickle dump:', pickle.dumps(p.knownPeers))
        print('arr', p.knownPeers)

    p.closeAll()

if __name__ == '__main__':
  main()
