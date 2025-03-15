import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class Config:
    db_path: str = "devices.db"
    output_dir: str = "./processed"
    allowed_extensions: List[str] = (".jpg", ".jpeg", ".png", ".gif")
    backup_enabled: bool = True
    backup_dir: str = "./backups"
    log_file: str = "hik_qr.log"

def load_config(config_file: str = "config.yml") -> Config:
    if Path(config_file).exists():
        with open(config_file) as f:
            config_dict = yaml.safe_load(f)
            return Config(**config_dict)
    return Config()
