"""
Encrypted File Model
Represents encrypted patient file with metadata
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime
import json


@dataclass
class EncryptedFile:
    """
    Model for encrypted patient file with all necessary metadata
    """
    file_id: str
    original_filename: str
    encrypted_filename: str
    patient_id: str
    file_type: str  # "medical_record", "lab_report", "xray", etc.
    
    # Encryption metadata
    aes_key_id: str  # ID of encrypted AES key
    iv: str  # Initialization vector (hex)
    integrity_hash: str  # SHA-3 hash (hex)
    
    # Access control
    policy_id: str
    policy_expression: str
    
    # File information
    original_size: int
    encrypted_size: int
    mime_type: Optional[str] = None
    
    # Audit information
    encrypted_by: str
    encrypted_at: datetime = field(default_factory=datetime.now)
    last_accessed_at: Optional[datetime] = None
    access_count: int = 0
    
    # Storage paths
    encrypted_file_path: str = ""
    encrypted_key_path: str = ""
    
    # Additional metadata
    department: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'file_id': self.file_id,
            'original_filename': self.original_filename,
            'encrypted_filename': self.encrypted_filename,
            'patient_id': self.patient_id,
            'file_type': self.file_type,
            'aes_key_id': self.aes_key_id,
            'iv': self.iv,
            'integrity_hash': self.integrity_hash,
            'policy_id': self.policy_id,
            'policy_expression': self.policy_expression,
            'original_size': self.original_size,
            'encrypted_size': self.encrypted_size,
            'mime_type': self.mime_type,
            'encrypted_by': self.encrypted_by,
            'encrypted_at': self.encrypted_at.isoformat(),
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'access_count': self.access_count,
            'encrypted_file_path': self.encrypted_file_path,
            'encrypted_key_path': self.encrypted_key_path,
            'department': self.department,
            'category': self.category,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EncryptedFile':
        """Create from dictionary"""
        if isinstance(data.get('encrypted_at'), str):
            data['encrypted_at'] = datetime.fromisoformat(data['encrypted_at'])
        if isinstance(data.get('last_accessed_at'), str) and data.get('last_accessed_at'):
            data['last_accessed_at'] = datetime.fromisoformat(data['last_accessed_at'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'EncryptedFile':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def record_access(self):
        """Record file access"""
        self.last_accessed_at = datetime.now()
        self.access_count += 1
    
    def __repr__(self) -> str:
        return f"EncryptedFile(id={self.file_id}, patient={self.patient_id}, type={self.file_type})"


# Example usage
if __name__ == "__main__":
    print("=== Encrypted File Model Test ===\n")
    
    # Create encrypted file record
    encrypted_file = EncryptedFile(
        file_id="FILE001",
        original_filename="patient_P12345_medical_history.pdf",
        encrypted_filename="FILE001.enc",
        patient_id="P12345",
        file_type="medical_record",
        aes_key_id="KEY001",
        iv="1a2b3c4d5e6f7g8h9i0j",
        integrity_hash="sha3_hash_value_here",
        policy_id="POL001",
        policy_expression="Doctor AND Cardiology",
        original_size=524288,
        encrypted_size=524304,
        mime_type="application/pdf",
        encrypted_by="admin",
        encrypted_file_path="storage/encrypted/FILE001.enc",
        encrypted_key_path="storage/keys/KEY001.cpabe",
        department="Cardiology",
        category="Patient History",
        tags=["cardiology", "history", "important"]
    )
    
    print(f"{encrypted_file}\n")
    print(f"Original file: {encrypted_file.original_filename}")
    print(f"Patient: {encrypted_file.patient_id}")
    print(f"Policy: {encrypted_file.policy_expression}")
    print(f"Size: {encrypted_file.original_size} → {encrypted_file.encrypted_size} bytes")
    print(f"Encrypted by: {encrypted_file.encrypted_by}")
    print(f"Encrypted at: {encrypted_file.encrypted_at}")
    print(f"Access count: {encrypted_file.access_count}\n")
    
    # Record access
    print("Recording access...")
    encrypted_file.record_access()
    print(f"Access count: {encrypted_file.access_count}")
    print(f"Last accessed: {encrypted_file.last_accessed_at}\n")
    
    # Serialization
    print("Serialization test:")
    json_str = encrypted_file.to_json()
    print(f"\nJSON:\n{json_str}\n")
    
    restored = EncryptedFile.from_json(json_str)
    print(f"Restored: {restored}")
    print(f"Match: {encrypted_file.file_id == restored.file_id}")
    
    print("\n=== Test Complete ===")
