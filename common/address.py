import ecdsa
import base58
import hashlib

def getAddr(vkey):
    m = hashlib.sha256()
    m.update(vkey.to_string())
    return base58.b58encode(m.digest())

def genKey():
    with open('.Koku.pem', 'wb') as f:
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        f.write(sk.to_pem())
        print("Key has been generated and saved under `.Koku.pem`, don't lose it!")
        return getAddr(sk.get_verifying_key())
