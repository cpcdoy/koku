#!/usr/bin/env python3

import os
import time
import signal
import pickle
import logging
from common.address import *
from common.block import Block
from daemonize import Daemonize
from optparse import OptionParser
from common.p2p2 import KokuStruct
from common.block import checkChain
from common.p2p2 import KokuNetwork
from common.p2p2 import KokuMessageType
from common.transaction import Transaction
from gpu.gpu_miner import gpu_miner

pid = "/tmp/koku.pid"
sk = None
addr = ''
chain = [ Block(b'', b'', 0) ]
net = None
logger = None
miner = None

def getInitTransactions(vk, sk):
    tr = Transaction(10, 0, getAddr(vk), vk)
    #We do that because this transaction is the reward
    tr.sender = b''
    #We don't sign it bc no signature is needed
    return [tr]

def main():

    try:
        with open('/tmp/.koku.chain', 'r') as cfile:
            chain = pickle.load(cfile)
            logger.info("Chain found until block #" + str(chain[-1].id))
    except Exception as inst:
        logger.exception("Koku blockchain file not found")
        logger.error(type(inst))
        logger.error((inst.args))

    miner = gpu_miner(logger)
    net = KokuNetwork('miner', logger, chain, miner)
    #time.sleep(3)
    net.broadcastMessage(KokuMessageType.GET_ADDR, [])
    #time.sleep(3)
    net.broadcastMessage(KokuMessageType.GET_FROM_LAST, chain[-1].id)
    #J'ai ajouté logging ici pour que le network puisse en faire. C'est dans /tmp/koku.log
    #Ici il faut récupérer pleins de peers, je pense que c'est bon.
    #while not updateChain(net):
    #    logging.error('An error in the downloaded chain has been detected!')

    vk = sk.get_verifying_key()

    while True:
        try:
            transactions = getInitTransactions(vk, sk)
            newBlock = Block(chain[-1].getHash(), b'', len(chain))
            newBlock.setTransactions(transactions)

            miner.set_block(newBlock)
            nounce, fresh = miner.compute_hashes()
            if fresh:
                chain.append(nounce)
                net.broadcastMessage(KokuMessageType.FROM_LAST, [nounce])
                with open('/tmp/.koku.chain', 'w') as f:
                    dump = pickle.dumps(self.chain)
                    f.write(dump)

        except Exception as inst:
            logger.exception("Main loop exception")
            logger.error(type(inst))
            logger.error((inst.args))

if __name__ == "__main__":
    parser = OptionParser(description="This script is useed to mine the Koku crypto-currency. The logs are located in /tmp/koku.log")
    parser.add_option("-k", "--key", dest="key", help="generate a new keypair (will erease any existing in the same directory)", action="store_true", default=False)
    parser.add_option("-s", "--stop", dest="stop", help="stops the daemon", action="store_true", default=False)
    args, trash = parser.parse_args()

    if args.key:
        print("Your address is:", genKey())
    else:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        fh = logging.FileHandler('/tmp/koku.log', 'a')
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        keep_fds = [fh.stream.fileno()]

        daemon = Daemonize(app="koku_miner", pid=pid, action=main, keep_fds=keep_fds)
        if args.stop:
            with open(pid, 'r') as f:
                os.kill(int(f.read()), signal.SIGTERM)
                logger.info('Daemon stopped')
        else:
            with open('.Koku.pem', 'rb') as f:
                kernelFile = open('gpu/chady256.cl', 'r')
                sk = ecdsa.SigningKey.from_pem(f.read())
                addr = getAddr(sk.get_verifying_key())
                logger.info('Daemon is starting')
                logger.info('Daemon is using address: ' + addr)
                daemon.start()
