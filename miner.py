#!/usr/bin/env python3

import time
import logging
from common.address import *
from common.block import Block
from daemonize import Daemonize
from optparse import OptionParser
from common.p2p2 import KokuStruct
from common.p2p2 import KokuNetwork
from common.p2p2 import KokuMessageType
from common.transaction import Transaction

pid = "/tmp/koku.pid"
sk = None
addr = ''

def main():
    logging.basicConfig(
        filename='/tmp/koku.log',
        level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s',
    )
    logging.info('Daemon is starting')
    logging.info('Daemon is using address: ' + addr)
    net = KokuNetwork('miner')
    net.broadcastMessage(KokuMessageType.GET_ADDR, [])
    logging.info('Peer is fetching addresses')
    while True:
        time.sleep(1)

if __name__ == "__main__":
    parser = OptionParser(description="This script is useed to mine the Koku crypto-currency.")
    parser.add_option("-k", "--key", dest="key", help="generate a new keypair (will erease any existing in the same directory)", action="store_true", default=False)
    args, trash = parser.parse_args()

    if args.key:
        print("Your address is:", genKey())
    else:
        with open('.Koku.pem', 'rb') as f:
            sk = ecdsa.SigningKey.from_pem(f.read())
            addr = getAddr(sk.get_verifying_key())
            daemon = Daemonize(app="koku_miner", pid=pid, action=main)
            daemon.start()
