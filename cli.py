import os
import argparse
from os.path import join
from revenge import Revenge
from posixpath import abspath
from posixpath import expanduser

def main():
    parser = argparse.ArgumentParser(description="Encrypt and decrypt files in a folder.")
    parser.add_argument('mode', choices=['encrypt', 'decrypt'], help="Mode of operation: 'encrypt' to convert folder to encrypted binary, 'decrypt' to convert encrypted binary back to folder.")
    parser.add_argument('target_path', help="Path to the target folder or binary file.")
    parser.add_argument('output_path', help="Path to the output folder or binary file.")
    parser.add_argument('--key', help="Path to the encryption key file. If not provided, a new key will be generated and saved.")

    args = parser.parse_args()

    # Resolve paths
    target_path = abspath(expanduser(args.target_path))
    output_path = abspath(expanduser(args.output_path))
    key_path = abspath(expanduser(args.key)) if args.key else join(output_path, 'encryption_key.bin')

    # Create the output directory if it does not exist
    os.makedirs(output_path, exist_ok=True)

    if os.path.exists(key_path):
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
    else:
        key = os.urandom(32)  # 256-bit key for AES-256
        # Save the key to a file
        with open(key_path, 'wb') as key_file:
            key_file.write(key)

    revenge = Revenge(target_path=target_path, output_path=join(output_path, 'output.bin'), key=key)

    if args.mode == 'encrypt':
        revenge._folder_to_binary()
    elif args.mode == 'decrypt':
        revenge._binary_to_folder()

if __name__ == '__main__':
    main()
