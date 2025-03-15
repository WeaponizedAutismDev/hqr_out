import base64
from hik_aes import HikAES

def encode(input_str: str) -> str:
    str_padded = input_str.ljust(16, '\x00')
    return HikAES().encrypt_str_to_b64(str_padded)

def encodeb64(input_str: str) -> str:
    return base64.b64encode(input_str.encode('utf-8')).decode('utf-8')

str1 = encodeb64("subdomain.domain.tld")

str2 = encode("secretpassword")

print(str1)
print(str2)
