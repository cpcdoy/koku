import time
import struct
import random
import hashlib
from common.merkle import Merkle

class Block:

    def __init__(self, prev, root):
        self.prev = prev
        self.root = root
        self.time = int(round(time.time()))
        self.bits = 20
        self.pad = random.randrange(2 ** 32)

    #Sets the transactions list of this block.
    #If the Merkle root matches returns True. Returns false otherwise
    def setTransactions(self, transactions):
        #First we get the list of transactions hashes
        hashlist = []
        for t in transactions:
            m = hashlib.sha256()
            m.update(t.getSignedPack())
            hashlist.append(m.digest())

        #Then we can compute the Merkle root given by those hashes
        merkle = Merkle(hashlist)
        if merkle.getRoot() != self.root:
            return False
        self.transactions = transactions
        return True

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
        prev_encode = bytearray()
        prev_encode.extend(map(ord, self.prev))
        root_encode = bytearray()
        root_encode.extend(map(ord, self.root))

        return struct.pack('32s32s3I', prev_encode, root_encode, self.time, self.bits, self.pad)

    def unpack(self, buff):
        self.prev, data = struct.unpack('32s', buff[:32])[0].decode(), buff[32:]
        self.root, data = struct.unpack('32s', data[:32])[0].decode(), data[32:]
        obj = struct.decode('3I', data)
        self.time = obj[0]
        self.bits = obj[1]
        self.pad = obj[2]

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
