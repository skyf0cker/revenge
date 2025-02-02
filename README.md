<div align="center">
    <img alt="logo" width="120" src="https://raw.githubusercontent.com/skyf0cker/revenge/refs/heads/main/images/logo.svg" />
    <h1>Revenge</h1>
</div>

Revenge CLI is a command-line tool for encrypting and decrypting files in a folder. It allows you to convert a folder into an encrypted binary file and vice versa.

## Features

* Encrypt a folder into a single binary file.
* Decrypt an encrypted binary file back into a folder.
* Split an encrypted binary file into chunks.
* Reveal binary chunks back into the original file.
* Generate and use a 256-bit AES encryption key.

## Requirements

* Python 3.x

## Installation

1. Clone the repository or download the script.
2. Ensure you have Python 3.x installed on your system.
3. Install any required dependencies (if any).

## Usage

### Command-line Arguments

The following modes are available:

* `encrypt`: Convert a folder to an encrypted binary file.
* `decrypt`: Convert an encrypted binary file back to a folder.
* `split`: Split an encrypted binary file into chunks.
* `reveal`: Join binary chunks back into the original file.

### Modes

#### Encrypt Mode

* `target`: Path to the target folder.
* `output`: Path to the output folder.
* `--key`: (Optional) Path to the encryption key file. If not provided, a new key will be generated and saved in the output directory.
* `--metadata`: Path to metadata file.

Example:
```sh
python revenge/cli.py encrypt /path/to/folder /path/to/output --key /path/to/key --metadata /path/to/metadata
```

#### Decrypt Mode

* `binary`: Path to the binary file.
* `output`: Path to the output folder.
* `--key`: Path to the encryption key file.
* `--metadata`: Path to metadata file.

Example:
```sh
python revenge/cli.py decrypt /path/to/binary /path/to/output --key /path/to/key --metadata /path/to/metadata
```

#### Split Mode

* `binary`: Path to the encrypted binary file.
* `output`: Path to the output folder.
* `--chunk-size`: Size of each chunk in bytes. Defaults to 1MB.

Example:
```sh
python revenge/cli.py split /path/to/binary /path/to/output --chunk-size 1048576
```

#### Reveal Mode

* `chunks`: Path to the folder containing the binary chunks.
* `output`: Path where the joined binary file will be saved.

Example:
```sh
python revenge/cli.py reveal /path/to/chunks /path/to/output
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.
