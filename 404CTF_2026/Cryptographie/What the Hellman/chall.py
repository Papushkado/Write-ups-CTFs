from Crypto.Util.number import * 
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json

FLAG = os.getenv("FLAG", "404CTF{fakeflag}").encode()

def encrypt_flag(shared_secret: int):
    # Derive AES key from shared secret
    sha1 = hashlib.sha1()
    sha1.update(str(shared_secret).encode('ascii'))
    key = sha1.digest()[:16]
    # Encrypt flag
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(FLAG, 16))
    # Prepare data to send
    data = {}
    data['iv'] = iv.hex()
    data['encrypted_flag'] = ciphertext.hex()
    return data

file = open("output.txt", "w")

p = 13612606613985599256675278930068094538579224531235420791577034083547284094867111104869648580521710726604431822112579082474246451334033675308157542753240096037402065211066447540112253463
g = 2


# Descartes choisit sa clé privée et calcule sa clé publique
mdp_descartes = b"???????????????????"
d = bytes_to_long(hashlib.sha256(mdp_descartes).digest())
D = pow(g, d, p)

file.write("Descartes envoie les paramètres ainsi que sa clé publique : " + json.dumps({"p": hex(p), "g": hex(g), "D": hex(D)}) + "\n")

# Fermat choisit sa clé privée et calcule sa clé publique
mdp_fermat = b"????????????????????????"
f = bytes_to_long(hashlib.sha1(mdp_fermat).digest())
F = pow(g, f, p)

file.write("Fermat envoie sa clé publique : " + json.dumps({"F": hex(F)}) + "\n")


# Chacun calcul le secret caché de son côté
shared_secret_Descartes = pow(F, d, p)
shared_secret_Fermat = pow(D, f, p)

assert shared_secret_Descartes == shared_secret_Fermat

shared_secret = shared_secret_Descartes

file.write(json.dumps(encrypt_flag(shared_secret)) + "\n")
