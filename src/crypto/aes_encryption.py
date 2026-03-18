"""
AES-256 Encryption Module
Implements military-grade symmetric encryption for patient data files
"""

import os
import secrets
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class AESEncryption:
    """
    AES-256 Encryption Service
    
    Provides secure symmetric encryption for healthcare data files.
    Uses CBC mode with PKCS7 padding for security.
    """
    
    # AES-256 requires 32-byte keys
    KEY_SIZE = 32  # 256 bits
    BLOCK_SIZE = 16  # 128 bits (AES block size)
    
    def __init__(self):
        """Initialize AES encryption service"""
        pass
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a cryptographically secure random AES-256 key
        
        Returns:
            32-byte random key
            
        Security Note:
            Uses secrets module for cryptographically strong randomness
        """
        return secrets.token_bytes(AESEncryption.KEY_SIZE)
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """
        Encrypt data using AES-256-CBC
        
        Args:
            plaintext: Data to encrypt
            key: 32-byte AES-256 key
            
        Returns:
            (ciphertext, iv) - Encrypted data and initialization vector
            
        Example:
            >>> aes = AESEncryption()
            >>> key = aes.generate_key()
            >>> ciphertext, iv = aes.encrypt(b"Patient data", key)
        """
        if len(key) != AESEncryption.KEY_SIZE:
            raise ValueError(f"Key must be {AESEncryption.KEY_SIZE} bytes for AES-256")
        
        # Generate random IV (Initialization Vector)
        iv = get_random_bytes(AESEncryption.BLOCK_SIZE)
        
        # Create cipher in CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad plaintext to block size and encrypt
        padded_plaintext = pad(plaintext, AESEncryption.BLOCK_SIZE)
        ciphertext = cipher.encrypt(padded_plaintext)
        
        return ciphertext, iv
    
    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """
        Decrypt AES-256-CBC encrypted data
        
        Args:
            ciphertext: Encrypted data
            key: 32-byte AES-256 key
            iv: Initialization vector used during encryption
            
        Returns:
            Decrypted plaintext
            
        Raises:
            ValueError: If decryption fails (wrong key, corrupted data, etc.)
            
        Example:
            >>> plaintext = aes.decrypt(ciphertext, key, iv)
        """
        if len(key) != AESEncryption.KEY_SIZE:
            raise ValueError(f"Key must be {AESEncryption.KEY_SIZE} bytes for AES-256")
        
        if len(iv) != AESEncryption.BLOCK_SIZE:
            raise ValueError(f"IV must be {AESEncryption.BLOCK_SIZE} bytes")
        
        try:
            # Create cipher in CBC mode
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # Decrypt and remove padding
            padded_plaintext = cipher.decrypt(ciphertext)
            plaintext = unpad(padded_plaintext, AESEncryption.BLOCK_SIZE)
            
            return plaintext
            
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def encrypt_file(input_path: str, output_path: str, key: bytes) -> bytes:
        """
        Encrypt a file using AES-256
        
        Args:
            input_path: Path to plaintext file
            output_path: Path to save encrypted file
            key: 32-byte AES-256 key
            
        Returns:
            IV used for encryption (needed for decryption)
            
        File Format:
            The encrypted file contains only the ciphertext.
            IV is returned separately and should be stored with metadata.
            
        Example:
            >>> key = AESEncryption.generate_key()
            >>> iv = AESEncryption.encrypt_file("patient.txt", "patient.enc", key)
        """
        # Read plaintext file
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        
        # Encrypt
        ciphertext, iv = AESEncryption.encrypt(plaintext, key)
        
        # Write encrypted file
        with open(output_path, 'wb') as f:
            f.write(ciphertext)
        
        return iv
    
    @staticmethod
    def decrypt_file(input_path: str, output_path: str, key: bytes, iv: bytes):
        """
        Decrypt an AES-256 encrypted file
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to save decrypted file
            key: 32-byte AES-256 key
            iv: Initialization vector from encryption
            
        Example:
            >>> AESEncryption.decrypt_file("patient.enc", "patient.txt", key, iv)
        """
        # Read encrypted file
        with open(input_path, 'rb') as f:
            ciphertext = f.read()
        
        # Decrypt
        plaintext = AESEncryption.decrypt(ciphertext, key, iv)
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(plaintext)
    
    @staticmethod
    def encrypt_large_file(input_path: str, output_path: str, key: bytes, 
                          chunk_size: int = 64 * 1024) -> bytes:
        """
        Encrypt large files in chunks to avoid memory issues
        
        Args:
            input_path: Path to plaintext file
            output_path: Path to save encrypted file
            key: 32-byte AES-256 key
            chunk_size: Size of chunks to process (default: 64KB)
            
        Returns:
            IV used for encryption
            
        Note: For very large files (GB+), this streaming approach is recommended
        """
        if len(key) != AESEncryption.KEY_SIZE:
            raise ValueError(f"Key must be {AESEncryption.KEY_SIZE} bytes")
        
        # Generate IV
        iv = get_random_bytes(AESEncryption.BLOCK_SIZE)
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Process file in chunks
        with open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                while True:
                    chunk = f_in.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    
                    # Pad last chunk
                    if len(chunk) < chunk_size:
                        chunk = pad(chunk, AESEncryption.BLOCK_SIZE)
                    
                    encrypted_chunk = cipher.encrypt(chunk)
                    f_out.write(encrypted_chunk)
        
        return iv
    
    @staticmethod
    def decrypt_large_file(input_path: str, output_path: str, key: bytes, 
                          iv: bytes, chunk_size: int = 64 * 1024):
        """
        Decrypt large files in chunks
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to save decrypted file
            key: 32-byte AES-256 key
            iv: Initialization vector
            chunk_size: Size of chunks to process (default: 64KB)
        """
        if len(key) != AESEncryption.KEY_SIZE:
            raise ValueError(f"Key must be {AESEncryption.KEY_SIZE} bytes")
        
        if len(iv) != AESEncryption.BLOCK_SIZE:
            raise ValueError(f"IV must be {AESEncryption.BLOCK_SIZE} bytes")
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Get file size
        file_size = os.path.getsize(input_path)
        
        # Process file in chunks
        with open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                bytes_read = 0
                while bytes_read < file_size:
                    chunk = f_in.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    
                    decrypted_chunk = cipher.decrypt(chunk)
                    
                    # Remove padding from last chunk
                    if bytes_read + len(chunk) >= file_size:
                        decrypted_chunk = unpad(decrypted_chunk, AESEncryption.BLOCK_SIZE)
                    
                    f_out.write(decrypted_chunk)
                    bytes_read += len(chunk)


# Example usage and testing
if __name__ == "__main__":
    print("=== AES-256 Encryption Test ===\n")
    
    # Test 1: Basic encryption/decryption
    print("1. Basic Encryption/Decryption Test")
    aes = AESEncryption()
    
    # Generate key
    key = aes.generate_key()
    print(f"   Generated key: {key.hex()[:32]}... ({len(key)} bytes)")
    
    # Sample data
    original_data = b"Patient Name: John Doe\nDiagnosis: Hypertension\nTreatment: Medication prescribed"
    print(f"   Original data: {original_data[:50]}...")
    
    # Encrypt
    ciphertext, iv = aes.encrypt(original_data, key)
    print(f"   Encrypted: {ciphertext.hex()[:32]}... ({len(ciphertext)} bytes)")
    print(f"   IV: {iv.hex()}")
    
    # Decrypt
    decrypted_data = aes.decrypt(ciphertext, key, iv)
    print(f"   Decrypted: {decrypted_data[:50]}...")
    
    # Verify
    assert original_data == decrypted_data, "Decryption failed!"
    print("   ✓ Encryption/Decryption successful!\n")
    
    # Test 2: File encryption
    print("2. File Encryption Test")
    
    # Create sample file
    test_file = "test_patient_record.txt"
    encrypted_file = "test_patient_record.enc"
    decrypted_file = "test_patient_record_decrypted.txt"
    
    sample_content = """
    PATIENT MEDICAL RECORD
    ======================
    Patient ID: P12345
    Name: Jane Smith
    DOB: 1985-03-15
    
    Medical History:
    - Diabetes Type 2 (2020)
    - High Blood Pressure (2019)
    
    Current Medications:
    - Metformin 500mg twice daily
    - Lisinopril 10mg once daily
    
    Last Visit: 2024-01-15
    Next Appointment: 2024-02-15
    
    Notes: Patient responding well to treatment.
    """
    
    with open(test_file, 'w') as f:
        f.write(sample_content)
    
    print(f"   Created test file: {test_file}")
    
    # Encrypt file
    key = aes.generate_key()
    iv = aes.encrypt_file(test_file, encrypted_file, key)
    print(f"   ✓ File encrypted: {encrypted_file}")
    print(f"   IV: {iv.hex()}")
    
    # Decrypt file
    aes.decrypt_file(encrypted_file, decrypted_file, key, iv)
    print(f"   ✓ File decrypted: {decrypted_file}")
    
    # Verify
    with open(test_file, 'r') as f:
        original = f.read()
    with open(decrypted_file, 'r') as f:
        decrypted = f.read()
    
    assert original == decrypted, "File decryption failed!"
    print("   ✓ File content matches original!\n")
    
    # Cleanup
    os.remove(test_file)
    os.remove(encrypted_file)
    os.remove(decrypted_file)
    
    print("=== Test Complete ===")
