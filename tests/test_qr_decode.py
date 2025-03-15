import pytest
from hik_aes import HikAES
from qr_code_data import QrCodeData

def test_qr_decode():
    test_qr = "QRC03010003eJwrKnNNzC0vNy/yLogwD041LTUocg13tLW1ijRyK4mK8MpQM1DzDcmu9MlyNfJ3NqkA0rZqFgYGBmpqySWGuSYp5iEVwc5eHkZJHpnhWcFBQK04JVSsjJO8g5IC0gMSU6KcqsxczEuzjfQNA21tAQ4rKR0="
    qr_data = QrCodeData.from_qr_string(test_qr)
    assert qr_data.header == "QRC03010003"
    assert len(qr_data.local_devices) > 0

def test_aes_encryption():
    aes = HikAES()
    test_str = "test123"
    encrypted = aes.encrypt_str_to_b64(test_str.ljust(16, '\x00'))
    decrypted = aes.decrypt_b64_to_str(encrypted).rstrip('\x00')
    assert decrypted == test_str
