"""
CP-ABE (Ciphertext-Policy Attribute-Based Encryption) Implementation
Using charm-crypto library for pairing-based cryptography
"""

import json
import pickle
from typing import Dict, List, Set, Any, Optional
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
import os


class CPABEEngine:
    """
    Ciphertext-Policy Attribute-Based Encryption Engine
    
    Implements CP-ABE for encrypting symmetric keys with embedded access policies.
    Decryption is only possible if user attributes satisfy the policy.
    """
    
    def __init__(self, curve: str = 'SS512'):
        """
        Initialize CP-ABE engine with pairing group
        
        Args:
            curve: Elliptic curve for pairing (default: SS512 for 80-bit security)
        """
        self.group = PairingGroup(curve)
        self.cpabe = CPabe_BSW07(self.group)
        self.master_public_key: Optional[Dict] = None
        self.master_secret_key: Optional[Dict] = None
        
    def setup(self) -> tuple[Dict, Dict]:
        """
        Generate master public and secret keys for the system
        
        Returns:
            (master_public_key, master_secret_key)
            
        Security Note:
            - Master secret key MUST be stored securely (HSM recommended)
            - Only trusted authority should have access to master secret key
        """
        (pk, msk) = self.cpabe.setup()
        
        self.master_public_key = pk
        self.master_secret_key = msk
        
        return pk, msk
    
    def generate_user_key(self, user_attributes: List[str]) -> Dict:
        """
        Generate private key for a user based on their attributes
        
        Args:
            user_attributes: List of attributes (e.g., ['Doctor', 'Cardiology', 'L3'])
            
        Returns:
            User's private decryption key
            
        Example:
            >>> engine = CPABEEngine()
            >>> engine.setup()
            >>> user_key = engine.generate_user_key(['Doctor', 'Cardiology'])
        """
        if not self.master_public_key or not self.master_secret_key:
            raise ValueError("System not initialized. Call setup() first.")
        
        if not user_attributes:
            raise ValueError("User must have at least one attribute")
        
        user_key = self.cpabe.keygen(
            self.master_public_key,
            self.master_secret_key,
            user_attributes
        )
        
        return user_key
    
    def encrypt_key(self, aes_key: bytes, access_policy: str) -> Dict[str, Any]:
        """
        Encrypt AES key using CP-ABE with access policy
        
        Args:
            aes_key: AES-256 symmetric key (32 bytes)
            access_policy: Boolean expression of attributes
                          e.g., "(Doctor AND Cardiology) OR Admin"
            
        Returns:
            Encrypted key structure containing:
                - ciphertext: CP-ABE encrypted key
                - policy: Access policy
                - metadata: Additional information
                
        Policy Syntax:
            - AND: Conjunction (both required)
            - OR: Disjunction (either required)
            - Parentheses for grouping
            
        Example:
            >>> ciphertext = engine.encrypt_key(aes_key, "Doctor AND Cardiology")
        """
        if not self.master_public_key:
            raise ValueError("System not initialized. Call setup() first.")
        
        if len(aes_key) != 32:
            raise ValueError("AES key must be 32 bytes for AES-256")
        
        # Validate policy syntax
        self._validate_policy(access_policy)
        
        # Convert AES key to group element for encryption
        key_element = self.group.hash(aes_key, GT)
        
        # Encrypt using CP-ABE
        ciphertext = self.cpabe.encrypt(
            self.master_public_key,
            key_element,
            access_policy
        )
        
        return {
            'ciphertext': ciphertext,
            'policy': access_policy,
            'version': '1.0',
            'curve': str(self.group.groupType())
        }
    
    def decrypt_key(self, encrypted_key: Dict[str, Any], user_key: Dict) -> Optional[bytes]:
        """
        Decrypt AES key using user's private key
        
        Args:
            encrypted_key: Encrypted key structure from encrypt_key()
            user_key: User's private key from generate_user_key()
            
        Returns:
            Decrypted AES key (32 bytes) if user attributes satisfy policy,
            None otherwise
            
        Example:
            >>> aes_key = engine.decrypt_key(encrypted_key, user_key)
            >>> if aes_key:
            ...     print("Access granted")
        """
        if not self.master_public_key:
            raise ValueError("System not initialized. Call setup() first.")
        
        try:
            # Attempt CP-ABE decryption
            key_element = self.cpabe.decrypt(
                self.master_public_key,
                user_key,
                encrypted_key['ciphertext']
            )
            
            if key_element is False:
                # Policy not satisfied
                return None
            
            # Convert group element back to bytes
            # We need to serialize and extract the original key
            # This is a simplified approach; production should use KDF
            key_bytes = self.group.serialize(key_element)
            
            # Extract 32 bytes for AES-256
            aes_key = key_bytes[:32]
            
            return aes_key
            
        except Exception as e:
            # Decryption failed (policy not satisfied or invalid key)
            print(f"Decryption failed: {e}")
            return None
    
    def _validate_policy(self, policy: str) -> bool:
        """
        Validate access policy syntax
        
        Args:
            policy: Access policy string
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If policy syntax is invalid
        """
        # Basic validation
        if not policy or not policy.strip():
            raise ValueError("Policy cannot be empty")
        
        # Check balanced parentheses
        if policy.count('(') != policy.count(')'):
            raise ValueError("Unbalanced parentheses in policy")
        
        # Policy should contain valid operators
        valid_operators = {'AND', 'OR', '(', ')'}
        tokens = policy.replace('(', ' ( ').replace(')', ' ) ').split()
        
        for token in tokens:
            if token.upper() in valid_operators:
                continue
            # Attributes should be alphanumeric with possible underscores/colons
            if not all(c.isalnum() or c in '_:' for c in token):
                raise ValueError(f"Invalid attribute name: {token}")
        
        return True
    
    def save_keys(self, public_key_path: str, secret_key_path: str):
        """
        Save master keys to files (SECURE STORAGE REQUIRED)
        
        Args:
            public_key_path: Path to save public key
            secret_key_path: Path to save secret key (MUST BE ENCRYPTED IN PRODUCTION)
        """
        if not self.master_public_key or not self.master_secret_key:
            raise ValueError("No keys to save. Call setup() first.")
        
        # Serialize keys
        pk_bytes = self.group.serialize(self.master_public_key)
        sk_bytes = self.group.serialize(self.master_secret_key)
        
        # Save to files
        with open(public_key_path, 'wb') as f:
            f.write(pk_bytes)
        
        # WARNING: In production, encrypt this file!
        with open(secret_key_path, 'wb') as f:
            f.write(sk_bytes)
        
        # Set restrictive permissions (Unix-like systems)
        try:
            os.chmod(secret_key_path, 0o600)
        except:
            pass
    
    def load_keys(self, public_key_path: str, secret_key_path: Optional[str] = None):
        """
        Load master keys from files
        
        Args:
            public_key_path: Path to public key file
            secret_key_path: Path to secret key file (optional)
        """
        with open(public_key_path, 'rb') as f:
            pk_bytes = f.read()
            self.master_public_key = self.group.deserialize(pk_bytes)
        
        if secret_key_path:
            with open(secret_key_path, 'rb') as f:
                sk_bytes = f.read()
                self.master_secret_key = self.group.deserialize(sk_bytes)
    
    def verify_attributes(self, user_attributes: Set[str], policy: str) -> bool:
        """
        Verify if user attributes satisfy access policy (without decryption)
        
        Args:
            user_attributes: Set of user attributes
            policy: Access policy
            
        Returns:
            True if attributes satisfy policy, False otherwise
            
        Note: This is a simplified check for demonstration
        """
        # Parse and evaluate policy
        # This is a simplified implementation
        policy_upper = policy.upper()
        
        # Replace AND/OR with Python operators
        eval_policy = policy_upper.replace(' AND ', ' and ').replace(' OR ', ' or ')
        
        # Replace attributes with True/False
        for attr in user_attributes:
            eval_policy = eval_policy.replace(attr.upper(), 'True')
        
        # Replace any remaining words (missing attributes) with False
        tokens = eval_policy.split()
        for i, token in enumerate(tokens):
            if token not in ['True', 'False', 'and', 'or', '(', ')']:
                if token.isalnum() or '_' in token or ':' in token:
                    tokens[i] = 'False'
        
        eval_policy = ' '.join(tokens)
        
        try:
            return eval(eval_policy)
        except:
            return False


# Example usage and testing
if __name__ == "__main__":
    print("=== CP-ABE Engine Test ===\n")
    
    # Initialize engine
    engine = CPABEEngine()
    
    # Setup system (generate master keys)
    print("1. Setting up CP-ABE system...")
    pk, msk = engine.setup()
    print("   ✓ Master keys generated\n")
    
    # Define users with attributes
    doctor_attrs = ['Doctor', 'Cardiology', 'L2']
    nurse_attrs = ['Nurse', 'Emergency', 'L1']
    admin_attrs = ['Admin', 'L3']
    
    # Generate user keys
    print("2. Generating user keys...")
    doctor_key = engine.generate_user_key(doctor_attrs)
    nurse_key = engine.generate_user_key(nurse_attrs)
    admin_key = engine.generate_user_key(admin_attrs)
    print(f"   ✓ Doctor key (attributes: {doctor_attrs})")
    print(f"   ✓ Nurse key (attributes: {nurse_attrs})")
    print(f"   ✓ Admin key (attributes: {admin_attrs})\n")
    
    # Create sample AES key
    import secrets
    aes_key = secrets.token_bytes(32)
    print("3. Generated AES-256 key\n")
    
    # Test policies
    policies = [
        "Doctor AND Cardiology",  # Only doctor should decrypt
        "Nurse OR Admin",          # Nurse or admin should decrypt
        "(Doctor AND Cardiology) OR (Admin AND L3)"  # Doctor or high-level admin
    ]
    
    print("4. Testing access policies...\n")
    
    for i, policy in enumerate(policies, 1):
        print(f"   Policy {i}: {policy}")
        
        # Encrypt AES key with policy
        encrypted = engine.encrypt_key(aes_key, policy)
        print(f"   ✓ Key encrypted with policy")
        
        # Test decryption by different users
        doctor_result = engine.decrypt_key(encrypted, doctor_key)
        nurse_result = engine.decrypt_key(encrypted, nurse_key)
        admin_result = engine.decrypt_key(encrypted, admin_key)
        
        print(f"   Doctor access: {'✓ GRANTED' if doctor_result else '✗ DENIED'}")
        print(f"   Nurse access:  {'✓ GRANTED' if nurse_result else '✗ DENIED'}")
        print(f"   Admin access:  {'✓ GRANTED' if admin_result else '✗ DENIED'}")
        print()
    
    print("=== Test Complete ===")
