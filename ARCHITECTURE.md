# System Architecture - Healthcare CP-ABE System

## Overview

The Secure Healthcare Data Access System implements a multi-layered security architecture combining:
- **CP-ABE (Ciphertext-Policy Attribute-Based Encryption)** for fine-grained access control
- **AES-256** for efficient symmetric encryption of large files
- **SHA-3** for cryptographic integrity verification

## System Layers

### 1. Cryptographic Layer (`src/crypto/`)

**Components:**
- `cpabe.py` - CP-ABE engine using charm-crypto (pairing-based cryptography)
- `aes_encryption.py` - AES-256-CBC implementation
- `hash_integrity.py` - SHA-3 integrity verification
- `key_manager.py` - Secure key generation and storage

**Flow:**
```
┌─────────────────────────────────────────────────────────────┐
│                   CRYPTOGRAPHIC LAYER                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │   CP-ABE     │   │   AES-256    │   │    SHA-3     │   │
│  │   Engine     │   │  Encryption  │   │   Integrity  │   │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘   │
│         │                  │                   │            │
│         │ Policy-based     │ File encryption  │ Hash       │
│         │ key protection   │                   │ generation │
│         └──────────────────┴───────────────────┘            │
│                             │                                │
│                    ┌────────▼────────┐                      │
│                    │  Key Manager    │                      │
│                    │  • Generation   │                      │
│                    │  • Storage      │                      │
│                    │  • Rotation     │                      │
│                    └─────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

### 2. Access Control Layer (`src/access_control/`)

**Components:**
- `user_manager.py` - User CRUD and attribute management
- `policy_engine.py` - Policy creation and evaluation
- `attribute_manager.py` - Attribute validation and hierarchy

**Attribute-Based Access Control (ABAC):**
```
┌─────────────────────────────────────────────────────────────┐
│                  ACCESS CONTROL LAYER                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Attributes          Policy Expression                 │
│  ┌──────────────┐        ┌──────────────────┐              │
│  │ • Doctor     │        │ "Doctor AND      │              │
│  │ • Cardiology │   VS   │  Cardiology"     │  → Decision  │
│  │ • L3         │        │                  │              │
│  └──────────────┘        └──────────────────┘              │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │         Attribute Manager                     │          │
│  │  • Predefined: Roles, Departments, Clearance │          │
│  │  • Custom: Organization-specific attributes  │          │
│  │  • Hierarchy: L3 implies L2, L2 implies L1   │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │           Policy Engine                       │          │
│  │  • Create policies from templates            │          │
│  │  • Validate policy expressions                │          │
│  │  • Evaluate policies against user attributes  │          │
│  └──────────────────────────────────────────────┘          │
│                                                              │
│  ┌──────────────────────────────────────────────┐          │
│  │           User Manager                        │          │
│  │  • Create/update users                        │          │
│  │  • Assign/revoke attributes                   │          │
│  │  • Persist user data                          │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 3. Service Layer (`src/services/`)

**Components:**
- `encryption_service.py` - Hybrid encryption orchestration
- `decryption_service.py` - Controlled decryption with policy checks

**Encryption Flow:**
```
┌─────────────────────────────────────────────────────────────┐
│                    ENCRYPTION SERVICE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: Patient File (Plaintext)                            │
│         ↓                                                    │
│  ┌─────────────────────────┐                                │
│  │ 1. Generate AES-256 Key │                                │
│  └───────────┬─────────────┘                                │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 2. Encrypt File (AES)   │  ────→  Encrypted File        │
│  └───────────┬─────────────┘         + IV                   │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 3. Compute SHA-3 Hash   │  ────→  Integrity Hash        │
│  └───────────┬─────────────┘                                │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 4. Encrypt AES Key      │                                │
│  │    using CP-ABE with    │  ────→  Encrypted Key         │
│  │    Access Policy        │         + Policy              │
│  └───────────┬─────────────┘                                │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 5. Store All Components │                                │
│  │  • Encrypted file       │                                │
│  │  • Encrypted AES key    │                                │
│  │  • Metadata (IV, hash)  │                                │
│  └─────────────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

**Decryption Flow:**
```
┌─────────────────────────────────────────────────────────────┐
│                    DECRYPTION SERVICE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input: File ID + User + User Private Key                   │
│         ↓                                                    │
│  ┌─────────────────────────┐                                │
│  │ 1. Load Metadata        │                                │
│  └───────────┬─────────────┘                                │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 2. Verify SHA-3 Hash    │                                │
│  │    (Integrity Check)    │  ──✓──→  Continue             │
│  └───────────┬─────────────┘  ──✗──→  ABORT                │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 3. Load Encrypted Key   │                                │
│  └───────────┬─────────────┘                                │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 4. Decrypt AES Key      │                                │
│  │    using CP-ABE         │                                │
│  │    (POLICY CHECK)       │  ──✓──→  AES Key Recovered    │
│  └───────────┬─────────────┘  ──✗──→  ACCESS DENIED        │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 5. Decrypt File (AES)   │  ────→  Plaintext File        │
│  └───────────┬─────────────┘                                │
│              ↓                                               │
│  ┌─────────────────────────┐                                │
│  │ 6. Log Access Attempt   │  ────→  Audit Log             │
│  └─────────────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

### 4. Model Layer (`src/models/`)

**Data Models:**
- `user.py` - User with attributes
- `policy.py` - Access policy with expression
- `encrypted_file.py` - Encrypted file metadata

**Entity Relationships:**
```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    User     │         │   Policy    │         │  Encrypted  │
│             │         │             │         │    File     │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ user_id     │         │ policy_id   │         │ file_id     │
│ username    │         │ name        │◄───────┤ policy_id   │
│ role        │         │ expression  │         │ patient_id  │
│ department  │         │ description │         │ aes_key_id  │
│ attributes[]│         │ is_active   │         │ iv          │
│ clearance   │         │             │         │ hash        │
└─────────────┘         └─────────────┘         └─────────────┘
      │                                                 │
      │ has CP-ABE                                     │
      │ private key                                     │
      └─────────────────────────────────────────────────┘
                   Can decrypt if attributes
                   satisfy policy expression
```

## Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│                     SECURITY LAYERS                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Authentication                                     │
│  ┌────────────────────────────────────────────┐            │
│  │ • User authentication (future: MFA)        │            │
│  │ • Session management                        │            │
│  └────────────────────────────────────────────┘            │
│                                                              │
│  Layer 2: Authorization (Attribute-Based)                   │
│  ┌────────────────────────────────────────────┐            │
│  │ • CP-ABE policy enforcement                │            │
│  │ • Attribute verification                    │            │
│  │ • Role-based clearance levels               │            │
│  └────────────────────────────────────────────┘            │
│                                                              │
│  Layer 3: Encryption                                        │
│  ┌────────────────────────────────────────────┐            │
│  │ • AES-256 for data                         │            │
│  │ • CP-ABE for key protection                │            │
│  │ • Secure key generation (CSPRNG)           │            │
│  └────────────────────────────────────────────┘            │
│                                                              │
│  Layer 4: Integrity                                         │
│  ┌────────────────────────────────────────────┐            │
│  │ • SHA-3 hashing                             │            │
│  │ • Tamper detection                          │            │
│  │ • Pre-decryption verification               │            │
│  └────────────────────────────────────────────┘            │
│                                                              │
│  Layer 5: Audit                                             │
│  ┌────────────────────────────────────────────┐            │
│  │ • Access logging                            │            │
│  │ • Policy change tracking                    │            │
│  │ • User activity monitoring                  │            │
│  └────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Key Security Properties

1. **Confidentiality**: Files encrypted with AES-256, keys protected by CP-ABE
2. **Access Control**: Fine-grained, attribute-based policies
3. **Integrity**: SHA-3 hashing ensures tamper detection
4. **Auditability**: All access attempts logged
5. **Non-repudiation**: Cryptographic proof of access
6. **Key Security**: Master keys isolated, user keys attribute-specific

## Deployment Architecture

### Recommended Production Setup

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Web/Mobile │         │   REST API   │                 │
│  │   Frontend   │────────▶│   (FastAPI)  │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                   │                          │
│                           ┌───────▼────────┐                │
│                           │  Application   │                │
│                           │     Layer      │                │
│                           │  • Encryption  │                │
│                           │  • Decryption  │                │
│                           │  • Access Ctrl │                │
│                           └───────┬────────┘                │
│                                   │                          │
│              ┌────────────────────┼────────────────────┐    │
│              │                    │                    │    │
│      ┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│      │   PostgreSQL   │  │   File Storage │  │      HSM       │
│      │   (Metadata)   │  │   (Encrypted)  │  │  (Master Keys) │
│      └────────────────┘  └────────────────┘  └────────────────┘
│                                                              │
│  Additional Components:                                      │
│  • Load Balancer (nginx/HAProxy)                            │
│  • TLS/SSL Termination                                      │
 │  • Rate Limiting & WAF                                      │
│  • Intrusion Detection System                               │
│  • Backup & Disaster Recovery                               │
└─────────────────────────────────────────────────────────────┘
```

## Performance Considerations

### Optimization Strategies

1. **Large Files**: Streaming encryption/decryption with chunking
2. **Caching**: Cache policies and user attributes (with TTL)
3. **Async Operations**: Use async I/O for file operations
4. **Key Caching**: Cache decrypted AES keys temporarily (with secure deletion)
5. **Database Indexing**: Index on user_id, policy_id, patient_id

### Scalability

- **Horizontal Scaling**: Stateless services can be load-balanced
- **Key Storage**: Distribute keys across multiple HSMs
- **File Storage**: Use distributed file systems (S3, MinIO)
- **Database**: PostgreSQL replication for read scalability

## Compliance & Standards

### Healthcare Compliance

- **HIPAA**: Health Insurance Portability and Accountability Act
  - ✓ Access controls
  - ✓ Audit trails
  - ✓ Encryption at rest
  - ✓ Integrity verification

- **GDPR**: General Data Protection Regulation
  - ✓ Data minimization
  - ✓ Purpose limitation
  - ✓ Access control
  - ✓ Right to erasure (deletion support)

### Cryptographic Standards

- **NIST**: National Institute of Standards and Technology
  - AES-256 (FIPS 197)
  - SHA-3 (FIPS 202)
  - Secure random number generation (SP 800-90A)

## Future Enhancements

1. **Time-Based Policies**: Add temporal constraints to policies
2. **Multi-Factor Authentication**: Enhance user authentication
3. **Key Escrow**: Emergency access mechanisms
4. **Blockchain Audit Trail**: Immutable audit logging
5. **Homomorphic Encryption**: Compute on encrypted data
6. **Federated Learning**: Privacy-preserving analytics
7. **Quantum-Resistant Crypto**: Post-quantum cryptography
8. **Mobile SDK**: Native iOS/Android libraries

## Conclusion

This architecture provides:
- ✅ Strong encryption (AES-256 + CP-ABE)
- ✅ Fine-grained access control (attribute-based)
- ✅ Data integrity (SHA-3)
- ✅ Auditability (comprehensive logging)
- ✅ Scalability (modular design)
- ✅ Compliance-ready (HIPAA, GDPR)
