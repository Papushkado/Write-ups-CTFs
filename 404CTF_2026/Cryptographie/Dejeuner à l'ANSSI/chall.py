from Crypto.PublicKey import RSA
from Crypto.Util.number import long_to_bytes
import os

def encrypt(key, pl):
    return pow(pl, key.e, key.n)

def decrypt(key, ct):
    return pow(ct, key.d, key.n)

if __name__ == "__main__":
    key = RSA.generate(2048)

    flag = os.getenv("FLAG", "404CTF{Fake_Flag}").encode()

    print("[INFO] Bienvenue dans le système interne de récupération des données. Voici les paramètres publiques :")

    print(str({
        "n": key.n,
        "e": key.e,
        "encrypted_flag": encrypt(key, int(flag.hex(), 16))
    }))

    print("[SAISIE] Veuillez entrer un message à déchiffrer :")

    try:
        userinput = int(input("> "))
    except ValueError:
        print("[ERREUR] Entrée invalide. Veuillez entrer un entier.")
        exit(1)

    result = decrypt(key, userinput)

    if flag in long_to_bytes(result):
        print("[ALERTE] Tentative d'accès à des données sensibles détectée.")
    else:
        print("[SUCCÈS] Voici le résulat du calcul :")
        print(str(result))
