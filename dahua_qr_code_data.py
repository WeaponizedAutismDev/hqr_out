import base64
import datetime
import gzip
import json
from typing import List
from errors import DecryptError
from dahua_local_device import dahuaLocalDevice
from logger import setup_logger
import json

logger = setup_logger(__name__)

def decode_gzip_base64_string(encoded_str):
    try:
        binary_data = base64.b64decode(encoded_str)
        decompressed_data = gzip.decompress(binary_data)
        return decompressed_data.decode('utf-8')
    except Exception as e:
        logger.error(f"Error decoding gzip string: {e}")
        print(f"Error decoding string: {e}")
        return None

def parse_devices_from_json(json_data: str) -> list[dahuaLocalDevice]:
    """
    Parse a JSON string that may contain one or more devices and return a list of LocalDevice objects.
    
    Args:
        json_data: JSON string containing device information
        
    Returns:
        List of LocalDevice objects
    """
    logger.info({json_data})
    try:

        # Parse the JSON data
        #data = json.loads(json_data)
        clean_data = json.loads(json_data)
        logger.info(f"raw JSON: {json_data}")
        #logger.info(f"raw JSON Load: {data}")
        logger.info(f"raw JSON Load: {clean_data}")
        
        # Initialize the list to store LocalDevice objects
        dahua_local_devices = []
        
        # Check if we have a list of devices
        if isinstance(clean_data, list):
            for device_data in clean_data:
                dahua_local_device = dahuaLocalDevice.from_encoded(device_data)
                dahua_local_devices.append(dahua_local_device)
        else:
            # Handle case where data might be a single device (not in a list)
            logger.info(f"no list {clean_data}")    
            dahua_local_device = dahuaLocalDevice.from_encoded(clean_data)
            dahua_local_devices.append(dahua_local_device)
        logger.info(f"Local devices {dahua_local_devices}")    
        return dahua_local_devices
    
    except json.JSONDecodeError as e:
        logger.error(f"Error Decoding JSON {e}")
        print(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error parsing devices: {e}")
        logger.error(f"Unexpected error parsing devices: {e}")
        return []   

class dahuaQrCodeData:
    _e2e_password: str
    _footer: int
    _dahua_local_devices: list[dahuaLocalDevice]

    def __init__(
        self,
        e2e_password: str,
        dahua_local_devices: list[dahuaLocalDevice],
        header: str = "DMSS",
        footer: str = str(datetime.datetime.now().timestamp()),
    ):
        self._e2e_password = e2e_password
        self._dahua_local_devices = dahua_local_devices
        self._header = header
        self._footer = footer

    @classmethod
    def dahua_from_qr_string(cls, qr_string: str) -> "dahuaQrCodeData":
        header_test = qr_string[:4]
        if header_test == "DMSS":
           header = qr_string[:4]
           logger.info(f"header {header}")
           compressed_data_b64gz = qr_string[5:].strip()
        else: 
           header = "No_Header"
           logger.info(f"header {header}")
           compressed_data_b64gz = qr_string.strip()
        logger.info(f"compressed gzip data {compressed_data_b64gz}")
        dahua_local_devices_str:str
        parts = compressed_data_b64gz.split(':')
        logger.info(f"parts {len(parts)}")
        if len(parts) == 2:
            e2e_password, dahua_local_devices_str_enc = parts
            try:
                logger.info(f"two parts path")
                dahua_local_devices_str = decode_gzip_base64_string(dahua_local_devices_str_enc)
                logger.info(f"local_devices_string {dahua_local_devices_str}")
                logger.info(f" e2e password {e2e_password}")
                footer = str(datetime.datetime.now().timestamp())
                logger.info(f"footer {footer}")
            except Exception as e:
                logger.error(f"Error decrypting QR: {e}")
                raise DecryptError(f"Error decrypting QR: {e}")
        else:
            try:
                logger.info(f"one parts path")
                dahua_local_devices_str = decode_gzip_base64_string(compressed_data_b64gz)
                logger.info(f"local_devices_string {dahua_local_devices_str}")
                e2e_password= "NoPassword"
                logger.info(f" e2e password {e2e_password}")
                footer = str(datetime.datetime.now().timestamp())
                logger.info(f"footer {footer}")
            except Exception as e:
                logger.error(f"Error decrypting QR: {e}")
                raise DecryptError(f"Error decrypting QR: {e}")
            
        dahua_local_devices = parse_devices_from_json(dahua_local_devices_str)
        logger.info(f"local devices to return {dahua_local_devices}")
        return cls(
            e2e_password=e2e_password,
            dahua_local_devices=dahua_local_devices,
            header=header,
            footer=footer
        )

    
    @property
    def e2e_password(self) -> str:
        return self._e2e_password

    @property
    def dahua_local_devices(self) -> list[dahuaLocalDevice]:
        return self._dahua_local_devices

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
