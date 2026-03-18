"""
SHA-3 Hash Integrity Verification Module
Ensures file integrity before decryption
"""

import hashlib
from typing import Optional


class IntegrityChecker:
    """
    File Integrity Verification using SHA-3
    
    Provides cryptographic hashing to ensure files haven't been tampered with.
    Uses SHA-3 (256-bit) for collision resistance and security.
    """
    
    HASH_ALGORITHM = 'sha3_256'
    HASH_SIZE = 32  # 256 bits = 32 bytes
    
    def __init__(self):
        """Initialize integrity checker"""
        pass
    
    @staticmethod
    def compute_hash(data: bytes) -> str:
        """
        Compute SHA-3 hash of data
        
        Args:
            data: Binary data to hash
            
        Returns:
            Hexadecimal hash string
            
        Example:
            >>> checker = IntegrityChecker()
            >>> hash_value = checker.compute_hash(b"Patient data")
        """
        hasher = hashlib.sha3_256()
        hasher.update(data)
        return hasher.hexdigest()
    
    @staticmethod
    def compute_file_hash(file_path: str, chunk_size: int = 8192) -> str:
        """
        Compute SHA-3 hash of a file
        
        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read (for large files)
            
        Returns:
            Hexadecimal hash string
            
        Example:
            >>> hash_value = IntegrityChecker.compute_file_hash("patient.enc")
        """
        hasher = hashlib.sha3_256()
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    @staticmethod
    def verify_hash(data: bytes, expected_hash: str) -> bool:
        """
        Verify data integrity against expected hash
        
        Args:
            data: Binary data to verify
            expected_hash: Expected hash value (hex string)
            
        Returns:
            True if hash matches, False otherwise
            
        Example:
            >>> is_valid = checker.verify_hash(encrypted_data, stored_hash)
        """
        computed_hash = IntegrityChecker.compute_hash(data)
        return computed_hash.lower() == expected_hash.lower()
    
    @staticmethod
    def verify_file_hash(file_path: str, expected_hash: str) -> bool:
        """
        Verify file integrity against expected hash
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value (hex string)
            
        Returns:
            True if hash matches, False otherwise
            
        Example:
            >>> is_valid = IntegrityChecker.verify_file_hash("patient.enc", hash_value)
        """
        computed_hash = IntegrityChecker.compute_file_hash(file_path)
        return computed_hash.lower() == expected_hash.lower()
    
    @staticmethod
    def create_integrity_tag(data: bytes, metadata: str = "") -> dict:
        """
        Create integrity tag with hash and metadata
        
        Args:
            data: Binary data
            metadata: Optional metadata (e.g., timestamp, file info)
            
        Returns:
            Dictionary with hash, algorithm, and metadata
            
        Example:
            >>> tag = checker.create_integrity_tag(encrypted_data, "patient_001")
        """
        return {
            'hash': IntegrityChecker.compute_hash(data),
            'algorithm': IntegrityChecker.HASH_ALGORITHM,
            'metadata': metadata,
            'size': len(data)
        }
    
    @staticmethod
    def verify_integrity_tag(data: bytes, integrity_tag: dict) -> tuple[bool, Optional[str]]:
        """
        Verify data against integrity tag
        
        Args:
            data: Binary data to verify
            integrity_tag: Integrity tag from create_integrity_tag()
            
        Returns:
            (is_valid, error_message)
            
        Example:
            >>> is_valid, error = checker.verify_integrity_tag(data, tag)
            >>> if not is_valid:
            ...     print(f"Integrity check failed: {error}")
        """
        # Verify algorithm
        if integrity_tag.get('algorithm') != IntegrityChecker.HASH_ALGORITHM:
            return False, f"Algorithm mismatch: expected {IntegrityChecker.HASH_ALGORITHM}"
        
        # Verify size
        if integrity_tag.get('size') != len(data):
            return False, f"Size mismatch: expected {integrity_tag.get('size')}, got {len(data)}"
        
        # Verify hash
        computed_hash = IntegrityChecker.compute_hash(data)
        expected_hash = integrity_tag.get('hash', '')
        
        if computed_hash.lower() != expected_hash.lower():
            return False, "Hash mismatch: data has been modified"
        
        return True, None
    
    @staticmethod
    def hmac_verify(data: bytes, key: bytes, expected_hmac: str) -> bool:
        """
        Verify HMAC for authenticated encryption (optional enhancement)
        
        Args:
            data: Binary data
            key: Secret key for HMAC
            expected_hmac: Expected HMAC value
            
        Returns:
            True if HMAC matches, False otherwise
        """
        import hmac
        computed_hmac = hmac.new(key, data, hashlib.sha3_256).hexdigest()
        return hmac.compare_digest(computed_hmac, expected_hmac)


# Example usage and testing
if __name__ == "__main__":
    print("=== SHA-3 Integrity Checker Test ===\n")
    
    checker = IntegrityChecker()
    
    # Test 1: Basic hash computation
    print("1. Basic Hash Computation")
    sample_data = b"Patient ID: P12345\nDiagnosis: Hypertension"
    hash1 = checker.compute_hash(sample_data)
    print(f"   Data: {sample_data}")
    print(f"   SHA-3 Hash: {hash1}")
    print(f"   Hash Length: {len(hash1)} characters ({len(hash1)//2} bytes)\n")
    
    # Test 2: Hash verification
    print("2. Hash Verification")
    
    # Verify correct data
    is_valid = checker.verify_hash(sample_data, hash1)
    print(f"   Original data verification: {'✓ VALID' if is_valid else '✗ INVALID'}")
    
    # Verify modified data
    modified_data = b"Patient ID: P12345\nDiagnosis: Diabetes"  # Changed diagnosis
    is_valid = checker.verify_hash(modified_data, hash1)
    print(f"   Modified data verification: {'✓ VALID' if is_valid else '✗ INVALID (Expected)'}\n")
    
    # Test 3: File integrity
    print("3. File Integrity Check")
    
    import os
    test_file = "test_integrity.txt"
    
    # Create test file
    with open(test_file, 'w') as f:
        f.write("Confidential patient data\nMust not be tampered with")
    
    # Compute hash
    file_hash = checker.compute_file_hash(test_file)
    print(f"   File hash: {file_hash}")
    
    # Verify integrity
    is_valid = checker.verify_file_hash(test_file, file_hash)
    print(f"   Integrity check: {'✓ VALID' if is_valid else '✗ INVALID'}")
    
    # Modify file
    with open(test_file, 'a') as f:
        f.write("\nTampered data")
    
    # Verify again
    is_valid = checker.verify_file_hash(test_file, file_hash)
    print(f"   Integrity after modification: {'✓ VALID' if is_valid else '✗ INVALID (Expected)'}")
    
    # Cleanup
    os.remove(test_file)
    print()
    
    # Test 4: Integrity tags
    print("4. Integrity Tag System")
    
    encrypted_data = b"Encrypted patient record..."
    
    # Create tag
    tag = checker.create_integrity_tag(encrypted_data, "patient_P12345_cardiology")
    print(f"   Created integrity tag:")
    print(f"   - Hash: {tag['hash'][:32]}...")
    print(f"   - Algorithm: {tag['algorithm']}")
    print(f"   - Metadata: {tag['metadata']}")
    print(f"   - Size: {tag['size']} bytes")
    
    # Verify tag
    is_valid, error = checker.verify_integrity_tag(encrypted_data, tag)
    print(f"   Verification: {'✓ VALID' if is_valid else f'✗ INVALID: {error}'}")
    
    # Verify with tampered data
    tampered_data = b"Tampered patient record..."
    is_valid, error = checker.verify_integrity_tag(tampered_data, tag)
    print(f"   Tampered data: {'✓ VALID' if is_valid else f'✗ INVALID: {error}'}\n")
    
    print("=== Test Complete ===")
