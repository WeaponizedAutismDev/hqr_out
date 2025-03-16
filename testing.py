import base64
import datetime
import zlib

from errors import InvalidLengthError
from hik_aes import HikAES
from local_device import LocalDevice

# test string manually created from a decoded QR code. This is the data that would be passed to the QrCodeData class

QRdatq = "QRC03010003eJwz9MkxNMoJjfDOjgo0dQrPDS43yTEJtLW1CjWyLIkKdnKJDDfMSc51tVUzUPMNya70yXI18nc2qQDStmoWBgYGamoFxhYGlnmlfr6pziYeaVl54WFFJdnltrZq+gEFmb7Fvqna+o4BbsWGaaFF/pbljkAJFSvjJO+gpID0gMSUKKcqMxfz0mwjfUOgtQAmxisw"

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
print("╔════════════⫸ QR Code Data ⫷════════════⦿")
print("║")
print(f"╠⦿ Header    ➛ {header}")
print(f"╠⦿ QR PW     ➛ {e2e_password}")
print(f"╠⦿ Timestamp ➛ {footer}")
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

    print(f"╔════════════⫸ Device #{n}/{nodev - 1} ⫷════════════⦿")
    print("║")
    print(f"╠⦿ Device    ➛ {name}")
    print(f"╠⦿ Type      ➛ {devtype}")
    print(f"╠⦿ Host      ➛ {ip_address}")
    print(f"╠⦿ Port      ➛ {port}")
    print(f"╠⦿ Filler    ➛ {filler}")
    print(f"╠⦿ Username  ➛ {username}")
    print(f"╠⦿ Password  ➛ {password}")
    print("║")
    print("╚═⫸")
    if n == nodev - 1:
        # check for end of devices and break out of loop

        print("Finished Looping Devices")
        break
    else:
        n += 1
        continue
