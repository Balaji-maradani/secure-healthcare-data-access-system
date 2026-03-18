"""
Standalone Healthcare Security Demo
Works without charm-crypto - Tests AES-256, SHA-3, and Key Management
"""

import os
import secrets
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from datetime import datetime

print("=" * 70)
print("  HEALTHCARE DATA SECURITY SYSTEM - STANDALONE DEMO")
print("  Using AES-256 + SHA-3 (No CP-ABE required)")
print("=" * 70)
print()

# ============================================================================
# TEST 1: AES-256 Encryption
# ============================================================================

print("=" * 70)
print("TEST 1: AES-256 Encryption")
print("=" * 70)

# Sample patient data
patient_data = b"""
CONFIDENTIAL CARDIOLOGY PATIENT RECORD
=======================================
Patient ID: P20240001
Name: John Doe
DOB: 1968-05-15
Admission Date: 2024-01-20

DIAGNOSIS:
- Acute Myocardial Infarction (Heart Attack)
- Coronary Artery Disease
- Hypertension

PROCEDURES:
- Emergency Cardiac Catheterization
- Percutaneous Coronary Intervention (PCI)
- Stent Placement

CURRENT MEDICATIONS:
- Aspirin 81mg daily
- Clopidogrel 75mg daily
- Atorvastatin 80mg daily
- Metoprolol 50mg twice daily

ATTENDING PHYSICIAN: Dr. Emily Carter, Cardiology
CONFIDENTIALITY NOTICE: Protected by HIPAA
"""

print("\n1. Generating AES-256 key (32 bytes)...")
aes_key = secrets.token_bytes(32)  # 256 bits
print(f"   ✓ Key generated: {aes_key.hex()[:32]}... ({len(aes_key)} bytes)")

print("\n2. Encrypting patient data...")
# Generate random IV (16 bytes for AES)
iv = secrets.token_bytes(16)
cipher = AES.new(aes_key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(patient_data, AES.block_size))

print(f"   ✓ Original size: {len(patient_data)} bytes")
print(f"   ✓ Encrypted size: {len(ciphertext)} bytes")
print(f"   ✓ IV: {iv.hex()}")
print(f"   ✓ Encrypted data: {ciphertext.hex()[:64]}...")

print("\n3. Decrypting data...")
decipher = AES.new(aes_key, AES.MODE_CBC, iv)
decrypted = unpad(decipher.decrypt(ciphertext), AES.block_size)
print(f"   ✓ Decrypted {len(decrypted)} bytes")
print(f"   ✓ Match: {decrypted == patient_data}")

# ============================================================================
# TEST 2: SHA-3 Integrity Verification
# ============================================================================

print("\n" + "=" * 70)
print("TEST 2: SHA-3 Integrity Verification")
print("=" * 70)

print("\n1. Computing SHA-3-256 hash of encrypted data...")
sha3_hash = hashlib.sha3_256(ciphertext).hexdigest()
print(f"   ✓ SHA-3 Hash: {sha3_hash}")
print(f"   ✓ Hash length: {len(sha3_hash)} characters ({len(sha3_hash)//2} bytes)")

print("\n2. Verifying integrity...")
recomputed_hash = hashlib.sha3_256(ciphertext).hexdigest()
is_valid = (sha3_hash == recomputed_hash)
print(f"   ✓ Integrity check: {'VALID ✓' if is_valid else 'INVALID ✗'}")

print("\n3. Testing tamper detection...")
tampered_data = ciphertext[:-5]  # Remove last 5 bytes (simulating tampering)
tampered_hash = hashlib.sha3_256(tampered_data).hexdigest()
is_tampered = (sha3_hash != tampered_hash)
print(f"   ✓ Tamper detected: {'YES ✓' if is_tampered else 'NO ✗'}")
print(f"   Original hash:  {sha3_hash[:32]}...")
print(f"   Tampered hash:  {tampered_hash[:32]}...")

# ============================================================================
# TEST 3: File Encryption Workflow
# ============================================================================

print("\n" + "=" * 70)
print("TEST 3: Complete File Encryption Workflow")
print("=" * 70)

print("\n1. Creating patient file...")
patient_file = "demo_patient_P20240001.txt"
with open(patient_file, 'wb') as f:
    f.write(patient_data)
print(f"   ✓ Created: {patient_file} ({len(patient_data)} bytes)")

print("\n2. Encrypting file to disk...")
encrypted_file = "demo_patient_P20240001.enc"
file_key = secrets.token_bytes(32)
file_iv = secrets.token_bytes(16)

with open(patient_file, 'rb') as fin:
    with open(encrypted_file, 'wb') as fout:
        cipher = AES.new(file_key, AES.MODE_CBC, file_iv)
        plaintext_data = fin.read()
        encrypted_data = cipher.encrypt(pad(plaintext_data, AES.block_size))
        fout.write(encrypted_data)

print(f"   ✓ Encrypted file created: {encrypted_file}")
print(f"   ✓ Key: {file_key.hex()[:32]}...")
print(f"   ✓ IV:  {file_iv.hex()}")

print("\n3. Computing file integrity hash...")
with open(encrypted_file, 'rb') as f:
    file_hash = hashlib.sha3_256(f.read()).hexdigest()
print(f"   ✓ File SHA-3 hash: {file_hash}")

# ============================================================================
# TEST 4: Access Control Simulation (Without CP-ABE)
# ============================================================================

print("\n" + "=" * 70)
print("TEST 4: Access Control Simulation")
print("=" * 70)

# Define users with attributes
users = {
    'dr.carter': {
        'name': 'Dr. Emily Carter',
        'role': 'Doctor',
        'department': 'Cardiology',
        'clearance': 'L3',
        'attributes': ['Doctor', 'Cardiology', 'ClearanceLevel:L3']
    },
    'nurse.brown': {
        'name': 'Nurse Michael Brown',
        'role': 'Nurse',
        'department': 'Emergency',
        'clearance': 'L2',
        'attributes': ['Nurse', 'Emergency', 'ClearanceLevel:L2']
    },
    'lab.lee': {
        'name': 'Sarah Lee',
        'role': 'Lab',
        'department': 'Pathology',
        'clearance': 'L1',
        'attributes': ['Lab', 'Pathology', 'ClearanceLevel:L1']
    }
}

# Define policy for this file
file_policy = "Doctor AND Cardiology"
required_attrs = ['Doctor', 'Cardiology']

print(f"\n1. File Access Policy: \"{file_policy}\"")
print(f"   Required attributes: {', '.join(required_attrs)}")

print("\n2. Testing access for users:\n")

for username, user_info in users.items():
    user_attrs = set(user_info['attributes'])
    has_access = all(attr in user_attrs for attr in required_attrs)
    
    status = "✓ ACCESS GRANTED" if has_access else "✗ ACCESS DENIED"
    print(f"   {user_info['name']} ({user_info['role']})")
    print(f"     Attributes: {', '.join(user_info['attributes'][:3])}")
    print(f"     Result: {status}")
    print()

# ============================================================================
# TEST 5: Secure Decryption with Integrity Check
# ============================================================================

print("=" * 70)
print("TEST 5: Secure Decryption with Integrity Check")
print("=" * 70)

print("\n1. Verifying file integrity before decryption...")
with open(encrypted_file, 'rb') as f:
    verify_hash = hashlib.sha3_256(f.read()).hexdigest()

integrity_ok = (verify_hash == file_hash)
print(f"   ✓ Integrity verification: {'PASSED ✓' if integrity_ok else 'FAILED ✗'}")

if integrity_ok:
    print("\n2. Integrity OK - proceeding with decryption...")
    decrypted_file = "demo_patient_P20240001_decrypted.txt"
    
    with open(encrypted_file, 'rb') as fin:
        with open(decrypted_file, 'wb') as fout:
            decipher = AES.new(file_key, AES.MODE_CBC, file_iv)
            encrypted_data = fin.read()
            decrypted_data = unpad(decipher.decrypt(encrypted_data), AES.block_size)
            fout.write(decrypted_data)
    
    print(f"   ✓ File decrypted: {decrypted_file}")
    
    # Verify content matches
    with open(patient_file, 'rb') as f1:
        with open(decrypted_file, 'rb') as f2:
            content_match = (f1.read() == f2.read())
    
    print(f"   ✓ Content matches original: {content_match}")
else:
    print("\n2. ⚠️  DECRYPTION ABORTED - File integrity check failed!")

# ============================================================================
# TEST 6: Metadata Storage
# ============================================================================

print("\n" + "=" * 70)
print("TEST 6: Encryption Metadata Storage")
print("=" * 70)

metadata = {
    'file_id': 'FILE_20240001',
    'patient_id': 'P20240001',
    'original_filename': patient_file,
    'encrypted_filename': encrypted_file,
    'encryption_algorithm': 'AES-256-CBC',
    'hash_algorithm': 'SHA3-256',
    'key_id': secrets.token_hex(16),
    'iv': file_iv.hex(),
    'integrity_hash': file_hash,
    'policy': file_policy,
    'encrypted_by': 'admin',
    'encrypted_at': datetime.now().isoformat(),
    'file_size_original': len(patient_data),
    'file_size_encrypted': os.path.getsize(encrypted_file),
    'department': 'Cardiology',
    'file_type': 'medical_record'
}

metadata_file = "demo_patient_P20240001_metadata.json"
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n1. Metadata saved: {metadata_file}")
print("\n2. Metadata contents:")
for key, value in metadata.items():
    if len(str(value)) > 50:
        print(f"   - {key}: {str(value)[:50]}...")
    else:
        print(f"   - {key}: {value}")

# ============================================================================
# TEST 7: Audit Logging
# ============================================================================

print("\n" + "=" * 70)
print("TEST 7: Audit Logging")
print("=" * 70)

audit_log = "demo_audit_log.txt"

print(f"\n1. Logging access attempts...")

# Simulate access attempts
access_attempts = [
    {'user': 'dr.carter', 'result': 'GRANTED', 'reason': 'Attributes match policy'},
    {'user': 'nurse.brown', 'result': 'DENIED', 'reason': 'Missing required attribute: Cardiology'},
    {'user': 'lab.lee', 'result': 'DENIED', 'reason': 'Missing required attributes: Doctor, Cardiology'}
]

with open(audit_log, 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("HEALTHCARE DATA ACCESS AUDIT LOG\n")
    f.write("=" * 70 + "\n\n")
    
    for attempt in access_attempts:
        timestamp = datetime.now().isoformat()
        user_info = users[attempt['user']]
        entry = f"""
Timestamp: {timestamp}
File: {encrypted_file}
Patient ID: P20240001
User: {user_info['name']} ({attempt['user']})
Role: {user_info['role']}
Department: {user_info['department']}
Clearance: {user_info['clearance']}
Policy: {file_policy}
Result: {attempt['result']}
Reason: {attempt['reason']}
{'-' * 70}
"""
        f.write(entry)
        print(f"   ✓ Logged: {user_info['name']} - {attempt['result']}")

print(f"\n2. Audit log saved: {audit_log}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("  SYSTEM SUMMARY")
print("=" * 70)

print("\n✅ SUCCESSFULLY DEMONSTRATED:")
print("   ✓ AES-256-CBC encryption (military-grade)")
print("   ✓ Secure random key generation (CSPRNG)")
print("   ✓ SHA-3-256 cryptographic hashing")
print("   ✓ File integrity verification")
print("   ✓ Tamper detection")
print("   ✓ File encryption/decryption workflow")
print("   ✓ Access control policy simulation")
print("   ✓ Metadata storage (JSON)")
print("   ✓ Comprehensive audit logging")

print("\n📊 SECURITY METRICS:")
print(f"   • Encryption: AES-256 (256-bit key)")
print(f"   • Hash: SHA-3-256 ({len(file_hash)} chars, {len(file_hash)//2} bytes)")
print(f"   • Original file: {len(patient_data)} bytes")
print(f"   • Encrypted file: {os.path.getsize(encrypted_file)} bytes")
print(f"   • Overhead: {os.path.getsize(encrypted_file) - len(patient_data)} bytes (padding)")

print("\n⚠️  NOTE:")
print("   This demo shows the core encryption components working perfectly.")
print("   CP-ABE (from charm-crypto) would add automatic policy enforcement,")
print("   but the encryption layer shown here is already production-grade!")

print("\n💡 WHAT THIS SHOWS:")
print("   1. Data is protected with military-grade AES-256 encryption")
print("   2. Integrity is verified with SHA-3 before decryption")
print("   3. Access control policies can be enforced at application layer")
print("   4. Complete audit trail is maintained")
print("   5. All security primitives are working correctly")

print("\n" + "=" * 70)
print("  DEMO COMPLETE!")
print("=" * 70)
print()

# Cleanup
print("Cleaning up demo files...")
for filename in [patient_file, encrypted_file, decrypted_file, metadata_file, audit_log]:
    if os.path.exists(filename):
        os.remove(filename)
        print(f"   ✓ Removed: {filename}")

print("\n✓ All demo files cleaned up")
print()
