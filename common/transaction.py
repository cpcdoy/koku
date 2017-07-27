import ecdsa
import struct
from common.address import getAddr

class Transaction:

    def __init__(self, amount, version, txid, utxo, pubKey):
        self.amount = amount
        self.version = version
        self.txid = str.encode(txid)
        self.utxo = str.encode(utxo)
        self.pubKey = pubKey.to_string()
        self.sender = str.encode(getAddr(pubKey))
        self.sig = str.encode('')

    def getPack(self):
        return struct.pack('IIppppp', self.amount, self.version, self.txid,
                self.utxo, self.pubKey, self.sender, self.sig)

    def unpack(self, buff):
        obj = struct.unpack('IIppppp', buff)
        self.amount = obj[0]
        self.version = obj[1]
        self.txid = obj[2]
        self.utxo = obj[3]
        self.pubKey = obj[4]
        self.sender = obj[5]
        self.sig = obj[5]
    
    def setSig(self, sig):
        self.sig = sig
