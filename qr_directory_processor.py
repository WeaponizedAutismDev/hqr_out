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

logger = setup_logger()


def setup_database(db_path: str) -> sqlite3.Connection:
    """Setup SQLite database for storing device information."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table for devices if it doesn't exist
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ip_address TEXT NOT NULL,
        port INTEGER NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        qr_file TEXT NOT NULL,
        qr_password TEXT NOT NULL,
        footer TEXT NOT NULL
    )
    """
    )
    conn.commit()

    return conn


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


def store_device_in_db(
    conn: sqlite3.Connection, qr_data: QrCodeData, qr_file: str
) -> None:
    """Store device information from QR code into database."""
    cursor = conn.cursor()

    for device in qr_data.local_devices:
        cursor.execute(
            """
        INSERT INTO devices 
        (name, ip_address, port, username, password, qr_file, qr_password, footer)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                device.name,
                device.ip_address,
                device.port,
                device.username,
                device.password,
                qr_file,
                qr_data.e2e_password,
                qr_data.footer,
            ),
        )

    conn.commit()


def sanitize_filename(filename: str) -> str:
    """Clean filename to prevent Windows path errors."""
    # Remove or replace problematic characters
    filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    # Replace multiple spaces with single space
    filename = ' '.join(filename.split())
    # Ensure filename isn't too long
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:195] + '...' + ext
    return filename


def process_qr_file(
    file_path: str, output_dir: str, db_conn: sqlite3.Connection, quiet: bool = False
) -> bool:
    """Process a single QR code file."""
    try:
        # Convert paths to Path objects for safer handling
        file_path = Path(file_path)
        output_dir = Path(output_dir)
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        if not quiet:
            logger.info(f"Processing: {file_path}")

        # Get the QR code data from image
        qr_string = read_qr_from_image(str(file_path))
        if not qr_string:
            logger.error(f"No QR code found in {file_path}")
            return False

        # Decode QR data
        qr_data = QrCodeData.from_qr_string(qr_string)

        # Store device info in database
        store_device_in_db(db_conn, qr_data, file_path.name)

        # Create new filename with password
        safe_stem = sanitize_filename(file_path.stem)
        safe_password = sanitize_filename(qr_data.e2e_password)
        new_file_name = f"{safe_stem}_pw_{safe_password}{file_path.suffix}"
        new_path = output_dir / new_file_name

        # Ensure unique filename
        counter = 1
        while new_path.exists():
            new_file_name = f"{safe_stem}_pw_{safe_password}_{counter}{file_path.suffix}"
            new_path = output_dir / new_file_name
            counter += 1

        # Copy file with error handling
        try:
            shutil.copy2(file_path, new_path)
            logger.info(f"Successfully copied to: {new_path}")
        except Exception as e:
            logger.error(f"Failed to copy {file_path} -> {new_path}: {e}")
            # Fallback to basic file copy
            try:
                with open(file_path, 'rb') as src, open(new_path, 'wb') as dst:
                    dst.write(src.read())
                logger.info("Successfully copied using fallback method")
            except Exception as e:
                logger.error(f"Fallback copy also failed: {e}")
                return False

        return True

    except Exception as e:
        logger.exception(f"Error processing {file_path}: {e}")
        return False


def process_directory_qr_files(
    directory: str,
    output_dir: str,
    db_path: str,
    extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif"],
    quiet: bool = False,
    delete_originals: bool = False,
) -> dict:
    """Process all QR code image files in a directory."""
    logger.info(f"Starting directory processing: {directory}")
    
    # Setup database first
    db_conn = setup_database(db_path)
    
    try:
        # Backup database if exists
        if Path(db_path).exists():
            backup_path = f"{db_path}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            shutil.copy2(db_path, backup_path)
            logger.info(f"Created database backup: {backup_path}")

        # Track statistics
        stats = {"total": 0, "processed": 0, "failed": 0}

        # Get list of files
        files = list(Path(directory).glob("**/*"))
        image_files = [f for f in files if f.suffix.lower() in extensions]
        
        # Process files with progress bar
        with click.progressbar(image_files, label='Processing QR codes') as files:
            for file_path in files:
                stats["total"] += 1
                try:
                    success = process_qr_file(str(file_path), output_dir, db_conn, quiet)
                    if success:
                        stats["processed"] += 1
                        if delete_originals:
                            os.remove(file_path)
                    else:
                        stats["failed"] += 1
                except Exception as e:
                    stats["failed"] += 1
                    logger.exception(f"Error processing {file_path}: {e}")

        return stats
        
    finally:
        # Ensure database connection is closed
        db_conn.close()
