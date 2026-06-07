import json
import sys
from sympy import nextprime, prevprime
import gmpy2

sys.set_int_max_str_digits(10000000)

with open("output.txt", "r") as file:
    data = json.loads(file.read())

ct = data["ct"]
N = data["N"]
e = data["e"]

# Approximer un facteur
approx_prime = int(gmpy2.iroot(gmpy2.mpz(N), 4000)[0])

# Trouver un premier qui divise N
p = nextprime(approx_prime)
while N % p != 0:
    p = nextprime(p)

# Dérouler les 4000 facteurs consécutifs
factors = [p]
temp = p
while True:
    temp = prevprime(temp)
    if N % temp == 0:
        factors.append(temp)
    else:
        break
temp = p
while True:
    temp = nextprime(temp)
    if N % temp == 0:
        factors.append(temp)
    else:
        break

factors = sorted(set(factors))
assert len(factors) == 4000

# Déchiffrement CRT
residues = []
moduli = []
for pi in factors:
    di = pow(e, -1, pi - 1)
    mi = pow(ct % pi, di, pi)
    residues.append(int(mi))
    moduli.append(int(pi))

# Recombinaison CRT incrémentale
r = residues[0]
m = moduli[0]
for i in range(1, len(residues)):
    inv = int(gmpy2.invert(m % moduli[i], moduli[i]))
    r = r + m * ((residues[i] - r) * inv % moduli[i])
    m = m * moduli[i]
flag = (r % m).to_bytes(((r % m).bit_length() + 7) // 8, 'big')
print(flag.decode())