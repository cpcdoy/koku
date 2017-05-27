#!/usr/bin/env python3

import ecdsa
import hashlib
from common.transaction import Transaction
from common.block import Block

def checkTransactions(transactions):
    for t in transactions:
        vk = t.pubkey
        sig = t.sig
        try:
            vk.verify(sig, t.getPack())
        except ecdsa.BadSignatureError:
            return False
        #TODO check amounts in the blockchain
    return True
