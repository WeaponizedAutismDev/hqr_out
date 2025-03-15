import base64
from errors import InvalidLengthError, MalformedDeviceDataError
from hik_aes import HikAES
from logger import setup_logger

logger = setup_logger(__name__)

class LocalDevice:
    _name: str
    _ip_address: str
    _port: int
    _username: str
    _password: str

    @staticmethod
    def _is_valid_block(encoded_str: str) -> bool:
        """Check if base64 string length is valid for AES block."""
        try:
            decoded = base64.b64decode(encoded_str)
            blocks = len(decoded) // 4  # AES block size is 16 bytes using 4 rounds
            logger.debug(f"Block length validation: {len(decoded)} bytes = {blocks} blocks")
            return len(decoded) % 4 == 0  # Must be divisible by 4
        except Exception:
            return False

    def __init__(
        self, name: str, ip_address: str, port: int, username: str, password: str
    ):
        # Remove validation/truncation and store values as-is
        self._name = name
        self._ip_address = ip_address
        self._port = port
        self._username = username
        self._password = password

    @classmethod
    def from_encoded(cls, ampersand_string: str) -> "LocalDevice":
        try:
            name_b64, _, ip_address_b64, port, _, username_enc_b64, password_enc_b64 = (
                ampersand_string.split("&")
            )
        except ValueError:
            raise MalformedDeviceDataError(
                f"not enough fields in ampersand string (expected 7, got {ampersand_string.count('&')})"
            )

        # Decode name
        try:
            name = base64.b64decode(name_b64).decode("unicode-escape")
            logger.debug(f"Successfully decoded name: {name}")
        except Exception as exc:
            logger.error(f"Failed to decode name field: {name_b64}, Error: {exc}")
            name = f"[DECODE_ERROR]_{name_b64}"

        # Decode IP address
        try:
            ip_address = base64.b64decode(ip_address_b64).decode("unicode-escape")
            logger.debug(f"Successfully decoded IP: {ip_address}")
        except Exception as exc:
            logger.error(f"Failed to decode IP field: {ip_address_b64}, Error: {exc}")
            ip_address = f"[DECODE_ERROR]_{ip_address_b64}"

        # Handle username decryption
        try:
            if cls._is_valid_block(username_enc_b64):
                decoded_len = len(base64.b64decode(username_enc_b64))
                blocks = decoded_len // 4
                logger.debug(f"Username for {name}: {decoded_len} bytes in {blocks} blocks")
                username = HikAES().decrypt_b64_to_str(username_enc_b64).rstrip("\x00")
            else:
                logger.error(f"Invalid AES block length for username: {username_enc_b64}")
                username = f"[INVALID_BLOCK_{len(base64.b64decode(username_enc_b64))}]_{username_enc_b64}"

        except Exception as exc:
            logger.error(f"Failed to decrypt username block: {exc}")
            username = f"[DECRYPT_ERROR]_{username_enc_b64}"

        # Handle password decryption
        try:
            if cls._is_valid_block(password_enc_b64):
                decoded_len = len(base64.b64decode(password_enc_b64))
                blocks = decoded_len // 4
                logger.debug(f"Password for {name}: {decoded_len} bytes in {blocks} blocks")
                password = HikAES().decrypt_b64_to_str(password_enc_b64).rstrip("\x00")
            else:
                logger.error(f"Invalid AES block length for password: {password_enc_b64}")
                password = f"[INVALID_BLOCK_{len(base64.b64decode(password_enc_b64))}]_{password_enc_b64}"

        except Exception as exc:
            logger.error(f"Failed to decrypt password block: {exc}")
            password = f"[DECRYPT_ERROR]_{password_enc_b64}"

        # Handle port conversion
        try:
            port_num = int(port)
        except ValueError as exc:
            logger.error(f"Invalid port number for {name}: {port}, Error: {exc}")
            port_num = 0

        # Create device instance with potentially failed fields
        return cls(
            name=name,
            ip_address=ip_address,
            port=port_num,
            username=username,
            password=password,
        )

    def encode(self) -> str:
        username_padded = self._username.ljust(16, "\x00")
        password_padded = self._password.ljust(16, "\x00")
        return "&".join(
            [
                base64.b64encode(self._name.encode("utf-8")).decode("utf-8"),
                "0",  # Always 0 in my cases (maybe device type)
                base64.b64encode(self._ip_address.encode("utf-8")).decode("utf-8"),
                str(self._port),
                "",  # Always empty in my cases
                HikAES().encrypt_str_to_b64(username_padded, "utf-8"),
                HikAES().encrypt_str_to_b64(password_padded, "utf-8"),
            ]
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def ip_address(self) -> str:
        return self._ip_address

    @property
    def port(self) -> int:
        return self._port

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name='{self.name}', ip_address='{self.ip_address}', port={self.port}, "
            f"username='{self.username}', password='{self.password}')"
        )
