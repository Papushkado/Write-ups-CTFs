# Déjeuner à l'ANSSI
easy
Auteur : Lienep

Pendant la pause déjeuner, vous vous êtes introduits à l'ANSSI et avez trouvés une machine dont le but est de chiffrer des données privées. Malheureusement pour vous, un filtre empêche les données les plus sensibles d'être leakées. En plus, il faut vous dépêcher avant que les cryptologues reviennent : vous n'avez le temps de faire qu'un seul essai. Saurez vous récupérer le flag ?

---
# Solution

Bon celui-là c'était plutôt sympa, un classique de crypto RSA.

On se connecte au serveur et on récupère `n`, `e`, et le `encrypted_flag`. Le serveur nous laisse déchiffrer **un seul** message, mais refuse de nous donner le résultat si le flag apparaît dans la sortie. Classique.

Premier réflexe : on peut pas juste envoyer `encrypted_flag` directement, le filtre nous bloque. **Évidemment.**

Deuxième réflexe : RSA c'est homomorphe multiplicativement. Si on envoie `encrypted_flag * 2^e mod n`, le serveur va déchiffrer et obtenir `flag * 2 mod n`. Et ça, ça contient plus les bytes du flag directement, donc le filtre laisse passer. Ensuite on multiplie par l'inverse de 2 mod n et c'est fini.

En gros :
- `c' = encrypted_flag * 2^e mod n`
- Le serveur déchiffre : `result = flag * 2 mod n`
- Le filtre voit pas le flag dans `result` → il nous le donne
- On calcule `flag = result * 2⁻¹ mod n`

Voilà le script :

```python
from pwn import *
import ast

def long_to_bytes(n):
    if n == 0:
        return b'\x00'
    byte_length = (n.bit_length() + 7) // 8
    return n.to_bytes(byte_length, byteorder='big')

conn = remote("challenge.404ctf.fr", 10005)

conn.recvuntil(b"publiques :\n")
params_line = conn.recvline().decode().strip()
params = ast.literal_eval(params_line)
n = params["n"]
e = params["e"]
encrypted_flag = params["encrypted_flag"]

r = 2
c_prime = (encrypted_flag * pow(r, e, n)) % n

conn.recvuntil(b"> ")
conn.sendline(str(c_prime).encode())

conn.recvline()  # ligne "[SUCCÈS] ..."
result = int(conn.recvline().decode().strip())

r_inv = pow(r, -1, n)
flag_int = (result * r_inv) % n
flag = long_to_bytes(flag_int)
print(f"[+] FLAG: {flag.decode()}")

conn.close()
```

On lance, et :

```
[*] Response: [SUCCÈS] Voici le résulat du calcul :
[*] Result: 202769164067021902987280809861733790609884485085202285245375830936141265411550581544698
[+] FLAG: 404CTF{Luncht1m3_4tt4ck_b35t_4tt4ck}
```

Lunchtime attack, évidemment. Le nom du challenge aurait dû me mettre la puce à l'oreille plus tôt. Déjeuner, lunch, tout ça tout ça.

Flag : `404CTF{Luncht1m3_4tt4ck_b35t_4tt4ck}`