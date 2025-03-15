import base64
from hik_aes import HikAES

def decodeAES(input_str: str) -> str:
    return HikAES().decrypt_b64_to_str(input_str).rstrip("\x00")

def decodeb64(input_str: str) -> str:
    return base64.b64decode(input_str).decode("unicode-escape")

str1 = decodeb64("MTkyLjE2OC4xLjE=")

string_enc_b64 = "TBCwBOnh0rZYdc8xFOICmQ=="

#TBCwBOnh0rZYdc8xFOICmQ==
#TBCwBOnh0rZYdc8xFOICm

ul = len(string_enc_b64)  # check length of string_enc_b64


valid_lengths = [16, 24, 32, 44]
if (
    ul in valid_lengths
):  # check for valid length of string_enc_b64 before attempting to decode
    string = HikAES().decrypt_b64_to_str(string_enc_b64)
else:
    string = f"Decrypt Error: {string_enc_b64} len is {ul}"

# Additional logging for clarity
print("Decoded string:", string)
print("Original string:", str1)
print("Length of encoded string:", ul)


