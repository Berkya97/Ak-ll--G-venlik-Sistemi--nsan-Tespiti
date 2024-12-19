from cryptography.fernet import Fernet
import os

class SecurityEncryption:
    def __init__(self, key_file="security.key"):
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.key)
        
        self.cipher_suite = Fernet(self.key)
        
    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = self.cipher_suite.encrypt(file_data)
        
        with open(file_path + '.encrypted', 'wb') as f:
            f.write(encrypted_data)
            
    def decrypt_file(self, encrypted_file_path):
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_data = self.cipher_suite.decrypt(encrypted_data)
        
        output_path = encrypted_file_path.replace('.encrypted', '.decrypted')
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
