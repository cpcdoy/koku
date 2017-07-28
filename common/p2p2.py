import logging
import socket
import _thread as thread
import time
import sys
import pickle
from common.block import Block
from enum import Enum

class KokuMessageType(Enum):
    GET_ADDR = 1
    ADDR = 2
    GET_FROM_LAST = 3
    FROM_LAST = 4
    GET_BLOCK = 5
    BLOCK = 6

class KokuStruct():
    def __init__(self):
        self.data = []
        self.type = 0

class KokuNetwork():
    def __init__(self, typ, logging, chain, miner, configFilename = '/tmp/addr.txt', port = 55555):
        self.ip = ''
        self.miner = miner
        self.PORT = port
        self.type = typ #client / miner
        self.logging = logging # Logging configuration
        self.chain = chain
        self.configFilename = configFilename
        self.knownPeers = set()
        self.peersSoc = {}
        self.myIpAddress = ""
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
        self.logging.info('serveraddr: ' + str(serveraddr[0]) + ':' + str(serveraddr[1]))
        try:
            self.serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSoc.bind(serveraddr)
            self.serverSoc.listen(5)
            self.myIpAddress = self.__getMyIpAddress()
            thread.start_new_thread(self.listenPeers,())
            self.serverStatus = 1

            with open(self.configFilename) as configFile:
                addrs = configFile.read().split()
            for addr in addrs:
                self.addPeerAndConnect(addr)

        except Exception as inst:
            self.logging.exception("Init")
            self.logging.error(type(inst))
            self.logging.error((inst.args))

    def __getMyIpAddress(self):
        return [l for l in ([ip for ip in \
                    socket.gethostbyname_ex(socket.gethostname())[2] if not \
                    ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', \
                    53)), s.getsockname()[0], s.close()) for s in \
                    [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    def broadcastMessage(self, type, msg):
        if self.serverStatus == 0:
          return
        for client in self.peersSoc.values():
            koku = KokuStruct()
            koku.data = msg
            koku.type = type
            data = pickle.dumps(koku)
            self.logging.info('Sent data : ' + str(data))
            client.send(data)

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
                self.logging.error("Handle koku protocol")
                self.logging.error(type(inst))
                self.logging.error((inst.args))
                continue
        clientsoc.close()
        self.removePeer(clientaddr)

    def handleKokuProtocol(self, data):
        try:
            self.logging.info('Received data ' + str(data))
            kokuStruct = pickle.loads(data)
            msgType = kokuStruct.type
            self.logging.info('KokuStruct type : ' + str(kokuStruct.type))
            self.logging.info('KokuStruct data : ' + str(kokuStruct.data))

            if msgType == KokuMessageType.GET_ADDR:
                self.logging.info("GET_ADDR")
                self.broadcastMessage(KokuMessageType.ADDR, [])
            if msgType == KokuMessageType.ADDR:
                for peer in kokuStruct.data:
                    self.addPeerAndConnect(peer)
                    self.logging.info("ADDR ")

            if msgType == KokuMessageType.GET_FROM_LAST:
                self.logging.info("GET FROM LAST")
                blockId = kokuStruct.data
                self.broadcastMessage(KokuMessageType.FROM_LAST, self.chain[blockId + 1:])
            if msgType == KokuMessageType.FROM_LAST:
                self.logging.info("FROM LAST")
                chainFromLast = kokuStruct.data
                if len(chainFromLast) > 0 and chainFromLast[0].id == chain[-1].id + 1:
                    self.chain += kokuStruct.data
                    self.miner.interrupt()

        except Exception as inst:
            self.logging.exception('handleKokuProtocol: ')
            self.logging.error(type(inst))
            self.logging.error((inst.args))

    def removePeer(self, clientaddr):
        self.peersSoc.pop(clientaddr, None)

    def addPeer(self, peerSoc, peerIp):
        self.knownPeers.add(peerIp)
        self.peersSoc[peerIp] = peerSoc

    def addPeerAndConnect(self, peerIp, peerPort = 55555):
        self.logging.info('Fetching new peer: ' + peerIp)
        if self.serverStatus == 0 and peerIp != self.myIpAddress:
          return
        clientaddr = (peerIp, peerPort)
        if (peerIp in self.knownPeers):
            return
        try:
            self.logging.info('Ok adding')
            clientsoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsoc.connect(clientaddr)
            self.addPeer(clientsoc, peerIp)
            thread.start_new_thread(self.handlePeerInteractions, (clientsoc, clientaddr))
        except Exception as inst:
            self.logging.exception('AddPeerAndConnect: ' + str(peerIp))
            self.logging.error(type(inst))
            self.logging.error((inst.args))

    def closeAll(self):
        for peer in self.peersSoc.values():
            peer.close()
        self.serverSoc.close()

def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    fh = logging.FileHandler('/tmp/koku.log', 'a')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    p = KokuNetwork('miner', logger)

    time.sleep(3)
    #p.addPeerAndConnect(sys.argv[1], int(sys.argv[3]))
    for i in range(10):
        p.broadcastMessage(KokuMessageType.GET_ADDR, [])
        time.sleep(1)
        #p.addPeerAndConnect(sys.argv[1], int(sys.argv[3]))
        print('sending')
        print('known type:', type(p.knownPeers))
        #print('pickle dump:', pickle.dumps(p.knownPeers))
        print('arr', p.knownPeers)

    p.closeAll()

if __name__ == '__main__':
  main()
