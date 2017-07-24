import hashlib
import random
import struct
import time

class Block:

    def __init__(self, prev, root):
        self.prev = prev
        self.root = root
        self.time = int(round(time.time()))
        #self.time = time.gmtime()
        self.bits = 20
        self.pad = random.randrange(2 ** 32)

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
