import os
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from typing import Optional

class Revenge:

    def __init__(
        self,
        target_path: Optional[str] = None,
        output_path: Optional[str] = None,
        binary_path: Optional[str] = None,
        chunks_path: Optional[str] = None,
        key: Optional[bytes] = None,
        metadata_path: Optional[str] = None,
    ):
        self.target_path = target_path
        self.output_path = output_path
        self.key = key
        self.metadata_path = metadata_path
        self.binary_path = binary_path
        self.chunks_path = chunks_path

    @classmethod
    def encrypt_instance(cls, target_path: str, output_path: str, metadata_path: str, key: Optional[bytes] = None):
        return cls(target_path=target_path, output_path=output_path, key=key, metadata_path=metadata_path)

    @classmethod
    def decrypt_instance(cls, output_path: str, binary_path: str, metadata_path: str, key: bytes):
        return cls(output_path=output_path, binary_path=binary_path, key=key, metadata_path=metadata_path)

    @classmethod
    def split_instance(cls, binary_path: str, output_path: str):
        return cls(target_path=output_path, output_path=binary_path)

    @classmethod
    def reveal_instance(cls, chunk_folder: str, output_path: str):
        return cls(chunks_path=chunk_folder, output_path=output_path)

    def _encrypt_data(self, data: bytes) -> bytes:
        # Generate a random IV
        iv = os.urandom(16)
        # Create a cipher object
        if self.key is None:
            raise ValueError("Encryption key is required for encryption.")

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        # Pad the data
        padder = padding.PKCS7(128).padder()  # AES block size is 128 bits
        padded_data = padder.update(data) + padder.finalize()
        # Encrypt the data
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        # Return the IV and encrypted data
        return iv + encrypted_data

    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        # Extract the IV
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        # Create a cipher object
        if self.key is None:
            raise ValueError("Encryption key is required for decryption.")

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        # Decrypt the data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        # Unpad the data
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

    def _folder_to_binary(self):
        if not self.target_path:
            raise ValueError("Target path is required for folder to binary conversion.")

        if not self.output_path:
            raise ValueError("Output path is required for folder to binary conversion.")

        # Check if the target path is a directory
        if not os.path.isdir(self.target_path):
            raise ValueError(f"The target path '{self.target_path}' is not a directory.")

        # Initialize an empty bytes object to store all binary data
        combined_binary_data = bytes()
        metadata = []

        # Iterate over all files in the target directory
        for root, _, files in os.walk(self.target_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Read each file in binary mode
                    with open(file_path, 'rb') as f:
                        binary_data = f.read()
                        # Append the binary data to the combined bytes object
                        combined_binary_data += binary_data
                        # Store the file name and its length in the metadata
                        relative_path = os.path.relpath(file_path, self.target_path)
                        metadata.append({'file_name': relative_path, 'length': len(binary_data)})
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

        # Encrypt the combined binary data
        encrypted_data = self._encrypt_data(combined_binary_data)

        # Write the encrypted binary data to the output file
        try:
            with open(self.output_path, 'wb') as output_file:
                output_file.write(encrypted_data)
            print(f"All files have been combined and encrypted into {self.output_path}")
        except Exception as e:
            print(f"Error writing to output file {self.output_path}: {e}")

        if self.metadata_path is None:
            raise ValueError("Metadata path is required for folder to binary conversion.")

        # Write the metadata to a separate file
        try:
            with open(self.metadata_path, 'w') as metadata_file:
                json.dump(metadata, metadata_file)
            print(f"Metadata has been written to {self.metadata_path}")
        except Exception as e:
            print(f"Error writing to metadata file {self.metadata_path}: {e}")

    def _binary_to_folder(self):
        if not self.binary_path:
            raise ValueError("Binary path is required for binary to folder conversion.")

        if not self.output_path:
            raise ValueError("Output path is required for binary to folder conversion.")

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

        if not os.path.exists(self.binary_path):
            raise ValueError(f"The binary path '{self.binary_path}' does not exist.")

        if self.metadata_path is None:
            raise ValueError("Metadata path is required for binary to folder conversion.")

        # Read the metadata file
        try:
            with open(self.metadata_path, 'r') as metadata_file:
                metadata = json.load(metadata_file)
        except Exception as e:
            print(f"Error reading metadata file {self.metadata_path}: {e}")
            return

        # Read the encrypted binary file
        try:
            with open(self.binary_path, 'rb') as binary_file:
                encrypted_data = binary_file.read()
        except Exception as e:
            print(f"Error reading binary file {self.output_path}: {e}")
            return

        # Decrypt the binary data
        binary_data = self._decrypt_data(encrypted_data)

        # Write each chunk to a separate file in the target directory
        offset = 0
        for entry in metadata:
            file_name = entry['file_name']
            length = entry['length']
            file_data = binary_data[offset:offset + length]
            offset += length

            file_path = os.path.join(self.output_path, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            try:
                with open(file_path, 'wb') as output_file:
                    output_file.write(file_data)
                print(f"File {file_path} has been created.")
            except Exception as e:
                print(f"Error writing to file {file_path}: {e}")

    def _chunk_file(self, file_path, chunk_size: int = 1024 * 1024):
        """
        Generator that yields chunks of a file.

        Args:
            file_path (str): The path to the file.
            chunk_size (int): The size of each chunk in bytes. Defaults to 1MB.
        """
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def _split_binary_file(self, chunk_size: int = 1024 * 1024):
        """
        Split the binary file into chunks and save them into a folder in the target path.

        Args:
        chunk_size (int): The size of each chunk in bytes. Defaults to 1MB.
        """
        if not self.output_path:
            raise ValueError("Output path is required for splitting the binary file.")

        if not self.target_path:
            raise ValueError("Target path is required for splitting the binary file.")

        # Check if the output path exists
        if not os.path.exists(self.output_path):
            raise ValueError(f"The output path '{self.output_path}' does not exist.")

        # Create a chunk folder in the target path
        chunk_folder = os.path.join(self.target_path, "chunks")
        os.makedirs(chunk_folder, exist_ok=True)

        # Initialize the chunk counter
        chunk_counter = 0

        # Read the binary file in chunks using the generator
        for chunk in self._chunk_file(self.output_path, chunk_size):
            chunk_file = os.path.join(chunk_folder, f"chunk_{chunk_counter:06d}.bin")
            try:
                with open(chunk_file, 'wb') as chunk_file_handle:
                    chunk_file_handle.write(chunk)
                    print(f"Chunk {chunk_counter + 1} has been saved to {chunk_file}")
                    chunk_counter += 1
            except Exception as e:
                print(f"Error writing chunk {chunk_counter + 1} to {chunk_file}: {e}")

    def _join_binary_chunks(self):
        """
        Join the binary chunks back into the original binary file.

        Raises:
        ValueError: If the chunk folder or output path is not specified and cannot be determined from the instance variables.
        """
        if self.chunks_path is None:
            raise ValueError("Chunks path is not specified.")

        if self.output_path is None:
            raise ValueError("Output path is not specified.")

        if not os.path.exists(self.chunks_path):
            raise ValueError(f"The chunk folder '{self.chunks_path}' does not exist.")

        # Get the list of chunk files in the chunk folder
        chunk_files = [os.path.join(self.chunks_path, file) for file in os.listdir(self.chunks_path) if file.startswith("chunk_") and file.endswith(".bin")]
        chunk_files.sort()

        # Check if there are any chunk files
        if not chunk_files:
            raise ValueError(f"No chunk files found in the chunk folder '{self.chunks_path}'.")

        # Read and write each chunk file to the output file
        with open(self.output_path, 'wb') as output_file:
            for chunk_file in chunk_files:
                try:
                    with open(chunk_file, 'rb') as chunk:
                        chunk_data = chunk.read()
                        output_file.write(chunk_data)
                        print(f"Chunk {chunk_file} has been written to {self.output_path}.")
                except Exception as e:
                    print(f"Error writing chunk {chunk_file} to {self.output_path}: {e}")

        print(f"All chunks have been joined into {self.output_path}.")
