# Too big or too small
easy
Auteur : clock

J'ai pas suivi mes cours de maths, la loi des grands nombres cite que plus le nombre est grand plus c'est compliqué à cracker c'est ça ?

On dispose d'un `output.txt` contenant `ct`, `N` et `e`, ainsi que du script d'encodage.

---
# Solution

Bon, on regarde le script. RSA classique sauf que N est le produit de 4000 nombres premiers consécutifs à partir d'un `k` random de 128 bits.

Premier réflexe : N est **énorme** (~512000 bits), mais composé de premiers tout petits (~125 bits chacun). Donc factorisable.

## Étape 1 : Retrouver les facteurs

L'idée c'est simple : si N = p1 × p2 × ... × p4000 avec des premiers consécutifs, alors chaque premier fait environ `log2(N) / 4000` bits. On approxime un facteur avec `N^(1/4000)`, on cherche le premier premier qui divise N autour de cette valeur, puis on déroule dans les deux directions avec `nextprime` / `prevprime`.

## Étape 2 : Déchiffrer

Là, piège. Si on fait bêtement `pow(ct, d, N)` avec un d de 512000 bits... on attend. Longtemps. **Très** longtemps.

L'astuce mathématique : le **CRT** (Théorème des Restes Chinois). Au lieu d'une exponentiation modulaire monstrueuse, on fait 4000 petites exponentiations de 125 bits chacune, puis on recombine. Des millions de fois plus rapide.

## Script final

```python
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
```

Sortie :

```
404CTF{uN_c3rvEau_v4ut_M!lL3_c4rTe5_GraPhIqU3S}
```

---

**TL;DR** : N est gros mais ses facteurs sont petits et consécutifs → on les retrouve avec `N^(1/4000)` → on déchiffre avec le CRT pour pas attendre 3 heures. La loi des grands nombres c'était un mensonge, un cerveau vaut mille cartes graphiques apparemment.

`404CTF{uN_c3rvEau_v4ut_M!lL3_c4rTe5_GraPhIqU3S}`