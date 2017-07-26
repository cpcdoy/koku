import ecdsa
import struct

class Transaction:

    def __init__(self, amount, version, txid, utxo, pubKey):
        self.amount = amount
        self.version = version
        self.txid = str.encode(txid)
        self.utxo = str.encode(utxo)
        self.pubKey = pubKey
        self.sender = str.encode(getAddr(pubKey))

    def getPack(self):
        return struct.pack('IIpppp', self.amount, self.version, self.txid, self.utxo, self.pubKey, self.sender)

    def setSig(self, sig):
        self.sig = sig
