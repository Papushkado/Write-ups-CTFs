# What the Hellman
easy
Auteur : ?

Descartes et Fermat se sont fait reverse regressioned dans le présent mais ne maîtrisent pas encore toutes les technologies modernes. Montrez leur que ce n'était pas une bonne idée d'utiliser des mots de passes pour le protocole Diffie-Hellman.

P.S : Les mots de passes ont été générés avec os.urandom.

---
# Solution

On a un échange Diffie-Hellman classique avec `g=2`, un premier `p`, et on nous donne les clés publiques `D` et `F` ainsi qu'un flag chiffré en AES-CBC dérivé du secret partagé.

Le hint c'est "clock" et "hellman" → **Pohlig-Hellman**. L'idée c'est que si `p-1` est smooth (composé de petits facteurs), le logarithme discret est trivial.

## Première tentative : factoriser p-1

Je lance `sympy.factorint(p-1)` et... ça tourne indéfiniment. Bon.

Plan B : division par petits premiers jusqu'à 10^6. Résultat :

```
Petits facteurs: {2, 11, 13, 43, 109, 409, 499, 541, 907, 2579, 2887, 3607, 3847, 4373, 5737, 23819, 27551, 34361, 356561, 457673, 555767}
Cofacteur restant: 383 bits (non factorisé)
```

Le produit des petits facteurs fait 229 bits, `f` (SHA1) fait 160 bits. Donc en théorie on a assez de bits pour retrouver `f` par CRT... **sauf que la vérification échoue** : `pow(g, f_recovered, p) != F`.

## Le déclic

Le problème : je faisais du Pohlig-Hellman par rapport à `p-1`, mais `g=2` **n'est pas forcément un générateur** de `(Z/pZ)*` ! Son ordre est un diviseur de `p-1`, pas nécessairement `p-1` tout entier.

L'astuce : on calcule l'**ordre réel** de `g` modulo `p`. Pour chaque facteur premier `q` de `p-1`, si `g^((p-1)/q) ≡ 1 mod p`, alors `q` ne divise pas l'ordre de `g`.

Et là, magie : le cofacteur de 383 bits **ne divise pas** l'ordre de `g` ! Donc l'ordre de `g` ne contient que les petits facteurs qu'on a déjà trouvés → Pohlig-Hellman est exact et instantané.


## Script final

```python
from Crypto.Util.number import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import json
from sympy import primerange
from math import isqrt
from functools import reduce

with open("output.txt", "r") as file:
    lines = file.readlines()

params = json.loads(lines[0].split(": ", 1)[1])
p = int(params["p"], 16)
g = int(params["g"], 16)
D = int(params["D"], 16)

fermat_data = json.loads(lines[1].split(": ", 1)[1])
F = int(fermat_data["F"], 16)

enc_data = json.loads(lines[2])
iv = bytes.fromhex(enc_data["iv"])
ciphertext = bytes.fromhex(enc_data["encrypted_flag"])

# Factorisation partielle de p-1
n = p - 1
small_factors = {}
for sp in primerange(2, 10**6):
    while n % sp == 0:
        small_factors[sp] = small_factors.get(sp, 0) + 1
        n //= sp
    if n == 1:
        break
cofactor = n

# Ordre réel de g : on retire les facteurs "inutiles"
order_g = p - 1
for q in small_factors:
    while order_g % q == 0:
        if pow(g, order_g // q, p) == 1:
            order_g //= q
        else:
            break
if order_g % cofactor == 0:
    if pow(g, order_g // cofactor, p) == 1:
        order_g //= cofactor

# Factoriser l'ordre de g
order_factors = {}
temp = order_g
for q in sorted(small_factors.keys()):
    while temp % q == 0:
        order_factors[q] = order_factors.get(q, 0) + 1
        temp //= q

# Pohlig-Hellman
def bsgs(g, h, p, n):
    m = isqrt(n) + 1
    table = {}
    pw = 1
    for j in range(m):
        table[pw] = j
        pw = pw * g % p
    factor = pow(g, -m, p)
    gamma = h
    for i in range(m):
        if gamma in table:
            return i * m + table[gamma]
        gamma = gamma * factor % p

def dlog_prime_power(g, h, p, order, q, e):
    x = 0
    gamma = pow(g, order // q, p)
    for k in range(e):
        gx_inv = pow(g, (-x) % order, p)
        h_k = pow(gx_inv * h % p, order // (q**(k+1)), p)
        x += bsgs(gamma, h_k, p, q) * (q**k)
    return x

remainders, moduli = [], []
for q, e in sorted(order_factors.items()):
    r = dlog_prime_power(g, F, p, order_g, q, e)
    remainders.append(r)
    moduli.append(q**e)

# CRT
M = reduce(lambda a, b: a * b, moduli)
f_recovered = sum(r * (M // m) * pow(M // m, -1, m) for r, m in zip(remainders, moduli)) % M

# Déchiffrement
shared_secret = pow(D, f_recovered, p)
sha1 = hashlib.sha1()
sha1.update(str(shared_secret).encode('ascii'))
key = sha1.digest()[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
flag = unpad(cipher.decrypt(ciphertext), 16)
print(flag.decode())
```

Flag `404{sM0otH_w4y_oF_s0lV!ng}`