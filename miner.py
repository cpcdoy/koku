#!/usr/bin/env python3

import daemon
from common.address import *
from common.block import Block
from optparse import OptionParser
from common.p2p2 import KokuStruct
from common.p2p2 import KokuNetwork
from common.p2p2 import KokuMessageType
from common.transaction import Transaction

def miner():
    sk = ecdsa.SigningKey.from_pem(f.read())
    addr = getAddr(sk.get_verifying_key())
    net = KokuNetwork('miner')
    net.broadcastMessage(KokuMessageType.GET_ADDR, [])

if __name__ == "__main__":
    parser = OptionParser(description="This script is useed to mine the Koku crypto-currency.")
    parser.add_option("-k", "--key", dest="key", help="generate a new keypair (will erease any existing in the same directory)", action="store_true", default=False)
    args, trash = parser.parse_args()

    if args.key:
        print("Your address is:", genKey())
    else:
        with daemon.DaemonContext():
            miner()
