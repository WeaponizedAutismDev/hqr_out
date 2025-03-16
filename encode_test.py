import base64
import zlib
from hik_aes import HikAES

def encodeaes(input_str: str) -> str:
    str_padded = input_str.ljust(16, '\x00')
    return HikAES().encrypt_str_to_b64(str_padded)

def encodeb64(input_str: str) -> str:
    return base64.b64encode(input_str.encode('utf-8')).decode('utf-8')

def compresszl64(input_str: str) -> str:
    return  base64.b64encode(zlib.compress(input_str.encode("utf-8"))).decode("utf-8")
header = 'QRC03010003'
qpw = encodeaes("a12345")
name = encodeb64("Some Camera")
devt = "0"
host = encodeb64("192.168.1.1")
port = "8000"
filler = ""
un = encodeaes("Admin")
pw = encodeaes("Admin123")
timestamp = encodeaes("1740175993")
a = [name,devt,host,port,filler,un,pw,"$"]
devicestring = "&".join(a)
b = [qpw,devicestring,timestamp]
uncompressedstring = ":".join(b)
compressed = compresszl64(uncompressedstring)
fullQRString = header+compressed

print(f"qpw          🐱 {qpw}")
print(f"name         🐱 {name}")
print(f"devt         🐱 {devt}")
print(f"host         🐱 {host}")
print(f"port         🐱 {port}")
print(f"filler       🐱 {filler}")
print(f"un           🐱 {un}")
print(f"pw           🐱 {pw}")
print(f"timestamp    🐱 {timestamp}")
print(f"devicestring 🐱 {devicestring}")
print(f"uncomp       🐱 {uncompressedstring}")
print(f"compressed   🐱 {compressed}")
print(f"fullQRString 🐱 {fullQRString}")