# CHAesT
medium
Auteur : Layzix

Pour sécuriser les communications stratégiques des chercheurs de l'institut, un développeur un peu trop confiant a mis au point VaultChat, une application de messagerie à première vue solide mais qui cache plus d'un flop. À vous d'enchaîner de petites pirouhettes pour lui montrer l'étendu de son erreur.

`nc challenge.404ctf.fr 10006`

---
# Solution

Le nom du challenge donne déjà le ton : **CHA**es**T**. Trois lettres en majuscules qui sentent la triche à plein nez. Et effectivement, en lisant le code du serveur on tombe sur **trois failles** à enchaîner comme des petites pirouhettes 🐔.

## Faille n°1 : le secret HMAC qui n'en est pas un

Pour accéder à un chat, il faut un access token signé avec `_session_secret`. Regardons comment ce secret est généré :

```python
self._session_secret = os.urandom(32) and b'server_secret'
```

Et là, _patatra c'est le drame_ : en Python, l'opérateur `and` est court-circuité. Si la première opérande est *truthy* (et 32 octets aléatoires non-nuls le sont quasiment toujours), alors l'expression renvoie la **deuxième** opérande. 

Donc :
```python
>>> os.urandom(32) and b'server_secret'
b'server_secret'
```

Le "secret" du serveur est littéralement `b'server_secret'`. On peut donc forger n'importe quel token d'accès, y compris celui de l'admin sur le chat qui contient le flag (`uid=0, cid=0`) :

```python
def make_token(uid, cid):
    data = f"{uid}:{cid}".encode()
    h = hmac.new(b'server_secret', data, hashlib.sha256).hexdigest()
    return f"{uid}:{cid}:{h}"
```

✅ On peut maintenant récupérer le blob chiffré du chat admin↔flag_bot.

## Faille n°2 : RSA mal généré, factorisable en 2 secondes

On a le blob, mais la clé AES est _wrappée_ avec la clé publique RSA de l'admin (PKCS1-OAEP). Il faut donc casser RSA. Heureusement, le code de génération est... particulier :

```python
def _gen_key(self):
    seed = int.from_bytes(os.urandom(64), 'big') | (1 << 511) | 1
    p = int(nextprime(seed))
    q = int(nextprime(p + M))   # <-- M = primoriel des 100 premiers premiers
```

Donc `q = p + M + δ` où δ est un petit gap entre nombres premiers (quelques centaines à quelques milliers).

En posant cette relation dans `n = p·q` :

$$n = p(p + M + \delta) \iff p^2 + p(M+\delta) - n = 0$$

C'est une équation du second degré en `p`. Pour qu'elle ait une solution entière, il faut que le discriminant `(M+δ)² + 4n` soit un carré parfait. On brute-force δ :

```python
def factor(n):
    for delta in range(1, 500000):
        s = (M+delta)**2 + 4*n
        r = isqrt(s)
        if r*r == s:
            p = (-(M+delta) + r) // 2
            if n % p == 0:
                return p, n//p
```

Bingo, en quelques milliers d'itérations on a `p` et `q` ==> La clef AES est tombée :)

## Faille n°3 : AES-GCM sans IV mais... avec plaintext connu

On a la clé AES, on a le ciphertext, on a le tag... mais le serveur **ne donne pas l'IV** (`"iv": None` dans le blob). _"IV discarded after sealing"_ comme le dit si bien flag_bot dans le chat. 

Sans IV, AES-GCM est censé être indéchiffrable. **Sauf que** :

1. AES-GCM = AES-CTR sous le capot pour le chiffrement.
2. Le plaintext est un JSON dont on connaît **toute la structure** sauf le flag :

```python
chat.add(admin,   "Did you store the secret safely?")
chat.add(flagbot, "Yes. IV discarded after sealing.")
chat.add(admin,   f"Perfect. Here it is: {FLAG}")
chat.add(flagbot, "Vault sealed. End-to-end encrypted.")
```

Le plaintext commence donc par `[{"from": 0, "msg": "Did you store the secret safely?"}, ...`

Le **bloc 0** (16 premiers octets) est entièrement connu. On peut donc en extraire le **keystream** :

```python
ks_block1 = bytes(a^b for a,b in zip(prefix[:16], ct[:16]))
```

Et là, _illumination_ : en mode CTR, `keystream_i = AES_encrypt(key, counter_i)`. Donc en **déchiffrant en ECB** ce keystream avec la clé AES, on récupère le compteur du bloc 1 :

```python
counter_1 = AES.new(aes_key, AES.MODE_ECB).decrypt(ks_block1)
```

Connaissant un compteur, on connaît tous les autres (il suffit d'incrémenter les 4 derniers octets). On régénère donc tout le keystream et on XOR avec le ciphertext


## Le code final

```python
from pwn import remote
import json, hmac, hashlib, struct
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.number import inverse
from math import isqrt

FIRST_100_PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,
101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,
223,227,229,233,239,241,251,257,263,269,271,277,281,283,293,307,311,313,317,331,337,347,
349,353,359,367,373,379,383,389,397,401,409,419,421,431,433,439,443,449,457,461,463,467,
479,487,491,499,503,509,521,523,541]
M = 1
for x in FIRST_100_PRIMES: M *= x

def factor(n):
    for delta in range(1, 500000):
        s = (M+delta)**2 + 4*n
        r = isqrt(s)
        if r*r == s:
            p = (-(M+delta) + r) // 2
            if p > 1 and n % p == 0:
                return p, n//p

SECRET = b'server_secret'
def make_token(uid, cid):
    data = f"{uid}:{cid}".encode()
    h = hmac.new(SECRET, data, hashlib.sha256).hexdigest()
    return f"{uid}:{cid}:{h}"

io = remote('challenge.404ctf.fr', 10006)
io.recvuntil(b'name):'); io.sendline(b'pwn')
io.recvuntil(b'Choice:'); io.sendline(b'4')
io.recvuntil(b'Access token:'); io.sendline(make_token(0, 0).encode())
raw = io.recvuntil(b'Choice:').decode()

# extraction du JSON
s = raw.index('{'); depth = 0
for i, c in enumerate(raw[s:], start=s):
    if c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0: e = i+1; break
blob = json.loads(raw[s:e])

n = int(blob['rsa_public_key']['n'], 16)
e_= int(blob['rsa_public_key']['e'], 16)
wrapped = bytes.fromhex(blob['wrapped_aes_key'])
ct      = bytes.fromhex(blob['encrypted_flag'])

p, q = factor(n)
d = inverse(e_, (p-1)*(q-1))
rsa = RSA.construct((n, e_, d, p, q))
aes_key = PKCS1_OAEP.new(rsa).decrypt(wrapped)

prefix = b'[{"from": 0, "msg": "Did you store the secret safely?"}, ' \
         b'{"from": 1, "msg": "Yes. IV discarded after sealing."}, ' \
         b'{"from": 0, "msg": "Perfect. Here it is: '
suffix = b'"}, {"from": 1, "msg": "Vault sealed. End-to-end encrypted."}]'

ks_block1 = bytes(a^b for a,b in zip(prefix[:16], ct[:16]))
ecb = AES.new(aes_key, AES.MODE_ECB)
counter_1 = ecb.decrypt(ks_block1)

def ctr(i):
    base = counter_1[:12]
    v = struct.unpack('>I', counter_1[12:])[0]
    return base + struct.pack('>I', (v + (i-1)) & 0xFFFFFFFF)

nblk = (len(ct) + 15)//16
ks = b''.join(ecb.encrypt(ctr(i)) for i in range(1, nblk+1))[:len(ct)]
pt = bytes(a^b for a,b in zip(ct, ks))

flag = pt[len(prefix):-len(suffix)]
print("[FLAG]", flag.decode())
```

## Anecdote 

J'ai longtemps hésité en voyant que le flag interne était un hash de 64 caractères hex, persuadé qu'il fallait encore le décoder. _Et puis non_ : le code source est explicite, `chat.add(admin, f"Perfect. Here it is: {FLAG}")` insère bien la variable d'environnement `FLAG` telle quelle. Le hash, c'est juste pour qu'on ne devine pas le flag à l'avance 🙃.

Le flag est : `404CTF{07aafdab5919b7a013b45466d0d18e87c29fa2e4953d767e55275ebc0c5396aa}`