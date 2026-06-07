import os, json, hmac, hashlib
from sympy import nextprime
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.number import inverse

FLAG = os.getenv('FLAG') or '404CTF{Fake_flag_for_testing_purposes}'
FIRST_100_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
                    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
                    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
                    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
                    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
                    509, 521, 523, 541]


def _primorial():
    p = 1
    for x in FIRST_100_PRIMES: p *= x
    return p


M = _primorial()


def aes_gcm_encrypt(key: bytes, iv: bytes, plaintext: bytes, aad: bytes = b'') -> tuple:
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    cipher.update(aad)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return ciphertext, tag


class User:
    def __init__(self, uid: int, name: str):
        self.id = uid
        self.name = name
        self.rsa_key = None
        self._gen_key()

    def _gen_key(self):
        seed = int.from_bytes(os.urandom(64), 'big') | (1 << 511) | 1
        p = int(nextprime(seed))
        q = int(nextprime(p + M))
        n = p * q
        e = 65537
        d = inverse(e, (p - 1) * (q - 1))
        self.rsa_key = RSA.construct((n, e, d, p, q))

    def pub(self) -> tuple[int, int]:
        return self.rsa_key.n, self.rsa_key.e

    def wrap(self, aes_key: bytes) -> bytes:
        cipher = PKCS1_OAEP.new(self.rsa_key.publickey())
        return cipher.encrypt(aes_key)

    def unwrap(self, wrapped: bytes) -> bytes:
        cipher = PKCS1_OAEP.new(self.rsa_key)
        return cipher.decrypt(wrapped)


class Chat:
    def __init__(self, u1: User, u2: User):
        self.u1 = u1
        self.u2 = u2
        self.messages = []

        self._key = os.urandom(32)
        self._wk1 = u1.wrap(self._key)
        self._wk2 = u2.wrap(self._key)
        self._iv = os.urandom(12)
        self._ct = self._tag = None

    def add(self, sender: User, text: str):
        self.messages.append((sender.id, text))

    def seal(self):
        pt = json.dumps([{"from": s, "msg": m} for s, m in self.messages]).encode()
        aad = f"chat:{self.u1.id}:{self.u2.id}".encode()
        self._ct, self._tag = aes_gcm_encrypt(self._key, self._iv, pt, aad)

    def blob(self, uid: int) -> dict[str, dict[str, str] | str]:
        match uid:
            case self.u1.id:
                wk = self._wk1
                n, e = self.u1.pub()
            case self.u2.id:
                wk = self._wk2
                n, e = self.u2.pub()
            case _:
                raise PermissionError("not a participant")
        return {"rsa_public_key": {"n": hex(n), "e": hex(e)},
                "wrapped_aes_key": wk.hex(),
                "encrypted_flag": self._ct.hex(),
                "auth_tag": self._tag.hex(),
                "iv": None,
                "aad": f"chat:{self.u1.id}:{self.u2.id}"}


class Server:
    def __init__(self):
        self._users = {}
        self._chats = {}
        self._uid_counter = self._cid_counter = 0
        self._session_secret = os.urandom(32) and b'server_secret'
        self._init()

    def _init(self):
        print("[server] Generating keys (~10s remaining)...")
        admin = self._create_user("admin")
        flagbot = self._create_user("flag_bot")
        _ = self._create_user("guest_seed")

        print(self._session_secret)

        chat = Chat(admin, flagbot)
        chat.add(admin, "Did you store the secret safely?")
        chat.add(flagbot, "Yes. IV discarded after sealing.")
        chat.add(admin, f"Perfect. Here it is: {FLAG}")
        chat.add(flagbot, "Vault sealed. End-to-end encrypted.")
        chat.seal()

        cid = self._store_chat(chat)
        print(f"[server] cid={cid} sealed\n")

    def _create_user(self, name: str) -> User:
        uid = self._uid_counter
        user = User(uid, name)
        self._users[uid] = user
        self._uid_counter += 1
        print(f"  uid={uid}  '{name}'  RSA-2048 key generated")
        return user

    def _store_chat(self, chat: Chat) -> int:
        cid = self._cid_counter
        self._chats[cid] = chat
        self._cid_counter += 1
        return cid

    def _generate_access_token(self, uid: int, cid: int) -> str:
        data = f"{uid}:{cid}".encode()
        token = hmac.new(self._session_secret, data, hashlib.sha256).hexdigest()
        return f"{uid}:{cid}:{token}"

    def _verify_access_token(self, token: str) -> tuple[int, int] | None:
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return None

            uid, cid, provided_hmac = int(parts[0]), int(parts[1]), parts[2]
            data = f"{uid}:{cid}".encode()
            expected_hmac = hmac.new(self._session_secret, data, hashlib.sha256).hexdigest()

            if provided_hmac == expected_hmac:
                return (uid, cid)
            return None
        except (ValueError, IndexError):
            return None

    def register(self, name: str) -> int:
        u = self._create_user(name)
        return u.id

    def list_users(self) -> list[dict[str, str]]:
        return [{"uid": str(u.id), "name": u.name} for u in self._users.values()]

    def get_pubkey(self, uid):
        u = self._users.get(uid)
        if not u: return {"error": "not found"}
        n, e = u.pub()
        return {"uid": uid, "name": u.name, "n": hex(n), "e": hex(e)}

    def get_chat(self, access_token: str) -> dict[str, dict[str, str] | str]:
        result = self._verify_access_token(access_token)
        if not result:
            return {"error": "invalid access token"}

        uid, cid = result
        chat = self._chats.get(cid)
        if not chat: return {"error": "not found"}
        try:
            return chat.blob(uid)
        except PermissionError as ex:
            return {"error": str(ex)}

    def create_chat(self, uid1: int, uid2: int, initial_message: str = "") -> tuple[int, str]:
        u1 = self._users.get(uid1)
        u2 = self._users.get(uid2)
        if not u1 or not u2:
            raise ValueError("Invalid user ID")

        chat = Chat(u1, u2)
        if initial_message:
            chat.add(u1, initial_message)
        chat.seal()
        cid = self._store_chat(chat)

        token = self._generate_access_token(uid1, cid)
        return cid, token


def interactive_menu(server: Server, my_uid: int):
    max_interactions = 50
    interaction_count = 0

    while interaction_count < max_interactions:
        interaction_count += 1

        print("┌──────────────────────────────┐")
        print("│      VaultChat  —  Menu      │")
        print("└──────────────────────────────┘\n")
        print("  [1] List users")
        print("  [2] View a chat (requires access token)")
        print("  [3] Start a new chat")
        print("  [4] Export encrypted blob to JSON")
        print("  [5] Exit\n")

        try:
            choice = int(input("Choice: ").strip())
        except ValueError as v:
            print(f"[!] Invalid input {v}")
            continue

        match choice:
            case 1:
                print("Registered users:")
                for u in server.list_users():
                    print(f"uid={u['uid']} - name={u['name']}")
            case 2:
                try:
                    token = input("Access token: ").strip()
                    blob = server.get_chat(token)

                    if "error" in blob:
                        print(f"[!] Error: {blob['error']}")
                    else:
                        print("[+] Encrypted blob retrieved:")
                        display = {}
                        for k, v in blob.items():
                            if isinstance(v, str) and len(v) > 60:
                                display[k] = v[:60] + "..."
                            else:
                                display[k] = v
                        print(json.dumps(display, indent=2))
                except (ValueError, Exception) as e:
                    print(f"[!] Error: {e}")
            case 3:
                try:
                    uid2 = int(input(f"\nStart chat with uid (you are uid={my_uid}): ").strip())
                    msg = input("Initial message: ").strip()

                    cid, token = server.create_chat(my_uid, uid2, msg)
                    print(f"[+] Chat created with cid={cid}")
                    print(f"[+] Your access token: {token}")
                    print("[i] Save this token to access the chat later!")
                except (ValueError, Exception) as e:
                    print(f"[!] Error: {e}")
            case 4:
                try:
                    token = input("Access token: ").strip()
                    blob = server.get_chat(token)

                    if "error" in blob:
                        print(f"[!] Error: {blob['error']}")
                    else:
                        print(json.dumps(blob, indent=2))

                except (ValueError, Exception) as e:
                    print(f"[!] Error: {e}")
            case 5:
                print("\n[*] Goodbye!")
                break
            case _:
                print("[!] Invalid choice")


def run():
    srv = Server()

    print("┌──────────────────────────────┐")
    print("│  VaultChat  —  Registering   │")
    print("└──────────────────────────────┘\n")

    name = str(input("Please register yourself (name): ").strip())
    if not name:
        name = "anonymous"

    my_uid = srv.register(name)
    print(f"[+] registered as uid = {my_uid}\n")

    interactive_menu(srv, my_uid)


if __name__ == "__main__":
    run()
