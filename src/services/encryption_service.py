"""
Hybrid Encryption Service
Combines AES-256 for data encryption and CP-ABE for key protection
"""

import os
import secrets
from typing import Dict, Optional
from datetime import datetime

from ..crypto.aes_encryption import AESEncryption
from ..crypto.cpabe import CPABEEngine
from ..crypto.hash_integrity import IntegrityChecker
from ..crypto.key_manager import KeyManager
from ..models.encrypted_file import EncryptedFile


class EncryptionService:
    """
    Hybrid Encryption Service
    
    Encrypts patient files using AES-256, then protects the AES key
    using CP-ABE with embedded access policies.
    """
    
    def __init__(self, 
                 cpabe_engine: CPABEEngine,
                 key_manager: KeyManager,
                 storage_dir: str = "storage"):
        """
        Initialize encryption service
        
        Args:
            cpabe_engine: CP-ABE engine instance
            key_manager: Key manager instance
            storage_dir: Base directory for file storage
        """
        self.cpabe = cpabe_engine
        self.key_manager = key_manager
        self.storage_dir = storage_dir
        
        # Create storage directories
        self.encrypted_dir = os.path.join(storage_dir, "encrypted")
        self.keys_dir = os.path.join(storage_dir, "keys")
        self.metadata_dir = os.path.join(storage_dir, "metadata")
        
        for directory in [self.encrypted_dir, self.keys_dir, self.metadata_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def encrypt_file(self,
                    input_file_path: str,
                    patient_id: str,
                    policy_expression: str,
                    encrypted_by: str,
                    file_type: str = "medical_record",
                    department: Optional[str] = None,
                    policy_id: Optional[str] = None,
                    metadata: Optional[Dict] = None) -> EncryptedFile:
        """
        Encrypt a patient file using hybrid AES-256 + CP-ABE encryption
        
        Args:
            input_file_path: Path to plaintext file
            patient_id: Patient identifier
            policy_expression: CP-ABE access policy  
            encrypted_by: User ID who encrypted the file
            file_type: Type of file (medical_record, lab_report, etc.)
            department: Department associated with file
            policy_id: Optional policy ID
            metadata: Optional additional metadata
            
        Returns:
            EncryptedFile object with all metadata
            
        Process:
            1. Generate random AES-256 key
            2. Encrypt file with AES-256
            3. Compute SHA-3 hash of encrypted file
            4. Encrypt AES key with CP-ABE using access policy
            5. Store encrypted file, encrypted key, and metadata
            
        Example:
            >>> encr_file = service.encrypt_file(
            ...     "patient_record.pdf",
            ...     "P12345",
            ...     "Doctor AND Cardiology",
            ...     "admin"
            ... )
        """
        # Generate unique file ID
        file_id = self._generate_file_id()
        
        # Get original file info
        original_filename = os.path.basename(input_file_path)
        original_size = os.path.getsize(input_file_path)
        
        # Generate file names
        encrypted_filename = f"{file_id}.enc"
        encrypted_file_path = os.path.join(self.encrypted_dir, encrypted_filename)
        
        # Step 1: Generate AES-256 key
        aes_key = AESEncryption.generate_key()
        
        # Step 2: Encrypt file with AES-256
        iv = AESEncryption.encrypt_file(input_file_path, encrypted_file_path, aes_key)
        
        # Step 3: Compute SHA-3 hash of encrypted file
        integrity_hash = IntegrityChecker.compute_file_hash(encrypted_file_path)
        
        # Step 4: Encrypt AES key with CP-ABE
        encrypted_aes_key = self.cpabe.encrypt_key(aes_key, policy_expression)
        
        # Generate key ID and store encrypted AES key
        aes_key_id = self.key_manager.generate_key_id()
        encrypted_key_path = os.path.join(self.keys_dir, f"{aes_key_id}.cpabe")
        
        # Save encrypted AES key
        import json
        import pickle
        with open(encrypted_key_path, 'wb') as f:
            pickle.dump(encrypted_aes_key, f)
        
        # Get encrypted file size
        encrypted_size = os.path.getsize(encrypted_file_path)
        
        # Step 5: Create encrypted file record
        encrypted_file = EncryptedFile(
            file_id=file_id,
            original_filename=original_filename,
            encrypted_filename=encrypted_filename,
            patient_id=patient_id,
            file_type=file_type,
            aes_key_id=aes_key_id,
            iv=iv.hex(),
            integrity_hash=integrity_hash,
            policy_id=policy_id or "CUSTOM",
            policy_expression=policy_expression,
            original_size=original_size,
            encrypted_size=encrypted_size,
            encrypted_by=encrypted_by,
            encrypted_at=datetime.now(),
            encrypted_file_path=encrypted_file_path,
            encrypted_key_path=encrypted_key_path,
            department=department,
            metadata=metadata or {}
        )
        
        # Save metadata
        metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
        with open(metadata_path, 'w') as f:
            f.write(encrypted_file.to_json())
        
        # Securely delete AES key from memory (best effort)
        del aes_key
        
        return encrypted_file
    
    def get_file_metadata(self, file_id: str) -> Optional[EncryptedFile]:
        """
        Retrieve metadata for an encrypted file
        
        Args:
            file_id: File identifier
            
        Returns:
            EncryptedFile object or None if not found
        """
        metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, 'r') as f:
            return EncryptedFile.from_json(f.read())
    
    def list_encrypted_files(self, patient_id: Optional[str] = None) -> list[EncryptedFile]:
        """
        List all encrypted files, optionally filtered by patient
        
        Args:
            patient_id: Optional patient ID to filter  
            
        Returns:
            List of EncryptedFile objects
        """
        files = []
        
        for filename in os.listdir(self.metadata_dir):
            if filename.endswith('.json'):
                file_id = filename[:-5]
                encrypted_file = self.get_file_metadata(file_id)
                
                if encrypted_file:
                    if patient_id is None or encrypted_file.patient_id == patient_id:
                        files.append(encrypted_file)
        
        return files
    
    def update_metadata(self, file_id: str, encrypted_file: EncryptedFile):
        """
        Update file metadata
        
        Args:
            file_id: File identifier
            encrypted_file: Updated EncryptedFile object
        """
        metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
        
        with open(metadata_path, 'w') as f:
            f.write(encrypted_file.to_json())
    
    def delete_encrypted_file(self, file_id: str) -> bool:
        """
        Delete encrypted file and all associated data
        
        Args:
            file_id: File identifier
            
        Returns:
            True if deleted, False if not found
        """
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            return False
        
        # Delete encrypted file
        if os.path.exists(metadata.encrypted_file_path):
            os.remove(metadata.encrypted_file_path)
        
        # Delete encrypted key
        if os.path.exists(metadata.encrypted_key_path):
            os.remove(metadata.encrypted_key_path)
        
        # Delete metadata
        metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
        
        return True
    
    @staticmethod
    def _generate_file_id() -> str:
        """Generate unique file identifier"""
        return f"FILE_{secrets.token_hex(8).upper()}"


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    print("=== Encryption Service Test ===\n")
    
    # Initialize components
    print("1. Initializing CP-ABE system...")
    cpabe = CPABEEngine()
    cpabe.setup()
    print("   ✓ CP-ABE initialized\n")
    
    print("2. Initializing Key Manager...")
    key_manager = KeyManager("test_storage/keys")
    print("   ✓ Key Manager initialized\n")
    
    print("3. Creating Encryption Service...")
    encryption_service = EncryptionService(cpabe, key_manager, "test_storage")
    print("   ✓ Encryption Service ready\n")
    
    # Create sample file
    print("4. Creating sample patient file...")
    sample_file = "test_patient_record.txt"
    with open(sample_file, 'w') as f:
        f.write("""
CONFIDENTIAL PATIENT RECORD
===========================
Patient ID: P12345
Name: John Doe
DOB: 1975-08-22

MEDICAL HISTORY:
- Hypertension (2018)
- Type 2 Diabetes (2020)
- High Cholesterol (2021)

CURRENT MEDICATIONS:
- Lisinopril 10mg daily
- Metformin 500mg twice daily
- Atorvastatin 20mg daily

ALLERGIES:
- Penicillin
- Sulfa drugs

LAST VISIT: 2024-01-15
NEXT APPOINTMENT: 2024-02-15

NOTES:
Patient is responding well to current treatment plan.
Blood pressure and glucose levels are within target range.
        """)
    print(f"   ✓ Created {sample_file}\n")
    
    # Encrypt file
    print("5. Encrypting file with CP-ABE policy...")
    policy = "Doctor AND Cardiology"
    print(f"   Policy: {policy}")
    
    encrypted_file = encryption_service.encrypt_file(
        input_file_path=sample_file,
        patient_id="P12345",
        policy_expression=policy,
        encrypted_by="admin",
        file_type="medical_record",
        department="Cardiology",
        metadata={'importance': 'high', 'category': 'chronic_disease'}
    )
    
    print(f"   ✓ File encrypted")
    print(f"   File ID: {encrypted_file.file_id}")
    print(f"   Original size: {encrypted_file.original_size} bytes")
    print(f"   Encrypted size: {encrypted_file.encrypted_size} bytes")
    print(f"   Integrity hash: {encrypted_file.integrity_hash[:32]}...")
    print(f"   AES Key ID: {encrypted_file.aes_key_id}")
    print(f"   Policy: {encrypted_file.policy_expression}\n")
    
    # List files
    print("6. Listing encrypted files...")
    files = encryption_service.list_encrypted_files()
    print(f"   Found {len(files)} file(s)")
    for f in files:
        print(f"   - {f.file_id}: {f.original_filename} (Patient: {f.patient_id})\n")
    
    # Retrieve metadata
    print("7. Retrieving file metadata...")
    retrieved = encryption_service.get_file_metadata(encrypted_file.file_id)
    print(f"   ✓ Retrieved: {retrieved.original_filename}")
    print(f"   Patient: {retrieved.patient_id}")
    print(f"   Encrypted by: {retrieved.encrypted_by}\n")
    
    # Cleanup
    print("8. Cleaning up...")
    os.remove(sample_file)
    import shutil
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    print("   ✓ Cleanup complete\n")
    
    print("=== Test Complete ===")
