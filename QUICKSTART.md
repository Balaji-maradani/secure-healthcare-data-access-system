# Quick Start Guide - Healthcare CP-ABE System

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Windows, Linux, or macOS

## Installation

### 1. Install Dependencies

```bash
cd cys
pip install -r requirements.txt
```

**Note:** Installing `charm-crypto` may require additional steps:

**On Windows:**
```bash
# Install Microsoft C++ Build Tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then install charm-crypto
pip install charm-crypto
```

**On Linux:**
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-dev libgmp-dev libmpfr-dev libmpc-dev

# Install charm-crypto
pip install charm-crypto
```

**On macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install gmp mpfr libmpc

# Install charm-crypto
pip install charm-crypto
```

### 2. Run Complete System Demo

```bash
cd examples
python complete_system_demo.py
```

This will:
- Initialize the CP-ABE system
- Create sample users (doctor, nurse, lab tech, admin)
- Generate CP-ABE keys for each user
- Create access policies
- Encrypt patient files with policies
- Test access control
- Demonstrate decryption based on attributes
- Show audit logs

### 3. Test Individual Modules

```bash
# Test CP-ABE engine
python src/crypto/cpabe.py

# Test AES encryption
python src/crypto/aes_encryption.py

# Test SHA-3 integrity
python src/crypto/hash_integrity.py

# Test key manager
python src/crypto/key_manager.py

# Test user manager
python src/access_control/user_manager.py

# Test policy engine
python src/access_control/policy_engine.py

# Test encryption service
python src/services/encryption_service.py

# Test decryption service
python src/services/decryption_service.py
```

## Basic Usage

### Create a New User

```python
from src.access_control.user_manager import UserManager

user_manager = UserManager()

doctor = user_manager.create_user(
    username="dr.smith",
    full_name="Dr. John Smith",
    role="Doctor",
    department="Cardiology",
    clearance_level="L3"
)

print(f"User attributes: {doctor.attributes}")
```

### Create an Access Policy

```python
from src.access_control.policy_engine import PolicyEngine

policy_engine = PolicyEngine()

policy = policy_engine.create_policy(
    name="Cardiology Access",
    policy_expression="Doctor AND Cardiology",
    description="Access to cardiology patient records"
)
```

### Encrypt a Patient File

```python
from src.crypto.cpabe import CPABEEngine
from src.crypto.key_manager import KeyManager
from src.services.encryption_service import EncryptionService

# Initialize
cpabe = CPABEEngine()
cpabe.setup()
key_manager = KeyManager()
encryption_service = EncryptionService(cpabe, key_manager)

# Encrypt file
encrypted_file = encryption_service.encrypt_file(
    input_file_path="patient_record.pdf",
    patient_id="P12345",
    policy_expression="Doctor AND Cardiology",
    encrypted_by="admin",
    file_type="medical_record"
)

print(f"File encrypted: {encrypted_file.file_id}")
```

### Decrypt a File

```python
from src.services.decryption_service import DecryptionService

# Initialize
decryption_service = DecryptionService(cpabe)

# Generate user key
user_key = cpabe.generate_user_key(doctor.attributes)

# Decrypt
success, error = decryption_service.decrypt_file(
    file_id=encrypted_file.file_id,
    user=doctor,
    user_private_key=user_key,
    output_path="decrypted_file.pdf"
)

if success:
    print("File decrypted successfully!")
else:
    print(f"Decryption failed: {error}")
```

## Project Structure

```
cys/
├── src/                        # Source code
│   ├── crypto/                # Cryptographic modules
│   ├── access_control/        # User and policy management
│   ├── services/              # Encryption/decryption services
│   └── models/                # Data models
├── examples/                   # Usage examples
├── config/                     # Configuration files
├── storage/                    # Data storage (created at runtime)
├── tests/                      # Unit tests
└── README.md                   # Project documentation
```

## Common Issues

### 1. charm-crypto Installation Fails

**Solution:** Install build dependencies first (see Installation section above)

### 2. ModuleNotFoundError

**Solution:** Make sure you're in the correct directory and have installed all dependencies:
```bash
pip install -r requirements.txt
```

### 3. Permission Denied on Key Files

**Solution:** Ensure the storage directories have proper permissions:
```bash
chmod 700 storage/keys  # On Unix-like systems
```

## Next Steps

1. **Customize Configuration:**
   Edit `config/config.yaml` to match your requirements

2. **Create Custom Policies:**
   Define organization-specific access policies

3. **Integrate with Database:**
   Add database support for user and policy persistence

4. **Build REST API:**
   Implement API endpoints for web/mobile applications

5. **Add Authentication:**
   Integrate with existing authentication systems (LDAP, OAuth, etc.)

## Security Recommendations

⚠️ **For Production Use:**

1. **Use Hardware Security Module (HSM)** for CP-ABE master keys
2. **Enable TLS/SSL** for all network communications
3. **Implement rate limiting** to prevent brute force attacks
4. **Enable comprehensive audit logging**
5. **Conduct regular security audits**
6. **Follow HIPAA/GDPR compliance** guidelines
7. **Implement key rotation policies**
8. **Use strong password policies**
9. **Enable multi-factor authentication**
10. **Regular backup and disaster recovery** procedures

## Support

For issues or questions:
- Check examples in `examples/` directory
- Review test cases in each module
- Consult `README.md` for detailed documentation

## License

MIT License - For educational and research purposes
