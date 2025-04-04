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

    def _fix_padding(self, s: str) -> str:
        s = s.strip()
        missing_padding = len(s) % 4
        return s + "=" * (4 - missing_padding) if missing_padding else s

    def decrypt_b64_to_str(self, ciphertext: str) -> str:
        ciphertext_fixed = self._fix_padding(ciphertext)
        decrypted = self.decrypt(base64.b64decode(ciphertext_fixed))
        return "".join(chr(c) for c in decrypted)

    def encrypt_str_to_b64(self, plaintext: str) -> str:
        encrypted = self.encrypt(plaintext.encode())
        return base64.b64encode(bytearray(encrypted)).decode()
