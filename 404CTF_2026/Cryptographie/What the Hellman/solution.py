from Crypto.Util.number import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import json
from sympy import primerange, isprime
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

p_minus_1 = p - 1

# Factorisation partielle de p-1
n = p_minus_1
small_factors = {}
for small_p in primerange(2, 10**6):
    while n % small_p == 0:
        small_factors[small_p] = small_factors.get(small_p, 0) + 1
        n //= small_p
    if n == 1:
        break

cofactor = n  # partie non factorisée (383 bits)
print(f"Petits facteurs: {small_factors}")
print(f"Cofacteur restant: {cofactor.bit_length()} bits")

# Déterminer l'ordre de g=2 modulo p
# ord(g) | p-1. On teste si g^((p-1)/q) == 1 pour chaque facteur premier q
# Si oui, q ne divise PAS l'ordre de g

# Trouver l'ordre exact de g parmi les diviseurs de p-1
# On part de p-1 et on divise par les facteurs qui "marchent"
order_g = p_minus_1

for q in small_factors:
    while order_g % q == 0:
        if pow(g, order_g // q, p) == 1:
            order_g //= q
        else:
            break

if order_g % cofactor == 0:
    if pow(g, order_g // cofactor, p) == 1:
        order_g //= cofactor
        print("Le cofacteur ne divise pas l'ordre de g !")

print(f"\nOrdre de g mod p : {order_g}")
print(f"Ordre de g en bits : {order_g.bit_length()}")
print(f"Vérification pow(g, order_g, p) == 1 : {pow(g, order_g, p) == 1}")

order_factors = {}
temp = order_g
for q in sorted(small_factors.keys()):
    while temp % q == 0:
        order_factors[q] = order_factors.get(q, 0) + 1
        temp //= q

if temp > 1:
    print(f"Reste dans l'ordre: {temp} ({temp.bit_length()} bits)")
    order_factors[temp] = 1

print(f"Facteurs de ord(g): {order_factors}")

# Pohlig-Hellman sur l'ordre réel de g
def bsgs(g, h, p, n):
    m = isqrt(n) + 1
    table = {}
    power = 1
    for j in range(m):
        table[power] = j
        power = power * g % p
    factor = pow(g, -m, p)
    gamma = h
    for i in range(m):
        if gamma in table:
            return i * m + table[gamma]
        gamma = gamma * factor % p
    return None

def dlog_prime_power(g, h, p, order, q, e):
    x = 0
    gamma = pow(g, order // q, p)
    
    for k in range(e):
        gx_inv = pow(g, (-x) % order, p)
        h_k = pow(gx_inv * h % p, order // (q**(k+1)), p)
        d_k = bsgs(gamma, h_k, p, q)
        if d_k is None:
            print(f"    BSGS échoué pour q={q}, k={k}")
            return None
        x += d_k * (q**k)
    return x

remainders = []
moduli = []

for q, e in sorted(order_factors.items()):
    if q.bit_length() > 40:
        print(f"  Skip {q} (trop grand)")
        continue
    print(f"  dlog mod {q}^{e} ...", end=" ", flush=True)
    r = dlog_prime_power(g, F, p, order_g, q, e)
    print(f"→ {r}")
    if r is not None:
        remainders.append(r)
        moduli.append(q**e)

# CRT
def crt(remainders, moduli):
    M = reduce(lambda a, b: a * b, moduli)
    x = 0
    for ri, mi in zip(remainders, moduli):
        Mi = M // mi
        yi = pow(Mi, -1, mi)
        x += ri * Mi * yi
    return x % M, M

f_recovered, mod_total = crt(remainders, moduli)
print(f"\nf mod ord(g) = {f_recovered}")
print(f"Bits couverts: {mod_total.bit_length()}")
print(f"Vérification: pow(g, f_recovered, p) == F ? {pow(g, f_recovered, p) == F}")

# Secret partagé
shared_secret = pow(D, f_recovered, p)

# Déchiffrement
sha1 = hashlib.sha1()
sha1.update(str(shared_secret).encode('ascii'))
key = sha1.digest()[:16]

cipher = AES.new(key, AES.MODE_CBC, iv)
flag = unpad(cipher.decrypt(ciphertext), 16)
print(f"\nFLAG: {flag.decode()}")
