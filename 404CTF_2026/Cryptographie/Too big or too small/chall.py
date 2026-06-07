from sympy import nextprime 
import random
import json
import sys

sys.set_int_max_str_digits(10000000)

flag = b"404CTF{???????????????????????????????????????}"
k = random.randint(1,2**128)
N = 1

for _ in range(4000):
    k = nextprime(k)
    N *= k

e = 0x10001

ct = pow(int.from_bytes(flag), e, N)

with open("output.txt", "w") as file:
    file.write(json.dumps({"ct": ct, "N": N, "e": e}))
