#!/usr/bin/env python3

from optparse import OptionParser
import ecdsa
import base58
import hashlib
from common.transaction import Transaction

def getAddr(vkey):
    m = hashlib.sha256()
    m.update(vkey.to_string())
    return base58.b58encode(m.digest())

if __name__ == "__main__":
    parser = OptionParser(description="This script is useed to interact with the Koku crypto-currency.")
    parser.add_option("-k", "--key", dest="key", help="generate a new keypair (will erease any existing in the same directory)", action="store_true", default=False)
    parser.add_option("-d", "--dest", dest="dest", help="address to send money to", metavar="STR", default="")
    parser.add_option("-A", "--amount", dest="amount", help="amount of Koku to send", metavar="INT", default=0)
    parser.add_option("-a", "--address", dest="address", help="Displays your address", action="store_true", default=False)
    args, trash = parser.parse_args()

    if args.key:
        with open('.Koku.pem', 'wb') as f:
            sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
            f.write(sk.to_pem())
            print("Key has been generated and saved under `.Koku.pem`, don't lose it!")
            addr = getAddr(sk.get_verifying_key())
            print("Your address is:", addr)
    else:
        with open('.Koku.pem', 'rb') as f:
            sk = ecdsa.SigningKey.from_pem(f.read())
            if args.address:
                addr = getAddr(sk.get_verifying_key())
                print("Your address is:", addr)
            else:
                vk = sk.get_verifying_key()
                tr = Transaction(0, getAddr(vk), getAddr(vk), vk.to_string())
                sig = sk.sign(tr.getPack())
                tr.setSig(sig)
                try:
                    vk.verify(sig, tr.getPack())
                    print("good signature")
                except ecdsa.BadSignatureError:
                    print("BAD SIGNATURE")
