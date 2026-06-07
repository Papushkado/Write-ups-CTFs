from pwn import *

conn = remote('challenge.404ctf.fr', 10007)

conn.recvuntil(b'> ')

conn.sendline(b'ab')
conn.recvuntil(b'> ')
conn.sendline(b'AB')


response = conn.recvall(timeout=5)
print(response.decode())

conn.close()