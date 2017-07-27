import ecdsa
import time
import struct
from common.address import getAddr

class Transaction:

    def __init__(self, amount, utxo, dest, pubKey):
        self.amount = amount
        self.utxo = utxo
        self.time = int(round(time.time()))
        self.pubKey = pubKey.to_string()
        self.sender = str.encode(getAddr(pubKey))
        self.sig = str.encode('')
        self.dest = str.encode(dest)

    def getPack(self, sig=False):
        if sig:
            return struct.pack('3I64p44p44p', self.amount, self.utxo, self.time,
                    self.pubKey, self.sender, self.dest)
        return struct.pack('3I64p44p64p44p', self.amount, self.utxo, self.time,
                self.pubKey, self.sender, self.sig, self.dest)


    def unpack(self, buff):
        obj, data = struct.unpack('3I', buff[:12]), buff[12:]
        self.amount = obj[0]
        self.utxo = obj[1]
        self.time = obj[2]
        (self.pubKey, ), data = struct.unpack('64p', data[:64]), data[64:]
        (self.sender, ), data = struct.unpack('44p', data[:44]), data[44:]
        (self.sig, ), data = struct.unpack('64p', data[:64]), data[64:]
        (self.dest, ), data = struct.unpack('44p', data[:44]), data[44:]
    
    def setSig(self, sig):
        self.sig = sig
