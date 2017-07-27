import hashlib
import math

class Merkle:

    def __init__(self, hashlist):
        self.tree = [hashlist]
        cur_list = hashlist
        while len(cur_list) > 1:
            if len(cur_list) % 2 == 1:
                cur_list.append(b'')
            new_list = []
            for i in range(math.ceil(len(cur_list) / 2)):
                new_list.append(self.compute(cur_list[2 * i], cur_list[2 * i + 1]))
            self.tree.append(new_list)
            cur_list = new_list


    #Computes the hash of two other hashes
    def compute(self, val1, val2):
        m = hashlib.sha256()
        m.update(val1)
        m.update(val2)
        return m.digest()
    
    #Returns the desired Merkle root
    def getRoot():
        return self.tree[-1][0]

    #Prints the computed tree
    def prettyPrint(self, nb=0):
        for i in self.tree:
            print((10 - len(i)) * ' ', i)
