"""
Controlled Decryption Service
Decrypts files only if user attributes satisfy access policy
"""

import os
import pickle
from typing import Optional, Tuple
from datetime import datetime

from ..crypto.aes_encryption import AESEncryption
from ..crypto.cpabe import CPABEEngine
from ..crypto.hash_integrity import IntegrityChecker
from ..models.encrypted_file import EncryptedFile
from ..models.user import User


class DecryptionService:
    """
    Controlled Decryption Service
    
    Enforces attribute-based access control through CP-ABE.
    Verifies file integrity before decryption.
    """
    
    def __init__(self, cpabe_engine: CPABEEngine, storage_dir: str = "storage"):
        """
        Initialize decryption service
        
        Args:
            cpabe_engine: CP-ABE engine instance
            storage_dir: Base directory for file storage
        """
        self.cpabe = cpabe_engine
        self.storage_dir = storage_dir
        
        self.encrypted_dir = os.path.join(storage_dir, "encrypted")
        self.keys_dir = os.path.join(storage_dir, "keys")
        self.metadata_dir = os.path.join(storage_dir, "metadata")
    
    def decrypt_file(self,
                    file_id: str,
                    user: User,
                    user_private_key: dict,
                    output_path: str,
                    verify_integrity: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Decrypt a file if user has appropriate attributes
        
        Args:
            file_id: Encrypted file identifier
            user: User object with attributes
            user_private_key: User's CP-ABE private key
            output_path: Path to save decrypted file
            verify_integrity: Whether to verify SHA-3 hash before decryption
            
        Returns:
            (success: bool, error_message: Optional[str])
            
        Process:
            1. Load file metadata
            2. Verify file integrity (SHA-3 hash)
            3. Load encrypted AES key
            4. Decrypt AES key using CP-ABE (policy check happens here)
            5. If successful, decrypt file with AES key
            6. Record access in audit log
            
        Example:
            >>> success, error = service.decrypt_file(
            ...     "FILE_123",
            ...     doctor_user,
            ...     doctor_private_key,
            ...     "decrypted_record.pdf"
            ... )
            >>> if success:
            ...     print("File decrypted successfully")
        """
        # Step 1: Load metadata
        metadata = self._load_metadata(file_id)
        if not metadata:
            return False, f"File {file_id} not found"
        
        # Step 2: Verify integrity
        if verify_integrity:
            is_valid, error = self._verify_integrity(metadata)
            if not is_valid:
                return False, f"Integrity verification failed: {error}"
        
        # Step 3: Load encrypted AES key
        encrypted_aes_key = self._load_encrypted_key(metadata.aes_key_id)
        if not encrypted_aes_key:
            return False, f"Encrypted key not found: {metadata.aes_key_id}"
        
        # Step 4: Decrypt AES key using CP-ABE (POLICY CHECK)
        aes_key = self.cpabe.decrypt_key(encrypted_aes_key, user_private_key)
        
        if aes_key is None:
            # Policy not satisfied - access denied
            self._log_access_attempt(file_id, user.user_id, False, "Policy not satisfied")
            return False, f"Access denied: Your attributes do not satisfy the policy '{metadata.policy_expression}'"
        
        # Step 5: Decrypt file with AES key
        try:
            iv = bytes.fromhex(metadata.iv)
            AESEncryption.decrypt_file(
                metadata.encrypted_file_path,
                output_path,
                aes_key,
                iv
            )
            
            # Step 6: Record successful access
            self._log_access_attempt(file_id, user.user_id, True, "Success")
            self._update_access_metadata(metadata)
            
            # Securely delete AES key from memory
            del aes_key
            
            return True, None
            
        except Exception as e:
            self._log_access_attempt(file_id, user.user_id, False, str(e))
            return False, f"Decryption failed: {str(e)}"
    
    def check_access(self, file_id: str, user: User) -> Tuple[bool, str]:
        """
        Check if user can access file without actually decrypting
        
        Args:
            file_id: File identifier
            user: User object
            
        Returns:
            (can_access: bool, reason: str)
        """
        metadata = self._load_metadata(file_id)
        if not metadata:
            return False, "File not found"
        
        # Simple attribute check (doesn't guarantee decryption will succeed)
        user_can_access = self.cpabe.verify_attributes(
            set(user.attributes),
            metadata.policy_expression
        )
        
        if user_can_access:
            return True, "Access granted (policy satisfied)"
        else:
            return False, f"Access denied: Policy '{metadata.policy_expression}' not satisfied"
    
    def get_accessible_files(self, user: User) -> list[EncryptedFile]:
        """
        Get list of files user can potentially access
        
        Args:
            user: User object
            
        Returns:
            List of EncryptedFile objects user might access
            
        Note: This is an optimistic check; actual decryption may still fail
        """
        accessible_files = []
        
        for filename in os.listdir(self.metadata_dir):
            if filename.endswith('.json'):
                file_id = filename[:-5]
                metadata = self._load_metadata(file_id)
                
                if metadata:
                    can_access, _ = self.check_access(file_id, user)
                    if can_access:
                        accessible_files.append(metadata)
        
        return accessible_files
    
    def _load_metadata(self, file_id: str) -> Optional[EncryptedFile]:
        """Load file metadata"""
        metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, 'r') as f:
            return EncryptedFile.from_json(f.read())
    
    def _load_encrypted_key(self, key_id: str) -> Optional[dict]:
        """Load encrypted AES key"""
        key_path = os.path.join(self.keys_dir, f"{key_id}.cpabe")
        
        if not os.path.exists(key_path):
            return None
        
        with open(key_path, 'rb') as f:
            return pickle.load(f)
    
    def _verify_integrity(self, metadata: EncryptedFile) -> Tuple[bool, Optional[str]]:
        """Verify file integrity using SHA-3 hash"""
        if not os.path.exists(metadata.encrypted_file_path):
            return False, "Encrypted file not found"
        
        is_valid = IntegrityChecker.verify_file_hash(
            metadata.encrypted_file_path,
            metadata.integrity_hash
        )
        
        if not is_valid:
            return False, "Hash mismatch - file may be corrupted or tampered"
        
        return True, None
    
    def _update_access_metadata(self, metadata: EncryptedFile):
        """Update file metadata after successful access"""
        metadata.record_access()
        
        metadata_path = os.path.join(self.metadata_dir, f"{metadata.file_id}.json")
        with open(metadata_path, 'w') as f:
            f.write(metadata.to_json())
    
    def _log_access_attempt(self, file_id: str, user_id: str, 
                           success: bool, reason: str):
        """
        Log access attempt for audit trail
        
        Args:
            file_id: File identifier
            user_id: User identifier
            success: Whether access was granted
            reason: Reason for success/failure
        """
        log_dir = os.path.join(self.storage_dir, "audit_logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "access_log.txt")
        
        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "DENIED"
        
        log_entry = f"{timestamp} | {status} | User: {user_id} | File: {file_id} | Reason: {reason}\n"
        
        with open(log_file, 'a') as f:
            f.write(log_entry)


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from src.services.encryption_service import EncryptionService
    from src.crypto.key_manager import KeyManager
    from src.models.user import User
    
    print("=== Decryption Service Test ===\n")
    
    # Initialize components
    print("1. Initializing system...")
    cpabe = CPABEEngine()
    cpabe.setup()
    
    key_manager = KeyManager("test_storage/keys")
    encryption_service = EncryptionService(cpabe, key_manager, "test_storage")
    decryption_service = DecryptionService(cpabe, "test_storage")
    print("   ✓ System initialized\n")
    
    # Create users
    print("2. Creating users...")
    doctor = User(
        user_id="U001",
        username="dr.smith",
        full_name="Dr. Smith",
        role="Doctor",
        department="Cardiology",
        clearance_level="L2"
    )
    
    nurse = User(
        user_id="U002",
        username="nurse.jones",
        full_name="Nurse Jones",
        role="Nurse",
        department="Emergency",
        clearance_level="L1"
    )
    
    print(f"   ✓ Doctor: {doctor.full_name} ({', '.join(doctor.attributes)})")
    print(f"   ✓ Nurse: {nurse.full_name} ({', '.join(nurse.attributes)})\n")
    
    # Generate user keys
    print("3. Generating CP-ABE user keys...")
    doctor_key = cpabe.generate_user_key(doctor.attributes)
    nurse_key = cpabe.generate_user_key(nurse.attributes)
    print("   ✓ User keys generated\n")
    
    # Create and encrypt sample file
    print("4. Creating and encrypting patient file...")
    sample_file = "test_patient_data.txt"
    with open(sample_file, 'w') as f:
        f.write("CONFIDENTIAL: Patient cardiac catheterization report")
    
    policy = "Doctor AND Cardiology"
    encrypted_file = encryption_service.encrypt_file(
        sample_file,
        "P12345",
        policy,
        "admin",
        department="Cardiology"
    )
    print(f"   ✓ File encrypted: {encrypted_file.file_id}")
    print(f"   Policy: {policy}\n")
    
    # Test access checks
    print("5. Checking access permissions...")
    
    doctor_can_access, doctor_reason = decryption_service.check_access(
        encrypted_file.file_id, doctor
    )
    print(f"   Doctor: {doctor_reason}")
    
    nurse_can_access, nurse_reason = decryption_service.check_access(
        encrypted_file.file_id, nurse
    )
    print(f"   Nurse: {nurse_reason}\n")
    
    # Test decryption - Doctor (should succeed)
    print("6. Testing decryption - Doctor...")
    doctor_output = "doctor_decrypted.txt"
    success, error = decryption_service.decrypt_file(
        encrypted_file.file_id,
        doctor,
        doctor_key,
        doctor_output
    )
    
    if success:
        print("   ✓ Doctor successfully decrypted file")
        with open(doctor_output, 'r') as f:
            print(f"   Content: {f.read()}")
    else:
        print(f"   ✗ Doctor failed: {error}")
    print()
    
    # Test decryption - Nurse (should fail)
    print("7. Testing decryption - Nurse...")
    nurse_output = "nurse_decrypted.txt"
    success, error = decryption_service.decrypt_file(
        encrypted_file.file_id,
        nurse,
        nurse_key,
        nurse_output
    )
    
    if success:
        print("   ✗ Nurse unexpectedly succeeded")
    else:
        print(f"   ✓ Nurse correctly denied: {error}\n")
    
    # List accessible files
    print("8. Listing doctor's accessible files...")
    accessible = decryption_service.get_accessible_files(doctor)
    print(f"   Doctor can access {len(accessible)} file(s):")
    for f in accessible:
        print(f"   - {f.file_id}: {f.original_filename}\n")
    
    # Show audit log
    print("9. Audit log:")
    audit_log_path = "test_storage/audit_logs/access_log.txt"
    if os.path.exists(audit_log_path):
        with open(audit_log_path, 'r') as f:
            for line in f:
                print(f"   {line.rstrip()}")
    print()
    
    # Cleanup
    print("10. Cleaning up...")
    import shutil
    if os.path.exists(sample_file):
        os.remove(sample_file)
    if os.path.exists(doctor_output):
        os.remove(doctor_output)
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    print("   ✓ Cleanup complete\n")
    
    print("=== Test Complete ===")
