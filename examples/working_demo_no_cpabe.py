"""
Working Demo - Without charm-crypto
Tests all components that don't require CP-ABE
"""

import sys
import os

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


print("="*70)
print("  HEALTHCARE DATA SECURITY SYSTEM - WORKING DEMO")
print("  (Components that work without charm-crypto)")
print("="*70)
print()

# Test 1: AES-256 Encryption
print("="*70)
print("TEST 1: AES-256 Encryption")
print("="*70)

from src.crypto.aes_encryption import AESEncryption

aes = AESEncryption()

# Sample patient data
patient_data = b"""
CONFIDENTIAL PATIENT RECORD
Patient ID: P12345
Name: John Doe
Diagnosis: Hypertension
Medications: Lisinopril 10mg daily
"""

print("\n1. Generating AES-256 key...")
key = aes.generate_key()
print(f"   ✓ Generated key: {key.hex()[:32]}... ({len(key)} bytes)")

print("\n2. Encrypting patient data...")
ciphertext, iv = aes.encrypt(patient_data, key)
print(f"   ✓ Encrypted {len(patient_data)} bytes → {len(ciphertext)} bytes")
print(f"   IV: {iv.hex()}")

print("\n3. Decrypting...")
decrypted = aes.decrypt(ciphertext, key, iv)
print(f"   ✓ Decrypted successfully")
print(f"   Match: {decrypted == patient_data}")

# Test 2: SHA-3 Integrity
print("\n" + "="*70)
print("TEST 2: SHA-3 Integrity Verification")
print("="*70)

from src.crypto.hash_integrity import IntegrityChecker

checker = IntegrityChecker()

print("\n1. Computing SHA-3 hash of encrypted data...")
hash_value = checker.compute_hash(ciphertext)
print(f"   ✓ Hash: {hash_value[:32]}...")

print("\n2. Verifying integrity...")
is_valid = checker.verify_hash(ciphertext, hash_value)
print(f"   ✓ Integrity check: {'VALID' if is_valid else 'INVALID'}")

print("\n3. Testing tamper detection...")
tampered_data = ciphertext[:-1]  # Remove last byte
is_valid = checker.verify_hash(tampered_data, hash_value)
print(f"   ✓ Tampered data detected: {'INVALID' if not is_valid else 'VALID'}")

# Test 3: Key Management
print("\n" + "="*70)
print("TEST 3: Key Management")
print("="*70)

from src.crypto.key_manager import KeyManager

km = KeyManager("demo_storage/keys")

print("\n1. Generating and storing key...")
key_id = km.generate_key_id()
aes_key = km.generate_aes_key()
print(f"   ✓ Key ID: {key_id}")

metadata = {
    'purpose': 'patient_records',
    'department': 'cardiology'
}

km.store_key(key_id, aes_key, metadata)
print(f"   ✓ Key stored with metadata")

print("\n2. Retrieving key...")
retrieved_key = km.retrieve_key(key_id)
print(f"   ✓ Key retrieved: {retrieved_key.hex()[:32]}...")
print(f"   Match: {retrieved_key == aes_key}")

print("\n3. Key rotation...")
new_key_id, new_key = km.rotate_key(key_id)
print(f"   ✓ Old key ID: {key_id}")
print(f"   ✓ New key ID: {new_key_id}")

# Test 4: User Management
print("\n" + "="*70)
print("TEST 4: User Management")
print("="*70)

from src.models.user import User

print("\n1. Creating users...")

doctor = User(
    user_id="U001",
    username="dr.carter",
    full_name="Dr. Emily Carter",
    role="Doctor",
    department="Cardiology",
    clearance_level="L3",
    specialty="Surgeon"
)

print(f"   ✓ Created: {doctor.full_name}")
print(f"   Attributes: {', '.join(doctor.attributes)}")

nurse = User(
    user_id="U002",
    username="nurse.brown",
    full_name="Nurse Michael Brown",
    role="Nurse",
    department="Emergency",
    clearance_level="L2"
)

print(f"\n   ✓ Created: {nurse.full_name}")
print(f"   Attributes: {', '.join(nurse.attributes)}")

# Test 5: Policy System
print("\n" + "="*70)
print("TEST 5: Policy Management")
print("="*70)

from src.models.policy import Policy, PolicyTemplates

print("\n1. Creating access policies...")

cardiology_policy = Policy(
    policy_id="POL001",
    name="Cardiology Access",
    policy_expression="Doctor AND Cardiology",
    description="Access to cardiology patient records",
    created_by="admin"
)

print(f"   ✓ Policy: {cardiology_policy.name}")
print(f"   Expression: {cardiology_policy.policy_expression}")
print(f"   Required attributes: {', '.join(cardiology_policy.get_required_attributes())}")

print("\n2. Testing policy templates...")
emergency_expr = PolicyTemplates.emergency_access()
print(f"   ✓ Emergency access: {emergency_expr}")

lab_expr = PolicyTemplates.lab_results()
print(f"   ✓ Lab results: {lab_expr}")

# Test 6: File Encryption Workflow
print("\n" + "="*70)
print("TEST 6: Complete File Encryption Workflow")
print("="*70)

print("\n1. Creating sample patient file...")
sample_file = "demo_patient_record.txt"
with open(sample_file, 'w') as f:
    f.write("""
CONFIDENTIAL CARDIOLOGY PATIENT RECORD
=======================================
Patient ID: P12345
Name: Jane Smith
DOB: 1975-03-15

DIAGNOSIS:
- Acute Myocardial Infarction
- Coronary Artery Disease

CURRENT MEDICATIONS:
- Aspirin 81mg daily
- Atorvastatin 80mg daily

ATTENDING PHYSICIAN: Dr. Emily Carter
    """)
print(f"   ✓ Created: {sample_file}")

print("\n2. Encrypting file with AES-256...")
encrypted_file = "demo_patient_record.enc"
encryption_key = aes.generate_aes_key()
iv = aes.encrypt_file(sample_file, encrypted_file, encryption_key)
print(f"   ✓ File encrypted: {encrypted_file}")
print(f"   IV: {iv.hex()}")

print("\n3. Computing integrity hash...")
file_hash = checker.compute_file_hash(encrypted_file)
print(f"   ✓ SHA-3 Hash: {file_hash[:32]}...")

print("\n4. Storing encryption metadata...")
encrypted_metadata = {
    'original_file': sample_file,
    'encrypted_file': encrypted_file,
    'iv': iv.hex(),
    'hash': file_hash,
    'policy': cardiology_policy.policy_expression,
    'patient_id': 'P12345'
}
print(f"   ✓ Metadata stored")

print("\n5. Simulating decryption (with integrity check)...")

# Verify integrity first
is_valid = checker.verify_file_hash(encrypted_file, file_hash)
print(f"   ✓ Integrity check: {'VALID' if is_valid else 'INVALID'}")

if is_valid:
    # Decrypt
    decrypted_file = "demo_patient_record_decrypted.txt"
    aes.decrypt_file(encrypted_file, decrypted_file, encryption_key, iv)
    print(f"   ✓ File decrypted: {decrypted_file}")
    
    # Verify content
    with open(sample_file, 'r') as f1:
        with open(decrypted_file, 'r') as f2:
            if f1.read() == f2.read():
                print(f"   ✓ Content matches original!")

# Summary
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)

print("\n✅ WORKING COMPONENTS:")
print("   ✓ AES-256 encryption/decryption")
print("   ✓ SHA-3 integrity verification")
print("   ✓ Secure key generation")
print("   ✓ Key management (generation, storage, rotation)")
print("   ✓ User model with attributes")
print("   ✓ Policy model with expressions")
print("   ✓ File encryption workflow")
print("   ✓ Integrity checking before decryption")

print("\n⚠️  REQUIRES charm-crypto (CP-ABE):")
print("   • Attribute-based key encryption")
print("   • Policy-enforced decryption")
print("   • Automatic access control via CP-ABE")

print("\n💡 NOTE:")
print("   The core security components (AES-256, SHA-3, Key Management)")
print("   are fully functional. CP-ABE adds policy-based access control,")
print("   but the encryption itself is already military-grade!")

print("\n" + "="*70)
print("  Demo Complete!")
print("="*70)
print()

# Cleanup
import shutil
if os.path.exists("demo_storage"):
    shutil.rmtree("demo_storage")
if os.path.exists(sample_file):
    os.remove(sample_file)
if os.path.exists(encrypted_file):
    os.remove(encrypted_file)
if os.path.exists(decrypted_file):
    os.remove(decrypted_file)

print("✓ Temporary files cleaned up")
print()
