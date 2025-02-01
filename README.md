# Revenge CLI

Revenge CLI is a command-line tool for encrypting and decrypting files in a folder. It allows you to convert a folder into an encrypted binary file and vice versa.

## Features

- Encrypt a folder into a single binary file.
- Decrypt an encrypted binary file back into a folder.
- Generate and use a 256-bit AES encryption key.

## Requirements

- Python 3.x
- `revenge` module (Ensure you have this module installed or replace it with your own implementation)

## Installation

1. Clone the repository or download the script.
2. Ensure you have Python 3.x installed on your system.
3. Install any required dependencies (if any).

## Usage

### Command-line Arguments

- `mode`: Mode of operation. Use `encrypt` to convert a folder to an encrypted binary file, and `decrypt` to convert an encrypted binary file back to a folder.
- `target_path`: Path to the target folder (for encryption) or binary file (for decryption).
- `output_path`: Path to the output folder (for decryption) or binary file (for encryption).
- `--key`: (Optional) Path to the encryption key file. If not provided, a new key will be generated and saved in the output directory.

### Examples

#### Encrypt a Folder

```sh
# recommand
uv run revenge/cli.py encrypt /path/to/folder /path/to/output
# not verified
python revenge/cli.py encrypt /path/to/folder /path/to/output
```

This command will encrypt the contents of `/path/to/folder` into a binary file located at `/path/to/output/output.bin`. If no key is provided, a new key will be generated and saved as `encryption_key.bin` in the output directory.

#### Decrypt a Binary File

```sh
# recommand
uv run revenge/cli.py encrypt /path/to/folder /path/to/output
# not verified
python revenge/cli.py decrypt /path/to/output/output.bin /path/to/decrypted_folder --key /path/to/output/encryption_key.bin
```

This command will decrypt the binary file `/path/to/output/output.bin` into the folder `/path/to/decrypted_folder` using the key stored in `/path/to/output/encryption_key.bin`.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

## Contact

For any questions or inquiries, please contact [Your Name] at [Your Email].
