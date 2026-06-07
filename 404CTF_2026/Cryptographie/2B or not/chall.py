import os
from pwn import xor

SIZE = 128
FLAG = os.environ.get("flag", "404CTF{fake_flag_for_testing}").encode()
RAW_KEY = os.environ.get("super_key", os.urandom(16).hex())
K = [int(b) for b in format(int(RAW_KEY, 16), f'0{SIZE}b')]


class Verify:
    def __init__(self, bits):
        self.k = bits
        self.n = len(bits)

    def verify_all(self):
        assert all(sum(self.k[i:i + 4]) % 2 == 1 for i in range(0, self.n, 4)), "E1"

        assert all(self.k[2 * i + 2] for i in range(self.n // 4) if not (self.k[i] == self.k[4 * i])), "E2"

        assert all(len(set(self.k[i:i + 3])) > 1 for i in range(self.n - 2)), "E3"

        assert all(sum(self.k[i:i + 8]) == 4 for i in range(self.n - 7)), "E4"

        assert all(self.k[i] ^ self.k[self.n - 1 - i] for i in range(self.n // 2)), "E5"


if __name__ == '__main__':
    try:
        v = Verify(K)
        v.verify_all()

        key_bytes = int(''.join(map(str, K)), 2).to_bytes(SIZE // 8, 'big')
        ciphertext = xor(FLAG, key_bytes)

        print(f"C: {ciphertext.hex()}")
    except AssertionError as e:
        print(f"Validation failed at {e}")
