import base64
import datetime
import zlib

from errors import InvalidLengthError
from hik_aes import HikAES
from local_device import LocalDevice

# test string manually created from a decoded QR code. This is the data that would be passed to the QrCodeData class
QRdatq = "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"

header = QRdatq[:11]
compressed_data_b64 = QRdatq[11:]
decompresseddata = zlib.decompress(base64.b64decode(compressed_data_b64)).decode(
    "utf-8"
)
clean_decompressed_data = decompresseddata.replace(";", "$").replace(",", "&")
split_data = clean_decompressed_data.split(":")
mastersplits = len(split_data)
print(f"Master Splits: {mastersplits}")
# sometimes there is no password or footer so we need to check for that and adjust the split accordingly
if mastersplits == 3:
    e2e_password_enc_b64 = split_data[0]
    local_devices_str = split_data[1]
    footer_enc = split_data[2]
elif mastersplits == 2:
    e2e_password_enc_b64 = split_data[0]
    local_devices_str = split_data[1]
elif mastersplits == 1:
    local_devices_str = split_data[0]
else:
    print("Error in split_data")
print(split_data)


if not e2e_password_enc_b64 is None:
    e2e_password = HikAES().decrypt_b64_to_str(e2e_password_enc_b64).rstrip("\x00")
else:
    e2e_password = "No QR password"
if not footer_enc is None:
    footer = HikAES().decrypt_b64_to_str(footer_enc).rstrip("\x00")
else:
    footer = "No Timestamp footer"

print("╔════════⫸ QR Code Data ⫷═════════⦿")
print("║")
print(f"╠⦿ Data header:   {header}")
print(f"╠⦿ QR Password:   {e2e_password}")
print(f"╠⦿ QR TS Footer:  {footer}")
print("║")
print("╚═⫸")
split_devices = list
# local_devices_str = "TmlnaHQgY2x1YiDwn5GvIEBIaWtRUkNhbQ==&0&ODYuMTI0Ljk1LjE5OA==&8000&&bdAew4pqk8YRp2lliUewpw==&Ik/iC7agUC/evBuaxVpLtA==$Q0FNMDk1&0&ZGRuczk3NzcuZHZybGlzdHMuY29t&8000&&QOBjV/vzvbh4MyTDpDlFhQ==&IXLIcz215Ei0GTLtrkiCmw==$dXNhIDExLTEz&0&YXplcjEyMy5uZXdkZG5zLmNvbQ==&8000&&pXnq01IIDFnNN6UOS5GyMw==&3Td4JtN1uniZUQjX2BnrtQ==$WCxDNg==&0&MTc5LjEwNS4xNDEuNjE=&8000&&ct1m4d7TxSCJH2bHiWjSRA==&e76jf6InR8h27eRk942kAg==$Q3VhcnRvIGM1&0&MTgxLjk0LjIxNC4yMzY=&8000&&ct1m4d7TxSCJH2bHiWjSRA==&9hx3uDDFI4vCOqCpw17zkw==$VGVlbiAwMSDwn4y3&0&MTgxLjEyMC4xNDAuMTk3&8000&&RaqOzAh9Yv0k5DsqdlQ+AA==&OC0B0i0b4Fb9fneP3Cx2pQ==$eHguc2V4LHNvdW5k8J+aqA==&0&aGlrY2FtNDQ2NzguY2FtZXJhZGRucy5uZXQ=&8000&&UxEsp+tdxnlO5DC8VOTQlQ==&ub0k1G7+RoE608npf8RkQA==$QSBub3JtYWwg8J+PoCBASGlrUVJDYW0=&0&c2lldXF1YXkuY2FtZXJhZGRucy5uZXQ=&8001&&I0Tqjjo/XmuTS+vyRfap5g==&9hx3uDDFI4vCOqCpw17zkw==$dmlwNjY=&0&Y2FtZXJhaGFpeWVubjkuY2FtZXJhZGRucy5uZXQ=&8001&&ct1m4d7TxSCJH2bHiWjSRA==&xVTFZ+HuWcv7Kgls5JKLAA==$YmljaWNsZXRhLmMzMA==&0&NzYuODYuMjQuMTU3&8000&&QOBjV/vzvbh4MyTDpDlFhQ==&Hijthc9QWT4sXjW8aKM7Bw==$bG9pcmE=&0&OTUuNjcuNjMuMjIy&8000&&PmXE8tWFIIrXw72J1SEurw==&WFo38H3PnI6vxrUll4QuCg==$Y2FtaXRhIGRvw7FhIGJi&0&ODEuMTk2LjEwLjM=&8000&&QOBjV/vzvbh4MyTDpDlFhQ==&FOErAwAyxiE3myz44/Yekg==$TmV1ZXMgR2Vyw6R0IDAx&0&MTk0LjI2LjE2NC4yMzY=&8000&&jJVIk0AVs6tBh/nZFq71VA==&reVrwdyl+mPyort0M6CH5Q==$8J+UpSAwNw==&0&MTgxLjEyMS45Ni4xNjI=&8000&&2liIWYcAnNep22TO2q23qg==&Ik/iC7agUC/evBuaxVpLtA==$bWFzc2FnZSBiag==&0&aG9hbmdkdW9uZzEuY2FtZXJhZGRucy5uZXQ=&8004&&ct1m4d7TxSCJH2bHiWjSRA==&9hx3uDDFI4vCOqCpw17zkw==$d2hpdGUgcm9vbSAjMTY=&0&MTA4LjIwMC4yMzYuMjQ1&8000&&QOBjV/vzvbh4MyTDpDlFhQ==&bJcbReNU3IQ74HAyXZEmJw==$bmlnaHQgdmNhbQ==&0&NjcuMjUwLjkxLjQx&8002&&IY3ep/BdqwL5Zq7hA3uh1A==&2FvWLUzMgLnHUnVLWl4fLg==$dC5tZS9ob3Rpa2FtIGNhbSAzMTk=&0&NS4xNzguMTYwLjIwMw==&8000&&QOBjV/vzvbh4MyTDpDlFhQ==&1t8NkpAqGZjFfrIG1awJPg==$YXNjZW5zb3IgY2FtYSBpbmRpYQ==&0&MTExLjEyNS4yNTUuMjA5&8000&&QOBjV/vzvbh4MyTDpDlFhQ==&RUDKDdQKYYBRDMQtR8O5sQ==$ODY=&0&MzEuMTU0LjIzMi45Ng==&8000&&ct1m4d7TxSCJH2bHiWjSRA==&LeXbf2tSfjHNAQqNGRF23g==$R29vZCBjYW1lcmEg&0&NzUuNzQuMTYyLjY1&8000&&QOBjV/vzvbh4MyTDpDlFhQ==&+xhbl7NGpJDBonjz7YibQA==$MDE4OPCfm6HvuI9MYSBjaGljYSBkZWwgU29mYSBDMw==&0&Z2VtbWFyaWdkZW4uZGRucy5uZXQ=&8000&&pXnq01IIDFnNN6UOS5GyMw==&8SeQ+xH5EQbM9aGfoUWBdg==$bW9tMg==&0&aGlra2E4NzAuY2FtZXJhZGRucy5uZXQ=&8000&&p3809nuNMeC4HfjnWVrtkw==&CIYBBuIuoSeN5aOW5Y47Gg==$VklWQTE=&0&MTgxLjEyMC4xOTAuNTI=&8000&&kxGb4BGTQbhsmfvrzHxY7A==&swNbX9jssPMViabva2VaTg==$QGlwY2FtY2x1YjNfMSB0ZWxlZ3JhbSAyKDQp&0&NjYuMjI5LjE1Ni42OQ==&8000&&B68HpDrnCeZLsA+TcAlV/A==&2XMuP+pDevGGm8OfBQygNQ==$VGVlbiA5MzY=&0&YWxkZWJhcmFueWNhbTkzNnRlbGVncmFtLmNhbWVyYWRkbnMubmV0&8000&&mkE8DPdX3Tml4M9fWBu+6a+vE/QiqZTwtmEhe9csjbE=&v/28w9UbJyk/90iFuYbhgA==$MTQ1IG1heWJlIGM3&0&MTgyLjE2MC4xMDAuMTQy&8000&&7jb1MCqw+G0g7MOT5v0lbw==&pp3DtRx7XC7jawWoZCzlMA==$Q2FtZXJhIDg4&0&MTg2LjAuNzAuMTI0&8000&&I0Tqjjo/XmuTS+vyRfap5g==&qS5egoFBLqpxmf020rQggw==$VklQMTMyIC0gdC5tZS92aXBlcnZpcGNhbQ==&0&MTg2LjE1NS42MC4yMg==&8000&&I0Tqjjo/XmuTS+vyRfap5g==&zK7/9+qQSBByyTPsNDBOHg==$ZnVja/Cfm48wMw==&0&MTgxLjEyMy4yMjYuMzI=&8000&&9iAaCj8uNxPDyP0XWV4q+w==&2dpYVABo5VbKG8DiKP1HIw==$'"
split_dev = local_devices_str.split("$")
nodev = len(split_dev)
n = 1
print(f"num devices = {nodev - 1}")
for dev in split_dev:
    split_devices = dev.split("&")
    name_b64 = split_devices[0]
    devtype_unenc = split_devices[1]
    ip_address_b64 = split_devices[2]
    port_unenc = split_devices[3]
    filler_unenc = split_devices[4]
    username_enc_b64 = split_devices[5]
    password_enc_b64 = split_devices[6]

    name = base64.b64decode(name_b64).decode(
        "unicode-escape"
    )  # .decode('utf-8') unicode-escape needed to handle some vietnamese characters that do not play well with utf-8
    devtype = int(devtype_unenc)
    ip_address = base64.b64decode(ip_address_b64).decode(
        "unicode-escape"
    )  # .decode('utf-8') unicode-escape needed to handle some vietnamese characters that do not play well with utf-8
    port = int(port_unenc)
    filler = filler_unenc
    ul = len(username_enc_b64)  # check length of username_enc_b64

    if (
        len(username_enc_b64) == 24
    ):  # check for valid length of username_enc_b64 before attempting to decode seems ok after adding 44 bytes to the AES key in HikAES is the real check here divisible by 4?
        username = HikAES().decrypt_b64_to_str(username_enc_b64).rstrip("\x00")
    else:
        username = f"Decrypt Error: {username_enc_b64} len is {ul}"
    password = HikAES().decrypt_b64_to_str(password_enc_b64).rstrip("\x00")

    print(f"╔═⫸ Device #{n}/{nodev - 1} ⫷═══⦿")
    print("║")
    print(f"╠⦿ Device ➛   {name}")
    print(f"╠⦿ Type ➛     {devtype}")
    print(f"╠⦿ Host ➛     {ip_address}")
    print(f"╠⦿ Port ➛     {port}")
    print(f"╠⦿ Filler ➛   {filler}")
    print(f"╠⦿ Username ➛ {username}")
    print(f"╠⦿ Password ➛ {password}")
    print("║")
    print("╚═⫸")
    if n == nodev - 1:
        # check for end of devices and break out of loop
        print("Finished Looping Devices")
        break
    else:
        n += 1
        continue
