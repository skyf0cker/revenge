import os
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class Revenge:

    def __init__(self, target_path: str, output_path: str, key: bytes):
        self.target = target_path
        self.output_path = output_path
        self.metadata_path = output_path + '.meta'
        self.key = key

    def _encrypt_data(self, data: bytes) -> bytes:
        # Generate a random IV
        iv = os.urandom(16)
        # Create a cipher object
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
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        # Decrypt the data
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        # Unpad the data
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data

    def _folder_to_binary(self):
            # Check if the target path is a directory
            if not os.path.isdir(self.target):
                raise ValueError(f"The target path '{self.target}' is not a directory.")

            # Initialize an empty bytes object to store all binary data
            combined_binary_data = bytes()
            metadata = []

            # Iterate over all files in the target directory
            for root, _, files in os.walk(self.target):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Read each file in binary mode
                        with open(file_path, 'rb') as f:
                            binary_data = f.read()
                            # Append the binary data to the combined bytes object
                            combined_binary_data += binary_data
                            # Store the file name and its length in the metadata
                            relative_path = os.path.relpath(file_path, self.target)
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

            # Write the metadata to a separate file
            try:
                with open(self.metadata_path, 'w') as metadata_file:
                    json.dump(metadata, metadata_file)
                print(f"Metadata has been written to {self.metadata_path}")
            except Exception as e:
                print(f"Error writing to metadata file {self.metadata_path}: {e}")

    def _binary_to_folder(self):
        # Check if the target path is a directory
        if not os.path.isdir(self.target):
            raise ValueError(f"The target path '{self.target}' is not a directory.")

        # Read the metadata file
        try:
            with open(self.metadata_path, 'r') as metadata_file:
                metadata = json.load(metadata_file)
        except Exception as e:
            print(f"Error reading metadata file {self.metadata_path}: {e}")
            return

        # Read the encrypted binary file
        try:
            with open(self.output_path, 'rb') as binary_file:
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

            file_path = os.path.join(self.target, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            try:
                with open(file_path, 'wb') as output_file:
                    output_file.write(file_data)
                print(f"File {file_path} has been created.")
            except Exception as e:
                print(f"Error writing to file {file_path}: {e}")
# Example usage:
# revenge = Revenge(target_path='/path/to/folder', output_path='/path/to/output.bin')
# revenge._folder_to_binary()
# revenge._binary_to_folder()
