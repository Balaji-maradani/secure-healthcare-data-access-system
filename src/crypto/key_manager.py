"""
Cryptographic Key Management Module
Secure key generation and management
"""

import secrets
import os
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
import hashlib


class KeyManager:
    """
    Secure Key Management System
    
    Handles generation, storage, and lifecycle management of cryptographic keys.
    """
    
    def __init__(self, keys_directory: str = "storage/keys"):
        """
        Initialize key manager
        
        Args:
            keys_directory: Directory to store keys (should be encrypted in production)
        """
        self.keys_directory = keys_directory
        os.makedirs(keys_directory, exist_ok=True)
        
        # Set restrictive permissions on keys directory
        try:
            os.chmod(keys_directory, 0o700)
        except:
            pass  # Windows doesn't support Unix permissions
    
    @staticmethod
    def generate_aes_key() -> bytes:
        """
        Generate cryptographically secure AES-256 key
        
        Returns:
            32-byte random key
        """
        return secrets.token_bytes(32)
    
    @staticmethod
    def generate_key_id() -> str:
        """
        Generate unique key identifier
        
        Returns:
            Unique key ID (UUID-like)
        """
        return secrets.token_hex(16)
    
    def store_key(self, key_id: str, key_data: bytes, metadata: Dict = None) -> str:
        """
        Store key with metadata
        
        Args:
            key_id: Unique key identifier
            key_data: Key data to store
            metadata: Optional metadata (purpose, expiry, etc.)
            
        Returns:
            Path to stored key file
            
        Security Note:
            In production, encrypt keys before storage using HSM or key wrapping
        """
        key_path = os.path.join(self.keys_directory, f"{key_id}.key")
        metadata_path = os.path.join(self.keys_directory, f"{key_id}.meta")
        
        # Store key (WARNING: Should be encrypted in production)
        with open(key_path, 'wb') as f:
            f.write(key_data)
        
        # Store metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'key_id': key_id,
            'created_at': datetime.now().isoformat(),
            'size': len(key_data)
        })
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Set restrictive permissions
        try:
            os.chmod(key_path, 0o600)
            os.chmod(metadata_path, 0o600)
        except:
            pass
        
        return key_path
    
    def retrieve_key(self, key_id: str) -> Optional[bytes]:
        """
        Retrieve key by ID
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key data or None if not found
        """
        key_path = os.path.join(self.keys_directory, f"{key_id}.key")
        
        if not os.path.exists(key_path):
            return None
        
        with open(key_path, 'rb') as f:
            return f.read()
    
    def get_key_metadata(self, key_id: str) -> Optional[Dict]:
        """
        Get key metadata
        
        Args:
            key_id: Key identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata_path = os.path.join(self.keys_directory, f"{key_id}.meta")
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def delete_key(self, key_id: str) -> bool:
        """
        Securely delete key
        
        Args:
            key_id: Key identifier
            
        Returns:
            True if deleted, False if not found
            
        Security Note:
            Should overwrite key data before deletion in production
        """
        key_path = os.path.join(self.keys_directory, f"{key_id}.key")
        metadata_path = os.path.join(self.keys_directory, f"{key_id}.meta")
        
        deleted = False
        
        if os.path.exists(key_path):
            # Secure deletion: overwrite before removing
            file_size = os.path.getsize(key_path)
            with open(key_path, 'wb') as f:
                f.write(secrets.token_bytes(file_size))
            os.remove(key_path)
            deleted = True
        
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            deleted = True
        
        return deleted
    
    def list_keys(self) -> list[Dict]:
        """
        List all stored keys with metadata
        
        Returns:
            List of key metadata dictionaries
        """
        keys = []
        
        for filename in os.listdir(self.keys_directory):
            if filename.endswith('.meta'):
                key_id = filename[:-5]  # Remove .meta extension
                metadata = self.get_key_metadata(key_id)
                if metadata:
                    keys.append(metadata)
        
        return keys
    
    def rotate_key(self, old_key_id: str) -> tuple[str, bytes]:
        """
        Rotate key (generate new key, mark old as deprecated)
        
        Args:
            old_key_id: ID of key to rotate
            
        Returns:
            (new_key_id, new_key_data)
        """
        # Get old key metadata
        old_metadata = self.get_key_metadata(old_key_id)
        
        # Generate new key
        new_key_id = self.generate_key_id()
        new_key_data = self.generate_aes_key()
        
        # Store new key
        new_metadata = old_metadata.copy() if old_metadata else {}
        new_metadata['rotated_from'] = old_key_id
        new_metadata['rotation_date'] = datetime.now().isoformat()
        
        self.store_key(new_key_id, new_key_data, new_metadata)
        
        # Mark old key as deprecated (don't delete yet for re-encryption)
        if old_metadata:
            old_metadata['status'] = 'deprecated'
            old_metadata['deprecated_at'] = datetime.now().isoformat()
            old_metadata['replaced_by'] = new_key_id
            
            metadata_path = os.path.join(self.keys_directory, f"{old_key_id}.meta")
            with open(metadata_path, 'w') as f:
                json.dump(old_metadata, f, indent=2)
        
        return new_key_id, new_key_data
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None, 
                                 iterations: int = 100000) -> tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: User password
            salt: Salt for key derivation (generated if None)
            iterations: Number of iterations (higher = more secure but slower)
            
        Returns:
            (derived_key, salt)
            
        Example:
            >>> key, salt = KeyManager.derive_key_from_password("user_password")
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=32
        )
        
        return key, salt
    
    def export_key(self, key_id: str, export_password: str) -> bytes:
        """
        Export key encrypted with password
        
        Args:
            key_id: Key to export
            export_password: Password to encrypt export
            
        Returns:
            Encrypted key bundle
        """
        # Retrieve key
        key_data = self.retrieve_key(key_id)
        if not key_data:
            raise ValueError(f"Key {key_id} not found")
        
        metadata = self.get_key_metadata(key_id)
        
        # Derive encryption key from password
        encryption_key, salt = self.derive_key_from_password(export_password)
        
        # Encrypt key data
        from .aes_encryption import AESEncryption
        ciphertext, iv = AESEncryption.encrypt(key_data, encryption_key)
        
        # Create export bundle
        export_bundle = {
            'key_id': key_id,
            'ciphertext': ciphertext.hex(),
            'iv': iv.hex(),
            'salt': salt.hex(),
            'metadata': metadata,
            'export_version': '1.0'
        }
        
        return json.dumps(export_bundle).encode('utf-8')
    
    def import_key(self, encrypted_bundle: bytes, import_password: str) -> str:
        """
        Import encrypted key
        
        Args:
            encrypted_bundle: Encrypted key bundle from export_key()
            import_password: Password to decrypt import
            
        Returns:
            Imported key ID
        """
        # Parse bundle
        bundle = json.loads(encrypted_bundle.decode('utf-8'))
        
        # Extract components
        ciphertext = bytes.fromhex(bundle['ciphertext'])
        iv = bytes.fromhex(bundle['iv'])
        salt = bytes.fromhex(bundle['salt'])
        
        # Derive decryption key
        decryption_key, _ = self.derive_key_from_password(import_password, salt)
        
        # Decrypt key data
        from .aes_encryption import AESEncryption
        key_data = AESEncryption.decrypt(ciphertext, decryption_key, iv)
        
        # Store imported key
        key_id = bundle['key_id']
        metadata = bundle.get('metadata', {})
        metadata['imported_at'] = datetime.now().isoformat()
        
        self.store_key(key_id, key_data, metadata)
        
        return key_id


# Example usage and testing
if __name__ == "__main__":
    print("=== Key Manager Test ===\n")
    
    # Initialize key manager
    km = KeyManager("test_keys")
    
    # Test 1: Generate and store key
    print("1. Key Generation and Storage")
    key_id = km.generate_key_id()
    aes_key = km.generate_aes_key()
    print(f"   Generated key ID: {key_id}")
    print(f"   Generated AES key: {aes_key.hex()[:32]}... ({len(aes_key)} bytes)")
    
    metadata = {
        'purpose': 'patient_records',
        'department': 'cardiology',
        'owner': 'admin'
    }
    
    km.store_key(key_id, aes_key, metadata)
    print(f"   ✓ Key stored with metadata\n")
    
    # Test 2: Retrieve key
    print("2. Key Retrieval")
    retrieved_key = km.retrieve_key(key_id)
    print(f"   Retrieved key: {retrieved_key.hex()[:32]}...")
    assert retrieved_key == aes_key, "Key mismatch!"
    print(f"   ✓ Key matches original\n")
    
    # Test 3: Get metadata
    print("3. Key Metadata")
    stored_metadata = km.get_key_metadata(key_id)
    print(f"   Metadata: {json.dumps(stored_metadata, indent=6)}\n")
    
    # Test 4: List keys
    print("4. List All Keys")
    all_keys = km.list_keys()
    print(f"   Found {len(all_keys)} key(s)")
    for key_meta in all_keys:
        print(f"   - {key_meta['key_id']}: {key_meta.get('purpose', 'N/A')}\n")
    
    # Test 5: Key rotation
    print("5. Key Rotation")
    new_key_id, new_key = km.rotate_key(key_id)
    print(f"   Old key ID: {key_id}")
    print(f"   New key ID: {new_key_id}")
    print(f"   ✓ Key rotated\n")
    
    # Test 6: Password-based key derivation
    print("6. Password-Based Key Derivation")
    password = "secure_password_123"
    derived_key, salt = km.derive_key_from_password(password)
    print(f"   Password: {password}")
    print(f"   Derived key: {derived_key.hex()[:32]}...")
    print(f"   Salt: {salt.hex()[:32]}...\n")
    
    # Test 7: Key export/import
    print("7. Key Export/Import")
    export_password = "export_password_456"
    
    # Export
    encrypted_bundle = km.export_key(new_key_id, export_password)
    print(f"   ✓ Key exported ({len(encrypted_bundle)} bytes)")
    
    # Delete key
    km.delete_key(new_key_id)
    print(f"   ✓ Key deleted")
    
    # Import
    imported_key_id = km.import_key(encrypted_bundle, export_password)
    print(f"   ✓ Key imported: {imported_key_id}\n")
    
    # Cleanup
    import shutil
    shutil.rmtree("test_keys")
    
    print("=== Test Complete ===")
