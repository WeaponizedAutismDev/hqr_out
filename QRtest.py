import os
import shutil
import sqlite3
import re
from pathlib import Path
from typing import List, Optional

import click
from qreader import QReader
import cv2
from pyzbar.pyzbar import decode
from PIL import Image

from qr_code_data import QrCodeData
from logger import setup_logger
from datetime import datetime


qreader = QReader()


def read_qr_from_image(image_path: str) -> Optional[str]:
    """Read QR code data from an image file."""
    try:
        # img = Image.open(image_path)
        image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        # decoded_objects = decode(img)
        decoded_text = qreader.detect_and_decode(image=image)

        for text in decoded_text:
            return text
        # for obj in decoded_objects:
        #     if obj.type == 'QRCODE':
        #         return obj.data.decode('utf-8')

        # No QR code found
        return None
    except Exception as e:
        click.echo(f"Error reading QR code from {image_path}: {e}", err=True)
        return None
    
def process_qr_file(file_path: str) -> str:
    file_path = Path(file_path)


    # Get the QR code data from image
    qr_string = read_qr_from_image(str(file_path))

    if not qr_string:
        return False
    else: 
        return qr_string
 
extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif"] 
files = list(Path("d:/convertqr/").glob("**/*"))
image_files = [f for f in files if f.suffix.lower() in extensions]

# Process files with progress bar
for file_path in files: 
    print(f"file: {file_path}")
    print("")
    qr = process_qr_file(file_path)
    print(qr)
    print("")
    print("")

