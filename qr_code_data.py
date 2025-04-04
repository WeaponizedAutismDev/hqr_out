import base64
import datetime
import zlib

from errors import InvalidLengthError, DecryptError
from hik_aes import HikAES
from local_device import LocalDevice


class QrCodeData:
    _e2e_password: str
    _footer: int
    _local_devices: list[LocalDevice]

    def __init__(
        self,
        e2e_password: str,
        local_devices: list[LocalDevice],
        header: str = "QRC03010003",
        footer: str = str(datetime.datetime.now().timestamp()),
    ):
        if len(e2e_password) > 16:
            raise InvalidLengthError(
                "e2e_password length must be not more than 16 characters"
            )
        self._e2e_password = e2e_password
        self._local_devices = local_devices
        self._header = header
        self._footer = footer

    @classmethod
    def from_qr_string(cls, qr_string: str) -> "QrCodeData":

        test_header = qr_string[:4]
        if test_header == "iVMS":
            header = qr_string[:12]
            compressed_data_b64 = qr_string[12:].strip()
        else:
            header = qr_string[:11]
            compressed_data_b64 = qr_string[11:].strip()
        missing_padding = len(compressed_data_b64) % 4
        if missing_padding:
            compressed_data_b64 += "=" * (4 - missing_padding)
        decompressed_data = zlib.decompress(
            base64.b64decode(compressed_data_b64)
        ).decode("utf-8")

        clean_decompressed_data = cls.handle_variations(decompressed_data)

        split_count = len(clean_decompressed_data.split(":"))

        if len(clean_decompressed_data.split(":")) == 3:
            e2e_password_enc_b64, local_devices_str, footer_enc = (
                clean_decompressed_data.split(":")
            )
            try:
                e2e_password = (
                    HikAES().decrypt_b64_to_str(e2e_password_enc_b64).rstrip("\x00")
                )
            except Exception as e:
                raise DecryptError(f"Error decrypting e2e_password: {e}")
            try:
                footer = HikAES().decrypt_b64_to_str(footer_enc).rstrip("\x00")
            except Exception as e:
                raise DecryptError(f"Error decrypting footer: {e}")
        elif len(clean_decompressed_data.split(":")) == 2:
            e2e_password_enc_b64, local_devices_str = clean_decompressed_data.split(":")
            try:
                e2e_password = (
                    HikAES().decrypt_b64_to_str(e2e_password_enc_b64).rstrip("\x00")
                )
            except Exception as e:
                raise DecryptError(f"Error decrypting e2e_password: {e}")
            footer = str(datetime.datetime.now().timestamp())
        elif len(clean_decompressed_data.split(":")) == 1:
            local_devices_str = clean_decompressed_data
            e2e_password = "NoPassWD"
            footer = str(datetime.datetime.now().timestamp())

        local_devices = []

        for local_device_encoded in local_devices_str.split("$"):
            if not len(local_device_encoded):
                #       print("continue")
                continue
            local_devices.append(LocalDevice.from_encoded(local_device_encoded))
        return cls(
            e2e_password=e2e_password,
            local_devices=local_devices,
            header=header,
            footer=footer,
        )

    def handle_variations(decompressed_data: str) -> str:
        # Standardize delimeters
        return decompressed_data.replace(";", "$").replace(",", "&")

    def renew(self):
        self._footer = str(datetime.datetime.now().timestamp())

    def encode(self) -> str:
        local_devices_str = (
            "$".join(local_device.encode() for local_device in self._local_devices)
            + "$"
        )
        compressed_data_b64 = base64.b64encode(
            zlib.compress(
                ":".join(
                    [
                        HikAES().encrypt_str_to_b64(
                            self._e2e_password.ljust(16, "\x00")
                        ),
                        local_devices_str,
                        HikAES().encrypt_str_to_b64(
                            str(self._footer).ljust(16, "\x00")
                        ),
                    ]
                ).encode("utf-8")
            )
        ).decode("utf-8")
        return f"{self._header}{compressed_data_b64}"

    @property
    def e2e_password(self) -> str:
        return self._e2e_password

    @property
    def local_devices(self) -> list[LocalDevice]:
        return self._local_devices

    @property
    def header(self) -> str:
        return self._header

    @property
    def footer(self) -> int:
        return self._footer

    @footer.setter
    def footer(self, value: str):
        self._footer = value

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(header='{self.header}', e2e_password='{self._e2e_password}', "
            f"footer={self.footer})"
        )
