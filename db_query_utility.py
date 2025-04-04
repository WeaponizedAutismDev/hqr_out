#!/usr/bin/env python3
import sys
import sqlite3
import click
from tabulate import tabulate


def safe_text_factory(data):
    try:
        return str(data, "utf-8")
    except UnicodeDecodeError:
        return str(data, "utf-8", "replace")


@click.group()
def cli():
    """Query the QR code device database."""
    pass


@cli.command(help="List all devices in the database.")
@click.argument("database", type=click.Path(exists=True))
@click.option(
    "--format",
    "-f",
    default="grid",
    type=click.Choice(["grid", "csv", "plain", "markdown"]),
    help="Output format.",
)
def list_devices(database, format):
    """List all devices stored in the database."""
    conn = sqlite3.connect(database)
    conn.text_factory = safe_text_factory
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT name, ip_address, port, username, password, qr_file, qr_password, footer
    FROM devices
    ORDER BY name
    """
    )

    rows = cursor.fetchall()
    headers = [
        "name",
        "ip_address",
        "port",
        "username",
        "password",
        "qr_file",
        "qr_password",
        "footer",
    ]

    if not rows:
        click.echo("No devices found in the database.")
        return

    click.echo(tabulate(rows, headers=headers, tablefmt=format))
    click.echo(f"\nTotal devices: {len(rows)}")

    conn.close()


@cli.command(help="Search for devices by name or IP address.")
@click.argument("database", type=click.Path(exists=True))
@click.argument("search_term")
@click.option(
    "--format",
    "-f",
    default="grid",
    type=click.Choice(["grid", "csv", "plain", "markdown"]),
    help="Output format.",
)
def search(database, search_term, format):
    """Search for devices by name or IP address."""

    conn = sqlite3.connect(database)
    conn.text_factory = safe_text_factory
    cursor = conn.cursor()

    cursor.execute(
        """
                   
                   
    SELECT name, ip_address, port, username, password, qr_file, qr_password, footer
    FROM devices
    WHERE name LIKE ? OR ip_address LIKE ?
    ORDER BY name
    """,
        (f"%{search_term}%", f"%{search_term}%"),
    )

    rows = cursor.fetchall()
    headers = [
        "name",
        "ip_address",
        "port",
        "username",
        "password",
        "qr_file",
        "qr_password",
        "footer",
    ]

    if not rows:
        click.echo(f"No devices found matching '{search_term}'.")
        return

    click.echo(tabulate(rows, headers=headers, tablefmt=format))
    click.echo(f"\nTotal matching devices: {len(rows)}")

    conn.close()


@cli.command(help="Export device data to CSV file.")
@click.argument("database", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def export_csv(database, output_file):
    """Export all device data to a CSV file."""
    import csv

    conn = sqlite3.connect(database)
    conn.text_factory = safe_text_factory
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT name, ip_address, port, username, password, qr_file, qr_password, footer
    FROM devices
    ORDER BY name
    """
    )

    rows = cursor.fetchall()
    headers = [
        "name",
        "ip_address",
        "port",
        "username",
        "password",
        "qr_file",
        "qr_password",
        "footer",
    ]

    if not rows:
        click.echo("No devices found in the database.")
        return

    with open(
        output_file,
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC, quotechar='"')
        writer.writerow(headers)
        writer.writerows(rows)

    click.echo(f"Exported {len(rows)} devices to {output_file}")

    conn.close()


if __name__ == "__main__":
    cli()
