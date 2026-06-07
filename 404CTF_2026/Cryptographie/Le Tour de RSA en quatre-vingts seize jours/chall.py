from Crypto.Util.number import bytes_to_long,getStrongPrime 

text="......".encode('utf-8')

e=96

moduli = []
ciphers = []

def to_send(text,e,n,moduli,ciphers):
    text_long = bytes_to_long(text)
    cipher = pow(text_long,e,n)
    moduli.append(n)
    ciphers.append(cipher)

for k in range(3):
    p = getStrongPrime(1024)
    q = getStrongPrime(1024)
    n = p * q
    to_send(text,e,n,moduli,ciphers)

    q = getStrongPrime(1024)
    n = p * q
    to_send(text,e,n,moduli,ciphers)

with open("output.txt", "w") as f:
    f.write("moduli = " + f"{moduli}\n")
    f.write("ciphers = " + f"{ciphers}")
