import os
import shutil
import sqlite3
from pathlib import Path
from typing import List, Optional

import click
from qreader import QReader
import cv2
from pyzbar.pyzbar import decode
from PIL import Image

from qr_code_data import QrCodeData


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


def process_qr_file(
    file_path: str, output_dir: str, db_conn: sqlite3.Connection, quiet: bool = False
) -> bool:
    """Process a single QR code file."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    if not quiet:
        print(f"╔═════════════════(( Decoding ))═════════════════⦿")
        print(f"╚═⫸ {file_path}")

    # Get the QR code data from image
    qr_string = read_qr_from_image(file_path)
    if not qr_string:
        if not quiet:
            click.echo(f"No QR code found in {file_path}")
        return False

    try:
        # Decode QR data
        qr_data = QrCodeData.from_qr_string(qr_string)

        # Store device info in database
        store_device_in_db(db_conn, qr_data, os.path.basename(file_path))

        # Create new filename with password
        file_stem = Path(file_path).stem
        file_suffix = Path(file_path).suffix
        new_file_name = f"{file_stem}_pw_{qr_data.e2e_password}{file_suffix}"
        new_file_path = os.path.join(output_dir, new_file_name)

        # Move and rename file
        shutil.copy2(file_path, new_file_path)

        if not quiet:
            click.echo(f"╔════════════════(( Processing ))════════════════⦿")
            click.echo(f"╠⦿ Processed: {file_path} -> {new_file_path}")
            click.echo(f"╠⦿ Header    {qr_data.header}")
            click.echo(f"╠⦿ Password  {qr_data.e2e_password}")
            click.echo(f"╠⦿ Footer    {qr_data.footer}")
            click.echo(f"╚═⫸ Devices  {len(qr_data.local_devices)}")
        return True
    except Exception as e:
        if not quiet:
            click.echo(f"Error processing {file_path}: {e}", err=True)
        return False


def process_directory_qr_files(
    directory: str,
    output_dir: str,
    db_path: str,
    extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif"],
    quiet: bool = False,
    delete_originals: bool = False,
) -> tuple:
    """Process all QR code image files in a directory."""
    # Setup database
    db_conn = setup_database(db_path)

    # Track statistics
    stats = {"total": 0, "processed": 0, "failed": 0}

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process all image files
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)

            # Check if file has a supported extension
            if any(file.lower().endswith(ext) for ext in extensions):
                stats["total"] += 1

                # Process the file
                success = process_qr_file(file_path, output_dir, db_conn, quiet)

                if success:
                    stats["processed"] += 1
                    # Delete original if requested
                    if delete_originals:
                        os.remove(file_path)
                else:
                    stats["failed"] += 1

    # Close database connection
    db_conn.close()

    return stats
