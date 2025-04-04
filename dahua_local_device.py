from logger import setup_logger
import json
import requests

logger = setup_logger(__name__)

class dahuaLocalDevice:
    _name: str
    _ip_address: str
    _port: int
    _username: str
    _password: str

    def __init__(
        self, name: str, ip_address: str, port: int, username: str, password: str
    ):
        self._name = name
        self._ip_address = ip_address
        self._port = port
        self._username = username
        self._password = password

    @classmethod
    def from_encoded(cls, json_string: str) -> "dahuaLocalDevice":
        """
        Create a LocalDevice instance from a JSON string representing a single device.
        """
        unicode_json_data = json.dumps(json_string, ensure_ascii=False)   
        logger.info(f"unicode json {unicode_json_data}")   
        data = json.loads(unicode_json_data) 
        logger.info(f"parsed data {data}")
        #data = json.loads(data_parse)
        #logger.info(f"2nd parsed data {data}")
        
        # Extract required fields
        name:str = data['deviceName']
        ip_address:str = data['ip']
        # Handle port as either string or int
        port_value = data['port']
        port_num = int(port_value) if isinstance(port_value, str) else port_value
        username:str = data['userName']
        password:str = data['passWord']
        
        return cls(
            name=name,
            ip_address=ip_address,
            port=port_num,
            username=username,
            password=password,
        )

    # def encode(self) -> str:
    #     return (    
    #     #re encode device to json        
    #     )

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
        
        
   