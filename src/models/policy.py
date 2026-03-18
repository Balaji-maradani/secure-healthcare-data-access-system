"""
Policy Model
Defines access policy structure for CP-ABE
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
import re


@dataclass
class Policy:
    """
    Access policy model for CP-ABE encryption
    """
    policy_id: str
    name: str
    policy_expression: str  # Boolean expression: "(Doctor AND Cardiology) OR Admin"
    description: Optional[str] = None
    resource_type: Optional[str] = None  # e.g., "patient_records", "lab_reports"
    department: Optional[str] = None
    clearance_required: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    expires_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate policy expression on initialization"""
        self.validate()
    
    def validate(self) -> bool:
        """
        Validate policy expression syntax
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If policy syntax is invalid
        """
        expr = self.policy_expression
        
        if not expr or not expr.strip():
            raise ValueError("Policy expression cannot be empty")
        
        # Check balanced parentheses
        if expr.count('(') != expr.count(')'):
            raise ValueError("Unbalanced parentheses in policy expression")
        
        # Check for valid operators and attributes
        valid_operators = {'AND', 'OR', '(', ')'}
        tokens = expr.replace('(', ' ( ').replace(')', ' ) ').split()
        
        for token in tokens:
            if token.upper() in valid_operators:
                continue
            # Attributes should be alphanumeric with possible underscores/colons
            if not re.match(r'^[a-zA-Z0-9_:]+$', token):
                raise ValueError(f"Invalid attribute name: {token}")
        
        return True
    
    def get_required_attributes(self) -> List[str]:
        """
        Extract all attributes mentioned in the policy
        
        Returns:
            List of unique attributes
        """
        expr = self.policy_expression
        valid_operators = {'AND', 'OR', '(', ')'}
        tokens = expr.replace('(', ' ( ').replace(')', ' ) ').split()
        
        attributes = set()
        for token in tokens:
            if token.upper() not in valid_operators:
                attributes.add(token)
        
        return sorted(list(attributes))
    
    def is_expired(self) -> bool:
        """Check if policy has expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict:
        """Convert policy to dictionary"""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'policy_expression': self.policy_expression,
            'description': self.description,
            'resource_type': self.resource_type,
            'department': self.department,
            'clearance_required': self.clearance_required,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Policy':
        """Create policy from dictionary"""
        # Convert datetime strings
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if isinstance(data.get('expires_at'), str) and data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert policy to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Policy':
        """Create policy from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        return f"Policy(id={self.policy_id}, name={self.name}, expr={self.policy_expression})"


# Predefined policy templates
class PolicyTemplates:
    """Common policy templates for healthcare scenarios"""
    
    @staticmethod
    def doctor_only(department: Optional[str] = None) -> str:
        """Doctor-only access policy"""
        if department:
            return f"Doctor AND {department}"
        return "Doctor"
    
    @staticmethod
    def doctor_or_nurse(department: Optional[str] = None) -> str:
        """Doctor or nurse access policy"""
        if department:
            return f"(Doctor OR Nurse) AND {department}"
        return "Doctor OR Nurse"
    
    @staticmethod
    def high_clearance() -> str:
        """High clearance level required"""
        return "ClearanceLevel:L3"
    
    @staticmethod
    def department_specific(department: str, roles: List[str] = None) -> str:
        """Department-specific access"""
        if roles:
            role_expr = " OR ".join(roles)
            return f"({role_expr}) AND {department}"
        return department
    
    @staticmethod
    def admin_or_doctor(clearance: Optional[str] = None) -> str:
        """Admin or doctor with optional clearance"""
        if clearance:
            return f"Admin OR (Doctor AND ClearanceLevel:{clearance})"
        return "Admin OR Doctor"
    
    @staticmethod
    def emergency_access() -> str:
        """Emergency department full access"""
        return "(Doctor OR Nurse) AND Emergency"
    
    @staticmethod
    def lab_results() -> str:
        """Lab results access"""
        return "Lab OR Doctor OR (Nurse AND ClearanceLevel:L2)"
    
    @staticmethod
    def surgical_records() -> str:
        """Surgical records access"""
        return "Doctor AND (Specialty:Surgeon OR ClearanceLevel:L3)"


# Example usage
if __name__ == "__main__":
    print("=== Policy Model Test ===\n")
    
    # Create policies
    policies = [
        Policy(
            policy_id="POL001",
            name="Cardiology Patient Records",
            policy_expression="Doctor AND Cardiology",
            description="Access to cardiology patient records",
            resource_type="patient_records",
            department="Cardiology",
            created_by="admin"
        ),
        Policy(
            policy_id="POL002",
            name="Emergency Department Access",
            policy_expression="(Doctor OR Nurse) AND Emergency",
            description="Emergency department staff access",
            resource_type="patient_records",
            department="Emergency",
            created_by="admin"
        ),
        Policy(
            policy_id="POL003",
            name="High-Level Admin or Specialist",
            policy_expression="(Admin AND ClearanceLevel:L3) OR (Doctor AND Specialty:Surgeon)",
            description="High-level access for admins and surgeons",
            resource_type="surgical_records",
            clearance_required="L3",
            created_by="admin"
        ),
        Policy(
            policy_id="POL004",
            name="Lab Results View",
            policy_expression="Lab OR Doctor OR (Nurse AND ClearanceLevel:L2)",
            description="Access to laboratory test results",
            resource_type="lab_reports",
            created_by="admin"
        )
    ]
    
    # Display policies
    print("Created Policies:\n")
    for policy in policies:
        print(f"{policy}")
        print(f"  Description: {policy.description}")
        print(f"  Expression: {policy.policy_expression}")
        print(f"  Required Attributes: {', '.join(policy.get_required_attributes())}")
        print(f"  Resource Type: {policy.resource_type}")
        print(f"  Active: {policy.is_active}")
        print()
    
    print("="*50 + "\n")
    
    # Test policy templates
    print("Policy Templates:\n")
    
    templates = [
        ("Doctor Only (Cardiology)", PolicyTemplates.doctor_only("Cardiology")),
        ("Doctor or Nurse (General)", PolicyTemplates.doctor_or_nurse()),
        ("High Clearance", PolicyTemplates.high_clearance()),
        ("Emergency Access", PolicyTemplates.emergency_access()),
        ("Lab Results", PolicyTemplates.lab_results()),
        ("Surgical Records", PolicyTemplates.surgical_records()),
    ]
    
    for name, expr in templates:
        print(f"{name}:")
        print(f"  Expression: {expr}\n")
    
    print("="*50 + "\n")
    
    # Test serialization
    print("Testing Serialization:\n")
    
    # To JSON
    policy_json = policies[0].to_json()
    print(f"Policy as JSON:\n{policy_json}\n")
    
    # From JSON
    policy_restored = Policy.from_json(policy_json)
    print(f"Restored Policy: {policy_restored}")
    print(f"Expression matches: {policies[0].policy_expression == policy_restored.policy_expression}")
    
    print("\n=== Test Complete ===")
