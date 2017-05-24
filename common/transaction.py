import ecdsa
import struct

class Transaction:

    def __init__(self, version, txid, utxo, pubKey):
        self.version = version
        self.txid = str.encode(txid)
        self.utxo = str.encode(utxo)
        self.pubKey = pubKey

    def getPack(self):
        return struct.pack('Ippp', self.version, self.txid, self.utxo, self.pubKey)

    def setSig(self, sig):
        self.sig = sig
