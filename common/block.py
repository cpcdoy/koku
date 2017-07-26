import hashlib
import random
import struct
import time

class Block:

    def __init__(self, prev, root):
        self.prev = prev
        self.root = root
        self.time = int(round(time.time()))
        self.bits = 20
        self.pad = random.randrange(2 ** 32)

    def setTransactions(self, transactions):
        self.transactions = transactions

    #Returns a tuple indicating if this block is the last one where addr spent
    #The second term of the tuple is the amount earned by addr in this block
    def getIncome(self, addr):
        last = False
        total = 0
        for t in self.transactions:
            if t.utxo == addr:
                if t.sender == addr:
                    last = True
                total += t.amount
        return (last, total)

    def getPack(self):
        prev_encode = self.prev.encode()
        root_encode = self.root.encode()

        return struct.pack('ssIII', prev_encode, root_encode, self.time, self.bits, self.pad)

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
