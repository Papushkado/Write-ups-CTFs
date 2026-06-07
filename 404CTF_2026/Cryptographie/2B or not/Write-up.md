# 2B or not to be
easy
Auteur : Layzix

Inspiré par les travaux de Blaise Pascal sur la statique des fluides, votre mentor a conçu un système cryptographique en quête d'un équilibre parfait. Pour garantir la robustesse de ses clés, il a instauré cinq règles rigoureuses que chaque bit doit satisfaire. Il est convaincu que cette complexité structurelle rend son secret inviolable. Montrez lui que vous n'êtes absolument pas démuni face à sa logique.

On nous fournit un ciphertext et le code serveur qui génère la clé.

---
# Solution

Ce challenge a l'air intimidant avec ses 5 contraintes, mais en réalité une seule d'entre elles casse tout le système.

## Analyse des contraintes

On a une clé de 128 bits soumise à 5 règles :

- **E1** : Chaque bloc de 4 bits (non-chevauchant) a une somme impaire
- **E2** : Une condition conditionnelle sur certains bits
- **E3** : Pas trois bits consécutifs identiques (pas de `000` ni `111`)
- **E4** : Toute fenêtre glissante de 8 bits consécutifs somme à exactement 4
- **E5** : Chaque bit est l'inverse de son miroir (`k[i] ≠ k[127-i]`)

## L'observation qui tue

**E4** est la contrainte la plus restrictive. Si `sum(k[i:i+8]) = 4` et `sum(k[i+1:i+9]) = 4`, alors par soustraction : `k[i] = k[i+8]`.

Donc **la clé est périodique de période 8**. 128 bits déterminés par seulement 8 bits. Voilà voilà.

Du coup on passe de 2¹²⁸ possibilités à... C(8,4) = 70. Magnifique robustesse.

## Brute force des 70 candidats

On filtre avec les autres contraintes (E1, E2, E3, E5) et il ne reste quasiment rien :

```python
from itertools import product
from pwn import xor

SIZE = 128
ciphertext = bytes.fromhex("CIPHERTEXT_ICI")

n = SIZE
for first8 in product([0,1], repeat=8):
    if sum(first8) != 4:
        continue
    
    K = list(first8) * 16
    
    # E3 : pas trois consécutifs identiques
    if any(len(set(K[i:i+3])) == 1 for i in range(n-2)):
        continue
    
    # E5 : k[i] != k[127-i]
    if not all(K[i] ^ K[n-1-i] for i in range(n//2)):
        continue
    
    # E1 : somme impaire par bloc de 4
    if not all(sum(K[i:i+4]) % 2 == 1 for i in range(0, n, 4)):
        continue
    
    # E2
    ok = True
    for i in range(n//4):
        if 4*i < n and not (K[i] == K[4*i]):
            if 2*i+2 < n and not K[2*i+2]:
                ok = False
                break
    if not ok:
        continue
    
    key_bytes = int(''.join(map(str, K)), 2).to_bytes(SIZE//8, 'big')
    plaintext = xor(ciphertext, key_bytes)
    
    if b"404CTF" in plaintext:
        print(f"FLAG: {plaintext.decode()}")
        print(f"Motif de 8 bits: {''.join(map(str, first8))}")
```

## Résultat

```
FLAG: 404CTF{S0mEt1Me$_2_mUC4_1s_70O_MuCh}
```

Le mentor pensait que 5 contraintes = sécurité. En réalité, E4 réduit l'espace à 70 clés, et les autres contraintes ne font que confirmer l'unicité. Un beau cas où trop de structure dans une clé la rend triviale à retrouver.

**"L'équilibre parfait" de Pascal, c'est joli, mais en crypto c'est une catastrophe.**