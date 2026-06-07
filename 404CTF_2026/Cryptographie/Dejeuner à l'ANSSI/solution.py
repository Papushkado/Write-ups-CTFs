from pwn import *
import ast

def long_to_bytes(n):
    """Convertit un entier en bytes"""
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

print(f"[*] n = {n}")
print(f"[*] e = {e}")
print(f"[*] encrypted_flag = {encrypted_flag}")

# Attaque par propriété homomorphe de RSA
# On choisit r = 2
r = 2

# c' = encrypted_flag * r^e mod n
# Quand le serveur déchiffre c', il obtient flag * r mod n
c_prime = (encrypted_flag * pow(r, e, n)) % n

# Envoyer c_prime au serveur
conn.recvuntil(b"> ")
conn.sendline(str(c_prime).encode())

response = conn.recvline().decode().strip()
print(f"[*] Response: {response}")

if "ALERTE" in response:
    print("[-] Le filtre a détecté le flag, essayez un autre r")
    conn.close()
    exit(1)

result_line = conn.recvline().decode().strip()
print(f"[*] Result: {result_line}")

result = int(result_line)

# Retrouver le flag : flag = result * r^(-1) mod n
r_inv = pow(r, -1, n)
flag_int = (result * r_inv) % n
flag = long_to_bytes(flag_int)
print(f"[+] FLAG: {flag.decode()}")

conn.close()