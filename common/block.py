import random
import struct

class Block:

    def __init__(self, prev, root):
        self.prev = prev
        self.root = root
        self.pad = random.randrange(2 ** 64)
    
    def getPack(self):
        return struct.pack('ssQ', self.prev, self.root, self.pad)
