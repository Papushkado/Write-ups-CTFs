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
    return None

SECRET = b'server_secret'
def make_token(uid, cid):
    data = f"{uid}:{cid}".encode()
    h = hmac.new(SECRET, data, hashlib.sha256).hexdigest()
    return f"{uid}:{cid}:{h}"

io = remote('challenge.404ctf.fr', 10006)
io.recvuntil(b'name):')
io.sendline(b'pwn')
io.recvuntil(b'Choice:')
io.sendline(b'4')
io.recvuntil(b'Access token:')
io.sendline(make_token(0, 0).encode())   # token forgé pour admin sur chat 0
raw = io.recvuntil(b'Choice:').decode()

# extraction du JSON
s = raw.index('{')
# trouver la fin du JSON (compter les accolades)
depth = 0
for i, c in enumerate(raw[s:], start=s):
    if c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            e = i+1; break
blob = json.loads(raw[s:e])

n  = int(blob['rsa_public_key']['n'], 16)
e_ = int(blob['rsa_public_key']['e'], 16)
wrapped = bytes.fromhex(blob['wrapped_aes_key'])
ct      = bytes.fromhex(blob['encrypted_flag'])

print("[*] Factorisation...")
p, q = factor(n)
print(f"[+] p trouvé ({p.bit_length()} bits)")

d = inverse(e_, (p-1)*(q-1))
rsa = RSA.construct((n, e_, d, p, q))
aes_key = PKCS1_OAEP.new(rsa).decrypt(wrapped)
print(f"[+] AES key: {aes_key.hex()}")

# Plaintext JSON connu (structure exacte produite par json.dumps)
prefix = b'[{"from": 0, "msg": "Did you store the secret safely?"}, ' \
         b'{"from": 1, "msg": "Yes. IV discarded after sealing."}, ' \
         b'{"from": 0, "msg": "Perfect. Here it is: '
suffix = b'"}, {"from": 1, "msg": "Vault sealed. End-to-end encrypted."}]'

# Bloc 0 (offsets 0..15) entièrement connu → keystream du bloc 1 du CTR
ks_block1 = bytes(a^b for a,b in zip(prefix[:16], ct[:16]))
ecb = AES.new(aes_key, AES.MODE_ECB)
counter_1 = ecb.decrypt(ks_block1)   # = inc32(J0)

# Génération du keystream complet
def ctr(i):
    base = counter_1[:12]
    v = struct.unpack('>I', counter_1[12:])[0]
    return base + struct.pack('>I', (v + (i-1)) & 0xFFFFFFFF)

nblk = (len(ct) + 15)//16
ks = b''.join(ecb.encrypt(ctr(i)) for i in range(1, nblk+1))[:len(ct)]
pt = bytes(a^b for a,b in zip(ct, ks))
print("[+] Plaintext :", pt)

# Vérification + extraction flag
assert pt.startswith(prefix) and pt.endswith(suffix)
flag = pt[len(prefix):-len(suffix)]
print("[FLAG]", flag.decode())

io.close()