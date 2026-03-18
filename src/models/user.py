"""
User Model
Defines user structure with attributes for CP-ABE
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json


@dataclass
class User:
    """
    User model with attributes for attribute-based access control
    """
    user_id: str
    username: str
    full_name: str
    role: str  # Doctor, Nurse, Lab, Admin
    department: str  # Cardiology, Emergency, Radiology, etc.
    attributes: List[str] = field(default_factory=list)
    clearance_level: Optional[str] = None  # L1, L2, L3
    specialty: Optional[str] = None  # Surgeon, Radiologist, etc.
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Auto-generate attributes from role and department"""
        if not self.attributes:
            self.attributes = self.generate_attributes()
    
    def generate_attributes(self) -> List[str]:
        """
        Generate CP-ABE attributes from user properties
        
        Returns:
            List of attribute strings
        """
        attrs = []
        
        # Add role
        if self.role:
            attrs.append(self.role)
        
        # Add department
        if self.department:
            attrs.append(self.department)
        
        # Add clearance level
        if self.clearance_level:
            attrs.append(f"ClearanceLevel:{self.clearance_level}")
        
        # Add specialty
        if self.specialty:
            attrs.append(f"Specialty:{self.specialty}")
        
        # Add combination attributes
        if self.role and self.department:
            attrs.append(f"{self.role}_{self.department}")
        
        return attrs
    
    def add_attribute(self, attribute: str):
        """Add an attribute to the user"""
        if attribute not in self.attributes:
            self.attributes.append(attribute)
            self.updated_at = datetime.now()
    
    def remove_attribute(self, attribute: str):
        """Remove an attribute from the user"""
        if attribute in self.attributes:
            self.attributes.remove(attribute)
            self.updated_at = datetime.now()
    
    def has_attribute(self, attribute: str) -> bool:
        """Check if user has a specific attribute"""
        return attribute in self.attributes
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'department': self.department,
            'attributes': self.attributes,
            'clearance_level': self.clearance_level,
            'specialty': self.specialty,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary"""
        # Convert datetime strings
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert user to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'User':
        """Create user from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        return f"User(id={self.user_id}, name={self.full_name}, role={self.role}, dept={self.department})"


# Example usage
if __name__ == "__main__":
    print("=== User Model Test ===\n")
    
    # Create users
    doctor = User(
        user_id="U001",
        username="dr.smith",
        full_name="Dr. John Smith",
        role="Doctor",
        department="Cardiology",
        clearance_level="L3",
        specialty="Surgeon",
        email="john.smith@hospital.com",
        phone="+1-555-0101"
    )
    
    nurse = User(
        user_id="U002",
        username="nurse.johnson",
        full_name="Sarah Johnson",
        role="Nurse",
        department="Emergency",
        clearance_level="L2",
        email="sarah.johnson@hospital.com"
    )
    
    lab_tech = User(
        user_id="U003",
        username="lab.wilson",
        full_name="Mike Wilson",
        role="Lab",
        department="Pathology",
        clearance_level="L1"
    )
    
    admin = User(
        user_id="U004",
        username="admin.davis",
        full_name="Emma Davis",
        role="Admin",
        department="IT",
        clearance_level="L3"
    )
    
    users = [doctor, nurse, lab_tech, admin]
    
    # Display users
    print("Created Users:")
    for user in users:
        print(f"\n{user}")
        print(f"  Attributes: {', '.join(user.attributes)}")
        print(f"  Email: {user.email}")
        print(f"  Active: {user.is_active}")
    
    print("\n" + "="*50 + "\n")
    
    # Test attribute management
    print("Testing Attribute Management:")
    print(f"\nDoctor has 'Cardiology': {doctor.has_attribute('Cardiology')}")
    print(f"Doctor has 'Emergency': {doctor.has_attribute('Emergency')}")
    
    # Add custom attribute
    doctor.add_attribute("VIPAccess")
    print(f"\nAfter adding 'VIPAccess': {doctor.attributes}")
    
    # Remove attribute
    doctor.remove_attribute("VIPAccess")
    print(f"After removing 'VIPAccess': {doctor.attributes}")
    
    print("\n" + "="*50 + "\n")
    
    # Test serialization
    print("Testing Serialization:")
    
    # To dict
    doctor_dict = doctor.to_dict()
    print(f"\nDoctor as dict: {json.dumps(doctor_dict, indent=2)}")
    
    # From dict
    doctor_restored = User.from_dict(doctor_dict)
    print(f"\nRestored doctor: {doctor_restored}")
    print(f"Attributes match: {doctor.attributes == doctor_restored.attributes}")
    
    print("\n=== Test Complete ===")
