import socket
from time import time
from random import randint, seed
from hashlib import sha256
from functools import reduce

def matmul(A, B):
    Bt = list(zip(*B))
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]

def genere_nombre_super_secret(n):
    A = [[randint(0, pow(2, 64)) for _ in range(n)] for _ in range(n)]
    for i in range(pow(2, 10)):
        A = matmul(A, A)
        A = [[y % pow(2, 64) for y in x] for x in A]
    base = reduce(lambda x, y: x ^ y, [reduce(lambda x, y: x ^ y, row) for row in A])
    hashed = sha256(hex(base).encode()).hexdigest()
    return int(hashed, 16)

# Étape 1 : Se connecter et noter le timestamp
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('challenge.404ctf.fr', 10200))
t = int(time())  # Le serveur a utilisé ce même timestamp (ou ±1)

# Recevoir le message d'intro
data = s.recv(4096).decode()
print(data)

# Étape 2 : Calculer le secret avec le même seed
print(f"[*] Calcul avec seed = {t} ...")
seed(t)
secret = genere_nombre_super_secret(8)
print(f"[*] Secret calculé : {secret}")

# Étape 3 : Envoyer la réponse
s.sendall((str(secret) + "\n").encode())

# Étape 4 : Recevoir la réponse
response = s.recv(4096).decode()
print(response)

s.close()