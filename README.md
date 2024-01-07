This is a test prib=vate repo for my ALX portfolio project


#!/usr/bin/env python3

import secrets

def generate_secret_key():
    # Generate a random key with 32 bytes (256 bits)
    secret_key = secrets.token_hex(32)
    return secret_key

def save_key_to_file(key, file_path):
    with open(file_path, 'w') as file:
        file.write(key)

if __name__ == "__main__":
    key = generate_secret_key()
    file_path = "/home/sirdom247/secret_keys/generated_keys.txt"  # Update with your actual desktop path
    save_key_to_file(key, file_path)
    print(f"Generated Secret Key and saved to: {file_path}")
