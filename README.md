# Secure Healthcare Data Access System

A comprehensive healthcare data security system implementing **CP-ABE (Ciphertext-Policy Attribute-Based Encryption)** combined with **AES-256** and **SHA-3** for secure, policy-based access control to medical records.

## 🔐 Security Features

- **CP-ABE Access Control**: Attribute-based encryption with embedded access policies
- **AES-256 Encryption**: Military-grade symmetric encryption for patient data
- **SHA-3 Integrity**: Cryptographic hashing for file integrity verification
- **Hybrid Encryption**: AES for data, CP-ABE for key protection
- **Role-Based Attributes**: Doctor, Nurse, Lab, Admin with department-level granularity

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Healthcare Data System                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐      ┌──────────────┐               │
│  │ Patient File │ ───▶ │  AES-256     │               │
│  │ (Plaintext)  │      │  Encryption  │               │
│  └──────────────┘      └──────┬───────┘               │
│                               │                         │
│                               ▼                         │
│                     ┌──────────────────┐               │
│                     │  Encrypted File  │               │
│                     │  + SHA-3 Hash    │               │
│                     └──────────────────┘               │
│                                                          │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   AES Key    │ ───▶ │    CP-ABE    │               │
│  │ (Symmetric)  │      │  Encryption  │               │
│  └──────────────┘      └──────┬───────┘               │
│                               │                         │
│                               ▼                         │
│                     ┌──────────────────┐               │
│                     │  Access Policy   │               │
│                     │  "Doctor AND     │               │
│                     │   Cardiology"    │               │
│                     └──────────────────┘               │
│                                                          │
│  Decryption: User Attributes → Policy Match → Decrypt  │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
cys/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── config/
│   ├── config.yaml                 # System configuration
│   └── policies.json               # Predefined access policies
├── src/
│   ├── __init__.py
│   ├── crypto/                     # Cryptographic modules
│   │   ├── __init__.py
│   │   ├── cpabe.py               # CP-ABE implementation
│   │   ├── aes_encryption.py      # AES-256 encryption
│   │   ├── hash_integrity.py      # SHA-3 hashing
│   │   └── key_manager.py         # Secure key generation
│   ├── access_control/             # Access control logic
│   │   ├── __init__.py
│   │   ├── user_manager.py        # User attribute management
│   │   ├── policy_engine.py       # Policy creation/validation
│   │   └── attribute_manager.py   # Attribute assignment
│   ├── services/                   # Core services
│   │   ├── __init__.py
│   │   ├── encryption_service.py  # Hybrid encryption service
│   │   ├── decryption_service.py  # Controlled decryption
│   │   └── integrity_service.py   # Integrity verification
│   └── models/                     # Data models
│       ├── __init__.py
│       ├── user.py                # User model
│       ├── policy.py              # Policy model
│       └── encrypted_file.py      # Encrypted file model
├── api/                            # REST API (Flask/FastAPI)
│   ├── __init__.py
│   ├── app.py                     # API application
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication
│   │   ├── encryption.py          # Encryption endpoints
│   │   ├── decryption.py          # Decryption endpoints
│   │   └── admin.py               # Admin operations
│   └── middleware/
│       ├── __init__.py
│       └── auth_middleware.py     # Authentication middleware
├── storage/                        # File storage
│   ├── encrypted/                 # Encrypted patient files
│   ├── keys/                      # CP-ABE keys (secure)
│   └── metadata/                  # File metadata
├── tests/                          # Unit and integration tests
│   ├── __init__.py
│   ├── test_cpabe.py
│   ├── test_aes.py
│   ├── test_integrity.py
│   ├── test_encryption_service.py
│   └── test_decryption_service.py
├── scripts/                        # Utility scripts
│   ├── setup_system.py            # Initial setup
│   ├── create_user.py             # Create users
│   ├── encrypt_file.py            # Encrypt file CLI
│   └── decrypt_file.py            # Decrypt file CLI
└── examples/                       # Usage examples
    ├── basic_encryption.py
    ├── policy_creation.py
    └── user_management.py
```

## 🚀 Quick Start

### 1. Installation

```bash
cd cys
pip install -r requirements.txt
python scripts/setup_system.py
```

### 2. Create Users

```bash
# Create a doctor
python scripts/create_user.py --role Doctor --department Cardiology --name "Dr. Smith"

# Create a nurse
python scripts/create_user.py --role Nurse --department Emergency --name "Nurse Johnson"
```

### 3. Encrypt Patient File

```bash
python scripts/encrypt_file.py \
    --file patient_record.txt \
    --policy "(Doctor AND Cardiology) OR (Nurse AND Emergency)" \
    --patient-id P12345
```

### 4. Decrypt Patient File

```bash
python scripts/decrypt_file.py \
    --encrypted-file patient_record.enc \
    --user-id user_123 \
    --output decrypted_record.txt
```

## 🔑 Key Concepts

### User Attributes

Users are assigned attributes based on their role and context:

- **Role**: Doctor, Nurse, Lab, Admin
- **Department**: Cardiology, Emergency, Radiology, etc.
- **Clearance Level**: L1, L2, L3
- **Specialty**: Surgeon, Radiologist, etc.

### Access Policies

Policies are boolean expressions over attributes:

```python
# Simple policy
policy = "Doctor AND Cardiology"

# Complex policy with OR
policy = "(Doctor AND Cardiology) OR (Admin AND ClearanceLevel:L3)"

# Time-based policy (future enhancement)
policy = "Doctor AND Cardiology AND TimeWindow:9-17"
```

### Hybrid Encryption Flow

1. **Encryption**:
   - Generate random AES-256 key
   - Encrypt patient file with AES-256
   - Compute SHA-3 hash of encrypted file
   - Encrypt AES key with CP-ABE using access policy
   - Store: encrypted file + encrypted AES key + hash + metadata

2. **Decryption**:
   - Verify user attributes
   - Attempt CP-ABE decryption of AES key (policy check)
   - If successful, verify SHA-3 hash
   - Decrypt file with recovered AES key
   - Return plaintext file

## 🔬 Technical Details

### Cryptographic Primitives

- **CP-ABE**: Based on charm-crypto library (pairing-based cryptography)
- **AES-256**: CBC mode with PKCS7 padding
- **SHA-3**: 256-bit output for integrity verification
- **Key Derivation**: PBKDF2 for password-based keys

### Security Considerations

✅ **Implemented**:
- Secure random number generation
- Proper key separation (CP-ABE master key isolation)
- Integrity verification before decryption
- Attribute-based access control
- Encrypted key storage

⚠️ **Production Requirements**:
- Hardware Security Module (HSM) for master key
- Secure key deletion (memory wiping)
- Audit logging for all access attempts
- Rate limiting and intrusion detection
- Regular key rotation policies

## 📊 API Endpoints

```
POST   /api/encrypt          - Encrypt a file
POST   /api/decrypt          - Decrypt a file
GET    /api/files            - List accessible files
POST   /api/users            - Create user
PUT    /api/users/:id        - Update user attributes
POST   /api/policies         - Create access policy
GET    /api/policies/:id     - Get policy details
POST   /api/verify-integrity - Verify file integrity
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_cpabe.py -v

# Run with coverage
pytest --cov=src tests/
```

## 📄 License

MIT License - For educational and research purposes.

## ⚠️ Disclaimer

This system is designed for educational purposes. Production deployment requires:
- Security audit
- Compliance review (HIPAA, GDPR)
- Penetration testing
- Professional cryptographic review
