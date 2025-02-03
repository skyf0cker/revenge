import os
import argparse
from os.path import dirname, join
from revenge import Revenge
from posixpath import abspath
from posixpath import expanduser
import uvicorn
import server

def encrypt(args):
    target_path = abspath(expanduser(args.target))
    output_path = abspath(expanduser(args.output))
    meta_path = abspath(expanduser(args.metadata))

    if not os.path.exists(dirname(meta_path)):
        os.makedirs(dirname(meta_path))

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    key_path = abspath(expanduser(args.key)) if args.key else join(output_path, 'encryption_key.bin')

    if os.path.exists(key_path):
        with open(key_path, 'rb') as key_file:
            key = key_file.read()
    else:
        key = os.urandom(32)  # 256-bit key for AES-256
        # Save the key to a file
        with open(key_path, 'wb') as key_file:
            key_file.write(key)

    revenge = Revenge.encrypt_instance(target_path=target_path, output_path=join(output_path, 'output.bin'), key=key, metadata_path=meta_path)
    revenge._folder_to_binary()

def decrypt(args):
    output_path = abspath(expanduser(args.output))
    binary_path = abspath(expanduser(args.binary))
    key_path = abspath(expanduser(args.key))
    meta_path = abspath(expanduser(args.metadata))

    if not os.path.exists(key_path):
        raise ValueError("Encryption key file is required for decrypt mode.")

    if not os.path.exists(meta_path):
        raise ValueError("Metadata file is required for decrypt mode.")

    with open(key_path, 'rb') as key_file:
        key = key_file.read()

    revenge = Revenge.decrypt_instance(output_path=output_path, binary_path=binary_path, key=key, metadata_path=meta_path)
    revenge._binary_to_folder()

def split_binary_file(args):
    binary_path = abspath(expanduser(args.binary))
    output_path = abspath(expanduser(args.output))
    if not os.path.exists(output_path):
        os.mkdir(output_path)

    revenge = Revenge.split_instance(binary_path=binary_path, output_path=output_path)  # dummy key, not needed for split mode
    revenge._split_binary_file(chunk_size=args.chunk_size)

def reveal_binary_file(args):
    chunk_folder = abspath(expanduser(args.chunks))
    output_path = abspath(expanduser(args.output))

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    revenge = Revenge.reveal_instance(chunk_folder=chunk_folder, output_path=output_path)
    revenge._join_binary_chunks()

def start_server(args):
    uvicorn.run(server.app, host=args.host, port=args.port)

def main():
    parser = argparse.ArgumentParser(description="Encrypt and decrypt files in a folder.")
    subparsers = parser.add_subparsers(dest='mode')

    # Encrypt mode
    encrypt_parser = subparsers.add_parser('encrypt', help="Convert folder to encrypted binary.")
    encrypt_parser.add_argument('target', help="Path to the target folder.")
    encrypt_parser.add_argument('output', help="Path to the output folder.")
    encrypt_parser.add_argument('--key', help="Path to the encryption key file. If not provided, a new key will be generated and saved.")
    encrypt_parser.add_argument('--metadata', help="Path to metadata file.")
    encrypt_parser.set_defaults(func=encrypt)

    # Decrypt mode
    decrypt_parser = subparsers.add_parser('decrypt', help="Convert encrypted binary back to folder.")
    decrypt_parser.add_argument('binary', help="Path to the binary file.")
    decrypt_parser.add_argument('output', help="Path to the output folder.")
    decrypt_parser.add_argument('--key', help="Path to the encryption key file.")
    decrypt_parser.add_argument('--metadata', help="Path to the metadata file.")
    decrypt_parser.set_defaults(func=decrypt)

    # Split mode
    split_parser = subparsers.add_parser('split', help="Split the encrypted binary file into chunks.")
    split_parser.add_argument('binary', help="Path to the encrypted binary file.")
    split_parser.add_argument('output', help="Path to the output folder.")
    split_parser.add_argument('--chunk-size', type=int, default=1024 * 1024, help="Size of each chunk in bytes. Defaults to 1MB.")
    split_parser.set_defaults(func=split_binary_file)

    # Reveal mode
    reveal_parser = subparsers.add_parser('reveal', help="Join binary chunks back into the original file.")
    reveal_parser.add_argument('chunks', help="Path to the folder containing the binary chunks.")
    reveal_parser.add_argument('output', help="Path where the joined binary file will be saved.")
    reveal_parser.set_defaults(func=reveal_binary_file)

    # Server mode
    server_parser = subparsers.add_parser('server', help="Start the HTTP server.")
    server_parser.add_argument('--host', default='127.0.0.1', help="Host address to bind the server to.")
    server_parser.add_argument('--port', type=int, default=8000, help="Port to bind the server to.")
    server_parser.set_defaults(func=start_server)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
