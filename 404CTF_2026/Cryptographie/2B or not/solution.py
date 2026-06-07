from itertools import product
from pwn import xor

SIZE = 128
ciphertext = bytes.fromhex("868286f1e6f4c9e182dff7c683ffd796ed80eddfe7f186ed83c1ed8582fdedffc7f1dacf")

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