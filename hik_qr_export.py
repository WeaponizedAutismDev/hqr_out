import datetime
import os

import click
from qr_code_data import QrCodeData
from qr_directory_module import process_directory_qr_files


@click.group()
def cli():
    pass


@cli.command(help="Decode QR code data, extract metadata and stored devices.")
@click.argument("qr_string")
def decode(qr_string):
    qr_code_data = QrCodeData.from_qr_string(qr_string)
    click.echo()
    click.echo(f"╔═══════════════════(( Decoding ))════════════════════⦿")
    click.echo(f"╠⦿ Data header:          {qr_code_data.header}")
    click.echo(f"╠⦿ QR Password:          {qr_code_data.e2e_password}")
    click.echo(f"╠⦿ QR code footer:       {qr_code_data.footer}")
    click.echo(f"╚═════════════════════════════════════════════════════⦿")
    for local_device in qr_code_data.local_devices:
        click.echo(f"║")
        click.echo(f"╠⦿ Device Name:          {local_device.name}")
        click.echo(f"╠⦿ IP Address:           {local_device.ip_address}")
        click.echo(f"╠⦿ Port:                 {local_device.port}")
        click.echo(f"╠⦿ Username:             {local_device.username}")
        click.echo(f"╠⦿ Password:             {local_device.password}")
        click.echo(f"║")
        click.echo(f"╚═════════════════════════════════════════════════════⦿")


@cli.command(help="Renew QR code.")
@click.argument("qr_string")
@click.option(
    "-q", "--quiet", default=False, is_flag=True, help="Suppress printing timestamps."
)
@click.option("--timestamp", default=None, help="Specify exact timestamp to use.")
def renew(qr_string, quiet, timestamp):
    qr_code_data = QrCodeData.from_qr_string(qr_string)
    if not quiet:
        click.echo(f"QR code generated at: {qr_code_data.footer} ")
        #  f'({datetime.datetime.fromtimestamp(qr_code_data.footer).isoformat()})')
    if timestamp is None:
        qr_code_data.renew()
    else:
        qr_code_data.footer = timestamp
    if not quiet:
        click.echo(f"New timestamp of QR creation is: {qr_code_data.footer} ")
        #  f'({datetime.datetime.fromtimestamp(qr_code_data.footer).isoformat()})')
    click.echo(qr_code_data.encode("utf-8"))


@cli.command(
    help="Process QR code images in a directory and store device info in a database."
)
@click.argument(
    "directory", type=click.Path(exists=True, file_okay=False, dir_okay=True)
)
@click.option(
    "-o",
    "--output-dir",
    default="./processed",
    help="Directory to move processed files to.",
)
@click.option(
    "-d", "--database", default="devices.db", help="SQLite database file path."
)
@click.option(
    "-q", "--quiet", default=False, is_flag=True, help="Suppress detailed output."
)
@click.option(
    "--delete-originals",
    default=False,
    is_flag=True,
    help="Delete original files after processing.",
)
@click.option(
    "--extensions",
    default=".jpg,.jpeg,.png,.gif",
    help="Comma-separated list of file extensions to process.",
)
def process_directory(
    directory, output_dir, database, quiet, delete_originals, extensions
):
    """Process all QR code images in a directory."""
    # Parse extensions

    extension_list = [ext.strip() for ext in extensions.split(",")]

    # Create output directory if it doesn't exist

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    click.echo(f"Processing QR codes in {directory}...")
    click.echo(f"Output directory: {output_dir}")
    click.echo(f"Database: {database}")

    # Process the directory

    stats = process_directory_qr_files(
        directory=directory,
        output_dir=output_dir,
        db_path=database,
        extensions=extension_list,
        quiet=quiet,
        delete_originals=delete_originals,
    )

    click.echo()
    click.echo(f"Processing complete!")
    click.echo(f"Total files examined: {stats['total']}")
    click.echo(f"Successfully processed: {stats['processed']}")
    click.echo(f"Failed to process: {stats['failed']}")

    # Check database

    if stats["processed"] > 0:
        click.echo()
        click.echo(f"Device information stored in database: {database}")
        click.echo(f"You can query the database with SQL, for example:")
        click.echo(
            f"  sqlite3 {database} 'SELECT name, ip_address, username, password FROM devices'"
        )


if __name__ == "__main__":
    cli()
