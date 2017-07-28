#!/usr/bin/env python3

import os
import sys
import pickle
import logging
from common.address import *
from optparse import OptionParser
from common.p2p2 import KokuStruct
from common.p2p2 import KokuNetwork
from common.p2p2 import KokuMessageType
from common.block import getAmountAvailable
from common.transaction import Transaction

if __name__ == "__main__":
    parser = OptionParser(description="This script is useed to interact with the Koku crypto-currency.")
    parser.add_option("-k", "--key", dest="key", help="generate a new keypair (will erease any existing in the same directory)", action="store_true", default=False)
    parser.add_option("-d", "--dest", dest="dest", help="address to send money to", metavar="STR", default="")
    parser.add_option("-A", "--amount", dest="amount", help="amount of Koku to send", metavar="INT", default=0)
    parser.add_option("-a", "--address", dest="address", help="Displays your address", action="store_true", default=False)
    args, trash = parser.parse_args()

    if args.key:
        print("Your address is:", genKey())
    else:
        with open('.Koku.pem', 'rb') as f:
            sk = ecdsa.SigningKey.from_pem(f.read())
            if args.address:
                addr = getAddr(sk.get_verifying_key())
                print("Your address is:", addr)
            elif int(args.amount) > 0:
                chain = []
                if os.path.exists('/tmp/.koku.chain'):
                    with open('/tmp/.koku.chain', 'rb') as cfile:
                        chain = pickle.load(cfile)
                else:
                    chain = [ Block(b'', b'', 0) ]

                logger = logging.getLogger(__name__)
                logger.setLevel(logging.DEBUG)
                logger.propagate = False
                fh = logging.StreamHandler(sys.stdout)
                fh.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
                fh.setFormatter(formatter)
                logger.addHandler(fh)

                net = KokuNetwork('client', logger, chain, None)
                net.broadcastMessage(KokuMessageType.GET_FROM_LAST, chain[-1].id)
                net.broadcastMessage(KokuMessageType.GET_TRANSACTION, [])

                net.waiting_for_transactions = True
                while net.waiting_for_transactions:
                    time.sleep(1)
                
                trans = net.transactions

                vk = sk.get_verifying_key()

                ######## TODO Remove this
                for b in chain:
                    b.setTransactions(trans[b.id])
                ########
                amount = getAmountAvailable(getAddr(vk), chain)
                if amount - int(args.amount) < 0:
                    logger.error('You don\'t have enough money...')
                    sys.exit(1)

                tr = Transaction(int(args.amount), amount - int(args.amount), args.dest, vk)
                sig = sk.sign(tr.getPack(True))
                tr.setSig(sig)
                #net.broadcastMessage(KokuMessageType.SEND_TRANSACTION, [tr])
