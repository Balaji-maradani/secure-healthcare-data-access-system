"""
User Manager
Handles user creation, attribute assignment, and management
"""

import os
import json
import secrets
from typing import Dict, List, Optional
from datetime import datetime

from ..models.user import User


class UserManager:
    """
    User Management System
    
    Handles user lifecycle, attribute assignment, and persistence.
    """
    
    def __init__(self, storage_dir: str = "storage/users"):
        """
        Initialize user manager
        
        Args:
            storage_dir: Directory to store user data
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        self._users: Dict[str, User] = {}
        self._load_users()
    
    def create_user(self,
                   username: str,
                   full_name: str,
                   role: str,
                   department: str,
                   clearance_level: Optional[str] = None,
                   specialty: Optional[str] = None,
                   email: Optional[str] = None,
                   phone: Optional[str] = None,
                   custom_attributes: Optional[List[str]] = None) -> User:
        """
        Create a new user with attributes
        
        Args:
            username: Unique username
            full_name: User's full name
            role: User role (Doctor, Nurse, Lab, Admin)
            department: Department
            clearance_level: Security clearance (L1, L2, L3)
            specialty: Medical specialty
            email: Email address
            phone: Phone number
            custom_attributes: Additional custom attributes
            
        Returns:
            Created User object
            
        Example:
            >>> user = manager.create_user(
            ...     "dr.smith",
            ...     "Dr. John Smith",
            ...     "Doctor",
            ...     "Cardiology",
            ...     clearance_level="L3"
            ... )
        """
        # Validate role
        valid_roles = ["Doctor", "Nurse", "Lab", "Admin", "Technician", "Radiologist"]
        if role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        # Check if username exists
        if self.get_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        # Generate user ID
        user_id = self._generate_user_id()
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            full_name=full_name,
            role=role,
            department=department,
            clearance_level=clearance_level,
            specialty=specialty,
            email=email,
            phone=phone
        )
        
        # Add custom attributes
        if custom_attributes:
            for attr in custom_attributes:
                user.add_attribute(attr)
        
        # Store user
        self._users[user_id] = user
        self._save_user(user)
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User identifier
            
        Returns:
            User object or None
        """
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User object or None
        """
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update user information
        
        Args:
            user_id: User identifier
            **kwargs: Fields to update
            
        Returns:
            Updated User object or None
        """
        user = self.get_user(user_id)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['full_name', 'email', 'phone', 'department', 
                         'clearance_level', 'specialty', 'is_active']
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(user, key, value)
        
        user.updated_at = datetime.now()
        
        # Regenerate attributes if department or role changed
        if 'department' in kwargs or 'clearance_level' in kwargs or 'specialty' in kwargs:
            user.attributes = user.generate_attributes()
        
        self._save_user(user)
        return user
    
    def add_user_attribute(self, user_id: str, attribute: str) -> bool:
        """
        Add attribute to user
        
        Args:
            user_id: User identifier
            attribute: Attribute to add
            
        Returns:
            True if added, False if user not found
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.add_attribute(attribute)
        self._save_user(user)
        return True
    
    def remove_user_attribute(self, user_id: str, attribute: str) -> bool:
        """
        Remove attribute from user
        
        Args:
            user_id: User identifier
            attribute: Attribute to remove
            
        Returns:
            True if removed, False if user not found
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.remove_attribute(attribute)
        self._save_user(user)
        return True
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate user account
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deactivated, False if not found
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.now()
        self._save_user(user)
        return True
    
    def activate_user(self, user_id: str) -> bool:
        """
        Activate user account
        
        Args:
            user_id: User identifier
            
        Returns:
            True if activated, False if not found
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.is_active = True
        user.updated_at = datetime.now()
        self._save_user(user)
        return True
    
    def list_users(self, 
                  role: Optional[str] = None,
                  department: Optional[str] = None,
                  is_active: Optional[bool] = None) -> List[User]:
        """
        List users with optional filters
        
        Args:
            role: Filter by role
            department: Filter by department
            is_active: Filter by active status
            
        Returns:
            List of User objects
        """
        users = list(self._users.values())
        
        if role:
            users = [u for u in users if u.role == role]
        
        if department:
            users = [u for u in users if u.department == department]
        
        if is_active is not None:
            users = [u for u in users if u.is_active == is_active]
        
        return users
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user (permanent)
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        if user_id not in self._users:
            return False
        
        # Remove from memory
        del self._users[user_id]
        
        # Delete file
        user_file = os.path.join(self.storage_dir, f"{user_id}.json")
        if os.path.exists(user_file):
            os.remove(user_file)
        
        return True
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"U{secrets.token_hex(6).upper()}"
    
    def _save_user(self, user: User):
        """Save user to file"""
        user_file = os.path.join(self.storage_dir, f"{user.user_id}.json")
        with open(user_file, 'w') as f:
            f.write(user.to_json())
    
    def _load_users(self):
        """Load all users from storage"""
        if not os.path.exists(self.storage_dir):
            return
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                user_file = os.path.join(self.storage_dir, filename)
                with open(user_file, 'r') as f:
                    user = User.from_json(f.read())
                    self._users[user.user_id] = user


# Example usage
if __name__ == "__main__":
    print("=== User Manager Test ===\n")
    
    # Initialize manager
    manager = UserManager("test_users")
    
    # Create users
    print("1. Creating users...\n")
    
    doctor = manager.create_user(
        username="dr.smith",
        full_name="Dr. John Smith",
        role="Doctor",
        department="Cardiology",
        clearance_level="L3",
        specialty="Surgeon",
        email="john.smith@hospital.com",
        phone="+1-555-0101"
    )
    print(f"   Created: {doctor}")
    print(f"   Attributes: {', '.join(doctor.attributes)}\n")
    
    nurse = manager.create_user(
        username="nurse.johnson",
        full_name="Sarah Johnson",
        role="Nurse",
        department="Emergency",
        clearance_level="L2",
        email="sarah.j@hospital.com"
    )
    print(f"   Created: {nurse}")
    print(f"   Attributes: {', '.join(nurse.attributes)}\n")
    
    lab_tech = manager.create_user(
        username="lab.wilson",
        full_name="Mike Wilson",
        role="Lab",
        department="Pathology",
        clearance_level="L1"
    )
    print(f"   Created: {lab_tech}")
    print(f"   Attributes: {', '.join(lab_tech.attributes)}\n")
    
    # List users
    print("2. Listing all users:")
    all_users = manager.list_users()
    for user in all_users:
        print(f"   - {user.username}: {user.full_name} ({user.role}, {user.department})")
    print()
    
    # Filter users
    print("3. Filtering users:")
    doctors = manager.list_users(role="Doctor")
    print(f"   Doctors: {len(doctors)}")
    for d in doctors:
        print(f"   - {d.full_name}")
    print()
    
    # Update user
    print("4. Updating user...")
    manager.update_user(doctor.user_id, clearance_level="L2", phone="+1-555-9999")
    updated_doctor = manager.get_user(doctor.user_id)
    print(f"   Updated clearance: {updated_doctor.clearance_level}")
    print(f"   Updated phone: {updated_doctor.phone}")
    print(f"   Updated attributes: {', '.join(updated_doctor.attributes)}\n")
    
    # Add/remove attributes
    print("5. Managing attributes...")
    manager.add_user_attribute(doctor.user_id, "VIPAccess")
    doctor = manager.get_user(doctor.user_id)
    print(f"   After adding VIPAccess: {', '.join(doctor.attributes)}")
    
    manager.remove_user_attribute(doctor.user_id, "VIPAccess")
    doctor = manager.get_user(doctor.user_id)
    print(f"   After removing VIPAccess: {', '.join(doctor.attributes)}\n")
    
    # Deactivate user
    print("6. Deactivating user...")
    manager.deactivate_user(nurse.user_id)
    nurse = manager.get_user(nurse.user_id)
    print(f"   Nurse active status: {nurse.is_active}\n")
    
    # Get by username
    print("7. Get user by username...")
    found_user = manager.get_user_by_username("dr.smith")
    print(f"   Found: {found_user.full_name} (ID: {found_user.user_id})\n")
    
    # Cleanup
    print("8. Cleaning up...")
    import shutil
    shutil.rmtree("test_users")
    print("   ✓ Cleanup complete\n")
    
    print("=== Test Complete ===")
