import base64

import pyaes


class HikAES(pyaes.AES):
    def __init__(self, key: bytes = b"dkfj4593@#&*wlfm", rounds: int = 4):
        self.number_of_rounds = {
            16: rounds,
            # 20: rounds,
            24: rounds,
            # 28: rounds,
            32: rounds,
            # 36: rounds,
            # 40: rounds,
            44: rounds,
            # 48: rounds,
            # 52: rounds,
            # 56: rounds,
            # 60: rounds,
            # 64: rounds,
        }  # 44 is not a standard key size, but it is used for padding by the looks found a few instances of ADT usernames 44 bytes long i tink the important thing here is the div/4 of the key size
        super().__init__(key)

    def decrypt_b64_to_str(self, ciphertext: str) -> str:
        return "".join(chr(c) for c in self.decrypt(base64.b64decode(ciphertext)))

    def encrypt_str_to_b64(self, plaintext: str) -> str:
        return base64.b64encode(bytearray(self.encrypt(plaintext.encode()))).decode()
