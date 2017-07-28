import time
import struct
import random
import hashlib
from common.merkle import Merkle

import logging

class Block:

    def __init__(self, prev, root, idBlock):
        self.prev = prev
        self.root = root
        self.id = idBlock
        self.bits = 20
        self.pad = 0

    #Sets the transactions list of this block.
    #If the Merkle root matches returns True. Returns false otherwise
    def setTransactions(self, transactions):
        #First we get the list of transactions hashes
        hashlist = []
        for t in transactions:
            m = hashlib.sha256()
            m.update(t.getPack())
            hashlist.append(m.digest())

        #Then we can compute the Merkle root given by those hashes
        merkle = Merkle(hashlist)
        self.transactions = transactions
        return True

    #Returns a tuple indicating if this block is the last one where addr spent
    #The second term of the tuple is the amount earned by addr in this block
    def getIncome(self, addr):
        last = False
        total = 0
        for t in self.transactions:
            if t.dest == addr and t.checkSig():
                total += t.amount
            elif t.sender == addr and t.checkSig():
                total += t.utxo
                last = True
        return (last, total)

    def getPack(self):
        return struct.pack('32s32s3I', self.prev, self.root, self.id, self.bits, self.pad)

    def unpack(self, buff):
        self.prev, data = struct.unpack('32s', buff[:32])[0], buff[32:]
        self.root, data = struct.unpack('32s', data[:32])[0], data[32:]
        obj = struct.unpack('3I', data)
        self.id = obj[0]
        self.bits = obj[1]
        self.pad = obj[2]

    def getHash(self):
        m = hashlib.sha256()
        m.update(self.getPack())
        return m.digest()

def checkChain(chain):
    prev = None
    for b in chain:
        if not prev is None and prev != b.prev:
            return False
        m = hashlib.sha256()
        m.update(b.getPack())
        prev = m.digest()
    return True

def getAmountAvailable(addr, chain):
    rev = chain[::-1]
    i = 0
    ans = 0
    last = False
    while i < len(rev) and not last:
        last, amount = getIncome(rev[i])
        ans += amount
    return ans
