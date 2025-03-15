# HikVision QR Export Utilities

A collection of tools for working with Hikvision QR codes, including encoding, decoding, and batch processing capabilities.

## Quick Start

```python
from encode_test import encode, encodeb64

# For domain names & IP,  (Base64)
domain = encodeb64("subdomain.domain.tld")

# For QR password, QR timestamp footer, device Username and passwords  (AES encrypted)
password = encode("secretpassword")

# Decode a single QR code
python hik_qr_export.py decode <qr_data>

# Process a directory of QR images
python hik_qr_export.py process-directory /path/to/images --output-dir ./processed --database devices.db

```

## Installation

```bash
$ git clone git@github.com:weaponizedautismdev/hqr_out.git
$ cd hik-qr-export
$ python3 -m venv venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- OpenCV (`cv2`) for QR image processing
- `qreader` for enhanced QR detection
- `pyaes` for AES encryption
- `click` for CLI interface
- `sqlite3` for device storage

## Developer Setup

### Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### Running Tests
```bash
python -m pytest tests/
```

### Common Issues
- QR detection may fail on low-resolution images
- Some non-UTF8 device names may cause decoding issues 
- Vietnamese Names did'nt like the UTF-8 in my testing use `.decode("unicode-escape")` instead
- AES decryption fails if username length > 16 chars

## Features

- Encode/decode Hikvision QR codes
- Process directories of QR code images
- Store device information in SQLite database
- Export data to CSV
- Handle multiple QR code format variations
- Support for legacy and modern QR formats

## Command Line Usage

```bash
# Decode a single QR code
python hik_qr_export.py decode <qr_data>

# Process a directory of QR images
python hik_qr_export.py process-directory /path/to/images --output-dir ./processed --database devices.db
```

## Technical Details

### Original Research and Implementation
<details>
<summary>View original research by maxim-smirnov</summary>

### QR Code Structure
Let's scan QR code I created for dummy camera and see what's inside.
`QRC03010003eJwrKnNNzC0vNy/yLogwD041LTUocg13tLW1ijRyK4mK8MpQM1DzDcmu9MlyNfJ3NqkA0rZqFgYGBmpqySWGuSYp5iEVwc5eHkZJHpnhWcFBQK04JVSsjJO8g5IC0gMSU6KcqsxczEuzjfQNA21tAQ4rKR0=`

Well, not so bad. 
We can clearly see the **Header** which is: `QRC03010003`

May be it's QR code structure format or name of the application which created this QR.

After the header we can see `base64` encoded data: `eJwrKnNNzC0vNy/yLogwD041LTUocg13tLW1ijRyK4mK8MpQM1DzDcmu9MlyNfJ3NqkA0rZqFgYGBmpqySWGuSYp5iEVwc5eHkZJHpnhWcFBQK04JVSsjJO8g5IC0gMSU6KcqsxczEuzjfQNA21tAQ4rKR0=`

Let's decode it and save the output to some file:
```bash
$ echo -n 'eJwrKnNNzC0vNy/yLogwD041LTUocg13tLW1ijRyK4mK8MpQM1DzDcmu9MlyNfJ3NqkA0rZqFgYGBmpqySWGuSYp5iEVwc5eHkZJHpnhWcFBQK04JVSsjJO8g5IC0gMSU6KcqsxczEuzjfQNA21tAQ4rKR0=' | base64 -d > /tmp/b64_decoded
```
So what's inside there...
```bash
$ cat /tmp/b64_decoded | hexdump -C
00000000  78 9c 2b 2a 73 4d cc 2d  2f 37 2f f2 2e 88 30 0f  |x.+*sM.-/7/...0.|
00000010  4e 35 2d 35 28 72 0d 77  b4 b5 b5 8a 34 72 2b 89  |N5-5(r.w....4r+.|
00000020  8a f0 ca 50 33 50 f3 0d  c9 ae f4 c9 72 35 f2 77  |...P3P......r5.w|
00000030  36 a9 00 d2 b6 6a 16 06  06 06 6a 6a c9 25 86 b9  |6....j....jj.%..|
00000040  26 29 e6 21 15 c1 ce 5e  1e 46 49 1e 99 e1 59 c1  |&).!...^.FI...Y.|
00000050  41 40 ad 38 25 54 ac 8c  93 bc 83 92 02 d2 03 12  |A@.8%T..........|
00000060  53 a2 9c aa cc 5c cc 4b  b3 8d f4 0d 03 6d 6d 01  |S....\.K.....mm.|
00000070  0e 2b 29 1d                                       |.+).|
00000074
$ file /tmp/b64_decoded
/tmp/b64_decoded: zlib compressed data
```
Not bad, but this compressed data has no header, so `zcat` will say that it's not gzip format.

I used python to decompress the data, but there are a lot of other ways to do that.
```python
>>> import base64
>>> import zlib
>>> zlib.decompress(base64.b64decode('eJwrKnNNzC0vNy/yLogwD041LTUocg13tLW1ijRyK4mK8MpQM1DzDcmu9MlyNfJ3NqkA0rZqFgYGBmpqySWGuSYp5iEVwc5eHkZJHpnhWcFBQK04JVSsjJO8g5IC0gMSU6KcqsxczEuzjfQNA21tAQ4rKR0='))
b'rvEamww7rKpX7Se5u0rEWA==:Y2FtZXJh&0&MTkyLjE2OC4xLjE=&8000&&ct1m4d7TxSCJH2bHiWjSRA==&ct1m4d7TxSCJH2bHiWjSRA==$:3bKRbPgPadZBz6D7uk2/1Q=='
```

We can clearly see some structure here. Let's try to decode it:

<table>
    <tr><th>Encoded</th><th>Decoded</th></tr>
    <tr><td><code>rvEamww7rKpX7Se5u0rEWA==</code></td><td><code>\xae\xf1\x1a\x9b\x0c;\xac\xaaW\xed'\xb9\xbbJ\xc4X</code></td></tr>
    <tr><th colspan="2"><code>:</code> separator</th>
    <tr><td><code>Y2FtZXJh</code></td><td><code>camera</code></td></tr>
    <tr><td colspan="2"><code>&</code> separator</td>
    <tr><td colspan="2"><code>0</code> not encoded</td></tr>
    <tr><td colspan="2"><code>&</code> separator</td>
    <tr><td><code>MTkyLjE2OC4xLjE=</code></td><td><code>192.168.1.1</code></td></tr>
    <tr><td colspan="2"><code>&</code> separator</td>
    <tr><td colspan="2"><code>8000</code> not encoded</td></tr>
    <tr><td colspan="2">empty field</td></tr>
    <tr><td colspan="2"><code>&</code> separator</td>
    <tr><td><code>ct1m4d7TxSCJH2bHiWjSRA==</code></td><td><code>r\xddf\xe1\xde\xd3\xc5 \x89\x1ff\xc7\x89h\xd2D</code></td></tr>
    <tr><td colspan="2"><code>&</code> separator</td>
    <tr><td><code>ct1m4d7TxSCJH2bHiWjSRA==</code></td><td><code>r\xddf\xe1\xde\xd3\xc5 \x89\x1ff\xc7\x89h\xd2D</code></td></tr>
    <tr><td colspan="2"><code>$</code> separator</td>
    <tr><th colspan="2"><code>:</code> separator</th>
    <tr><td><code>3bKRbPgPadZBz6D7uk2/1Q==</code></td><td><code>\xdd\xb2\x91l\xf8\x0fi\xd6A\xcf\xa0\xfb\xbaM\xbf\xd5</code></td></tr>
</table>

### Camera inside QR

We can already see the name of the camera: `camera`, IP address I put: `192.168.1.1`,
port: `8000` and also two identical data block one by one. Did you remember I put `admin`
for both fields `username` and `password`...

I created couple more QR codes for thw same camera with different export passwords
and saw that only parts of decoded data change:
`rvEamww7rKpX7Se5u0rEWA==` and `3bKRbPgPadZBz6D7uk2/1Q==` 
both of them separated from camera data by `:`.

Then I created QR export for two cameras and got that `$` sign separates cameras structures.

When I changed camera `username` **first** `ct1m4d7TxSCJH2bHiWjSRA==` changed.
When I changed camera `password` **second** `ct1m4d7TxSCJH2bHiWjSRA==` changed.

Ok, now we know where `username` and `password` for camera are located, 
also we know that our export password does not affect those encryption.

After that I started digging into the app itself.

### Application findings
Because I have created a lot of QR codes for cameras with different lengths of 
`username` and `password` I noticed that bytes count in decoded data always the same: `16`.

Looks like we're looking for block cipher! And what's most popular block cipher do we know?
**AES!**

### Final steps

Android application is loading native library with function we're looking for.

With Ghidra I continued to explore that native library.

Inside that library I found hardcoded key for AES encryption: `dkfj4593@#&*wlfm`, 
and discovered that it's AES with key size of `16` bytes and custom not standardised
number of rounds: `4`!

The export password is stored encrypted at first place between `:` separators.
But what's on the last place, after encrypted export password and all cameras?
It's encrypted timestamp of QR creation, that's how expiration mechanism made...

After that this program was created, so let's finally decode out QR data:
```bash
$ python hik_qr_export.py decode 'QRC03010003eJwrKnNNzC0vNy/yLogwD041LTUocg13tLW1ijRyK4mK8MpQM1DzDcmu9MlyNfJ3NqkA0rZqFgYGBmpqySWGuSYp5iEVwc5eHkZJHpnhWcFBQK04JVSsjJO8g5IC0gMSU6KcqsxczEuzjfQNA21tAQ4rKR0='
Data header: QRC03010003
Password used: 12Qweq24
QR code generated at: 1740175993 (2025-02-21T23:13:13)

Device Name: camera
IP Address: 192.168.1.1
Port: 8000
Username: admin
Password: admin
```

</details>

## Implementation Details

### QR Processing Tools

#### Directory Processor (`qr_directory_processor.py`)
- Uses Qreader & CV2 for improved QR detection
- Handles poor quality and damaged QRs
- Processes multiple image formats (jpg, png, gif)
- Automated file renaming with extracted passwords
- Database storage of device details

#### Database Schema
```sql
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
    );
```

### Variation Handling

Further research shows that there are variations in delimiters for both devices and fields.
- QR format changes based on OEM and age. 
- Header value is not static. Unsure of significancem, I have seen variations with the last char being 1, 2 or 3.
- QR password is optional.
- Footer Timestamp is optional and appears mostly on newer QR codes, it appears to govern access duration. 
  - It can be safely removed for clients that support older variations like ENS Vision, Alibi Witness 3.0, Guarding Vision.

#### QR Format Variations
```python
def handle_variations(decompressed_data: str) -> str:
    # Standardize delimeters
    return decompressed_data.replace(";", "$").replace(",", "&")
```

#### Optional Fields
```python
# Handle missing timestamps
if len(parts) < 3:
    footer = str(datetime.datetime.now().timestamp())

# Handle missing E2E password
if len(parts) == 1:
    e2e_password = "NoPassWD"
```

### CLI Reference

```bash
# Basic Usage
python hik_qr_export.py <command> [options]

# Commands
decode              # Decode single QR code
process-directory   # Batch process directory of QRs
export-csv         # Export database to CSV
search             # Search device database

# Options
--output-dir PATH      # Output directory for processed files
--database PATH        # SQLite database path
--quiet               # Suppress detailed output
--delete-originals    # Remove original files after processing
--extensions LIST     # File types to process (default: jpg,png,gif)
--rename-pattern STR  # Custom filename pattern for processed files
```

### Utility Scripts

#### Database Query Tool (`db_query.py`)
```bash
# List all devices
python db_query.py list-devices devices.db

# Search by IP or device name
python db_query.py search devices.db "192.168.1"

# Export filtered results
python db_query.py export-csv devices.db output.csv --filter "port=8000"
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[Add your license here]
