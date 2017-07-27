#!/usr/bin/env python3

from common.address import *
from optparse import OptionParser
from common.p2p2 import KokuStruct
from common.p2p2 import KokuNetwork
from common.p2p2 import KokuMessageType
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
            else:
                vk = sk.get_verifying_key()
                tr = Transaction(int(args.amount), 0, getAddr(vk), vk)
                sig = sk.sign(tr.getPack(True))
                tr.setSig(sig)
                aux = tr.getPack()
                foo = Transaction(13, 42, getAddr(vk), vk)
                foo.unpack(aux)
                try:
                    vk.verify(sig, foo.getPack(True))
                    print("good signature")
                except ecdsa.BadSignatureError:
                    print("BAD SIGNATURE")
