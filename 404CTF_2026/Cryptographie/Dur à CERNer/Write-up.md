# Dur à CERNer
100 - intro
Auteur : Lienep

---

# Solution

On se connecte au serveur et on nous demande d'entrer deux "particules" en hexadécimal. Le but : provoquer une collision SHA-256, c'est-à-dire trouver deux inputs différents qui produisent le même hash.

Bon, une vraie collision SHA-256... on n'est pas là pour casser la cryptographie moderne non plus. Il y a forcément une astuce.

Je regarde le code source :

```python
if particule_a == particule_b:
    print("Une seule particule ne peut pas produire de collisions !")
    exit(1)
```

OK donc les deux **strings** doivent être différentes.

```python
sha256.update(bytes.fromhex(particule_a))
```

Et là, tout devient évident : `bytes.fromhex()` est **case-insensitive**.

- `"ab"` et `"AB"` → strings différentes ✓
- `bytes.fromhex("ab")` et `bytes.fromhex("AB")` → même bytes `b'\xab'` ✓
- Même bytes → même SHA-256 ✓

Voilà, c'est tout. Pas besoin de casser quoi que ce soit, juste de lire la doc Python.

---

# Exploit

```python
from pwn import *

conn = remote('challenge.404ctf.fr', 10007)

conn.recvuntil(b'> ')
conn.sendline(b'ab')

conn.recvuntil(b'> ')
conn.sendline(b'AB')

response = conn.recvall(timeout=5)
print(response.decode())

conn.close()
```

On lance, et hop :

```
Accélérateur de particules en cours...
Bien joué ! Voici le résultat de l'analyse des données :
404CTF{P4rt1cl35_g0_brrrrrrrrr!}
```

---

Honnêtement, celui-là m'a pris plus de temps que je ne voudrais l'admettre. J'étais parti à chercher des collisions SHA-256 partielles, des attaques birthday, **rien**. Et puis j'ai relu le code une deuxième fois et... `bytes.fromhex`. Majuscules/minuscules. Voilà.

Le CERN peut dormir tranquille, la crypto n'est pas cassée.