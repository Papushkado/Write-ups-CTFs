# 5 Ronisés
intro
Écrit par Lienep

On va jouer à un petit jeu... Arriveras-tu à gagner contre ma génération hyper-sécurisée ?

nc challenge.404ctf.fr 10200

---
# Solution

Ce challenge, c'est du classique : un serveur qui te demande de deviner un nombre "super secret". Sauf que le secret est aussi secret que mon code WiFi en 2012.

On regarde le code source :

```python
def set_seed():
    seed(int(time()))
```

Ah. Le seed c'est juste `int(time())`. Le timestamp actuel. Magnifique.

Le flow du serveur :
1. Il seed le RNG avec le timestamp
2. Il nous demande de deviner
3. **Après** notre réponse, il calcule le nombre secret

Donc le seed est fixé **avant** qu'on réponde. Si on connaît le timestamp du serveur (spoiler : c'est le même que le nôtre à ±1 seconde), on peut reproduire tout le calcul localement.

Le "nombre super secret" c'est :
- Une matrice 8×8 de randint
- Élevée au carré 1024 fois (mod 2^64)
- XOR de tous les éléments
- SHA256 du résultat

Impressionnant sur le papier. Inutile si le seed est prévisible.

---

Script d'exploit :

```python
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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('challenge.404ctf.fr', 10200))
t = int(time())

data = s.recv(4096).decode()
print(data)

print(f"[*] Calcul avec seed = {t} ...")
seed(t)
secret = genere_nombre_super_secret(8)
print(f"[*] Secret calculé : {secret}")

s.sendall((str(secret) + "\n").encode())

response = s.recv(4096).decode()
print(response)

s.close()
```

On lance, ça mouline quelques secondes (1024 multiplications de matrices en Python pur, faut pas être pressé), et :

```
On va jouer à un jeu. Devine mon nombre secret et je te donne le flag !
> 
[*] Calcul avec seed = 1779039404 ...
[*] Secret calculé : 98874076714931857676814367883777088097572723265906488308014765254768757189562
Wow ! Voici le flag : 404CTF{J0l1_T1m1ng!}
```

Premier essai. "Hyper-sécurisée" qu'ils disaient.

Le flag est : `404CTF{J0l1_T1m1ng!}`