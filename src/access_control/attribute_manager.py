"""
Attribute Manager
Manages attribute definitions and assignments
"""

import os
import json
from typing import Dict, List, Set, Optional
from datetime import datetime


class Attribute Manager:
    """
    Attribute Management System
    
    Manages attribute definitions, hierarchies, and validations.
    """
    
    # Predefined attribute categories
    ROLES = ["Doctor", "Nurse", "Lab", "Admin", "Technician", "Radiologist", "Pharmacist"]
    DEPARTMENTS = [
        "Cardiology", "Emergency", "Radiology", "Pathology", "Surgery",
        "Pediatrics", "Oncology", "Neurology", "Orthopedics", "ICU",
        "Pharmacy", "IT", "Administration"
    ]
    CLEARANCE_LEVELS = ["L1", "L2", "L3"]
    SPECIALTIES = [
        "Surgeon", "Radiologist", "Pathologist", "Anesthesiologist",
        "Cardiologist", "Neurologist", "Oncologist", "Pediatrician",
        "General Practitioner"
    ]
    
    def __init__(self, storage_dir: str = "storage/attributes"):
        """
        Initialize attribute manager
        
        Args:
            storage_dir: Directory to store attribute definitions
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        self._custom_attributes: Dict[str, dict] = {}
        self._load_custom_attributes()
    
    def get_all_predefined_attributes(self) -> Dict[str, List[str]]:
        """
        Get all predefined attributes by category
        
        Returns:
            Dictionary of attribute categories and values
        """
        return {
            'roles': self.ROLES,
            'departments': self.DEPARTMENTS,
            'clearance_levels': self.CLEARANCE_LEVELS,
            'specialties': self.SPECIALTIES
        }
    
    def validate_attribute(self, attribute: str) -> tuple[bool, Optional[str]]:
        """
        Validate if attribute is valid
        
        Args:
            attribute: Attribute string
            
        Returns:
            (is_valid: bool, error_message: Optional[str])
        """
        # Check if it's a predefined attribute
        if attribute in self.ROLES:
            return True, None
        if attribute in self.DEPARTMENTS:
            return True, None
        if attribute in self.CLEARANCE_LEVELS:
            return True, None
        if attribute in self.SPECIALTIES:
            return True, None
        
        # Check if it's a qualified attribute (e.g., "ClearanceLevel:L2")
        if ':' in attribute:
            parts = attribute.split(':')
            if len(parts) == 2:
                category, value = parts
                if category == "ClearanceLevel" and value in self.CLEARANCE_LEVELS:
                    return True, None
                if category == "Specialty" and value in self.SPECIALTIES:
                    return True, None
        
        # Check custom attributes
        if attribute in self._custom_attributes:
            return True, None
        
        return False, f"Unknown attribute: {attribute}"
    
    def add_custom_attribute(self,
                           attribute_name: str,
                           category: str,
                           description: Optional[str] = None,
                           created_by: Optional[str] = None) -> bool:
        """
        Add a custom attribute definition
        
        Args:
            attribute_name: Name of the attribute
            category: Category (e.g., "custom_role", "special_access")
            description: Description of the attribute
            created_by: User who created the attribute
            
        Returns:
            True if added, False if already exists
        """
        if attribute_name in self._custom_attributes:
            return False
        
        self._custom_attributes[attribute_name] = {
            'name': attribute_name,
            'category': category,
            'description': description,
            'created_by': created_by,
            'created_at': datetime.now().isoformat()
        }
        
        self._save_custom_attributes()
        return True
    
    def remove_custom_attribute(self, attribute_name: str) -> bool:
        """
        Remove a custom attribute
        
        Args:
            attribute_name: Name of the attribute
            
        Returns:
            True if removed, False if not found
        """
        if attribute_name not in self._custom_attributes:
            return False
        
        del self._custom_attributes[attribute_name]
        self._save_custom_attributes()
        return True
    
    def get_custom_attributes(self) -> List[dict]:
        """
        Get all custom attributes
        
        Returns:
            List of custom attribute definitions
        """
        return list(self._custom_attributes.values())
    
    def get_attribute_info(self, attribute: str) -> Optional[dict]:
        """
        Get information about an attribute
        
        Args:
            attribute: Attribute name
            
        Returns:
            Attribute information or None
        """
        # Check predefined
        if attribute in self.ROLES:
            return {'name': attribute, 'category': 'role', 'predefined': True}
        if attribute in self.DEPARTMENTS:
            return {'name': attribute, 'category': 'department', 'predefined': True}
        if attribute in self.CLEARANCE_LEVELS:
            return {'name': attribute, 'category': 'clearance', 'predefined': True}
        if attribute in self.SPECIALTIES:
            return {'name': attribute, 'category': 'specialty', 'predefined': True}
        
        # Check custom
        if attribute in self._custom_attributes:
            info = self._custom_attributes[attribute].copy()
            info['predefined'] = False
            return info
        
        return None
    
    def suggest_attributes_for_role(self, role: str) -> List[str]:
        """
        Suggest common attributes for a role
        
        Args:
            role: User role
            
        Returns:
            List of suggested attributes
        """
        suggestions = [role]
        
        # Role-specific suggestions
        if role == "Doctor":
            suggestions.extend(["ClearanceLevel:L2", "ClearanceLevel:L3"])
        elif role == "Nurse":
            suggestions.extend(["ClearanceLevel:L1", "ClearanceLevel:L2"])
        elif role == "Admin":
            suggestions.extend(["ClearanceLevel:L3"])
        elif role == "Lab":
            suggestions.extend(["ClearanceLevel:L1"])
        
        return suggestions
    
    def get_attribute_hierarchy(self) -> Dict[str, List[str]]:
        """
        Get attribute hierarchy (which attributes imply others)
        
        Returns:
            Dictionary of attribute implications
        """
        hierarchy = {
            'ClearanceLevel:L3': ['ClearanceLevel:L2', 'ClearanceLevel:L1'],
            'ClearanceLevel:L2': ['ClearanceLevel:L1'],
            'Admin': ['ClearanceLevel:L3'],
        }
        
        return hierarchy
    
    def expand_attributes(self, attributes: Set[str]) -> Set[str]:
        """
        Expand attributes based on hierarchy
        
        Args:
            attributes: Set of explicit attributes
            
        Returns:
            Expanded set of attributes (including implied ones)
        """
        expanded = set(attributes)
        hierarchy = self.get_attribute_hierarchy()
        
        for attr in attributes:
            if attr in hierarchy:
                expanded.update(hierarchy[attr])
        
        return expanded
    
    def validate_attribute_set(self, attributes: Set[str]) -> tuple[bool, List[str]]:
        """
        Validate a set of attributes
        
        Args:
            attributes: Set of attributes to validate
            
        Returns:
            (all_valid: bool, invalid_attributes: List[str])
        """
        invalid = []
        
        for attr in attributes:
            is_valid, _ = self.validate_attribute(attr)
            if not is_valid:
                invalid.append(attr)
        
        return len(invalid) == 0, invalid
    
    def _save_custom_attributes(self):
        """Save custom attributes to file"""
        attr_file = os.path.join(self.storage_dir, "custom_attributes.json")
        with open(attr_file, 'w') as f:
            json.dump(self._custom_attributes, f, indent=2)
    
    def _load_custom_attributes(self):
        """Load custom attributes from file"""
        attr_file = os.path.join(self.storage_dir, "custom_attributes.json")
        
        if os.path.exists(attr_file):
            with open(attr_file, 'r') as f:
                self._custom_attributes = json.load(f)


# Example usage
if __name__ == "__main__":
    print("=== Attribute Manager Test ===\n")
    
    # Initialize manager
    manager = AttributeManager("test_attributes")
    
    # Get predefined attributes
    print("1. Predefined Attributes:\n")
    predefined = manager.get_all_predefined_attributes()
    for category, attrs in predefined.items():
        print(f"   {category.upper()}:")
        print(f"   {', '.join(attrs)}\n")
    
    # Validate attributes
    print("2. Validating Attributes:")
    
    test_attrs = [
        "Doctor",
        "Cardiology",
        "ClearanceLevel:L3",
        "InvalidAttribute",
        "Specialty:Surgeon"
    ]
    
    for attr in test_attrs:
        is_valid, error = manager.validate_attribute(attr)
        status = "✓ VALID" if is_valid else f"✗ INVALID: {error}"
        print(f"   {attr}: {status}")
    print()
    
    # Add custom attributes
    print("3. Adding Custom Attributes:")
    
    manager.add_custom_attribute(
        "VIPAccess",
        "special_access",
        "VIP patient access",
        "admin"
    )
    print("   ✓ Added: VIPAccess")
    
    manager.add_custom_attribute(
        "ResearchAccess",
        "special_access",
        "Access to research data",
        "admin"
    )
    print("   ✓ Added: ResearchAccess\n")
    
    # List custom attributes
    print("4. Custom Attributes:")
    custom = manager.get_custom_attributes()
    for attr in custom:
        print(f"   - {attr['name']}: {attr['description']}")
    print()
    
    # Suggest attributes for role
    print("5. Suggested Attributes for Roles:")
    
    for role in ["Doctor", "Nurse", "Admin"]:
        suggestions = manager.suggest_attributes_for_role(role)
        print(f"   {role}: {', '.join(suggestions)}")
    print()
    
    # Attribute hierarchy
    print("6. Attribute Hierarchy:")
    hierarchy = manager.get_attribute_hierarchy()
    for attr, implies in hierarchy.items():
        print(f"   {attr} implies: {', '.join(implies)}")
    print()
    
    # Expand attributes
    print("7. Attribute Expansion:")
    base_attrs = {"Doctor", "Cardiology", "ClearanceLevel:L3"}
    expanded_attrs = manager.expand_attributes(base_attrs)
    print(f"   Base: {', '.join(base_attrs)}")
    print(f"   Expanded: {', '.join(sorted(expanded_attrs))}\n")
    
    # Validate attribute set
    print("8. Validate Attribute Set:")
    
    valid_set = {"Doctor", "Cardiology", "ClearanceLevel:L2"}
    is_valid, invalid = manager.validate_attribute_set(valid_set)
    print(f"   Set 1: {', '.join(valid_set)}")
    print(f"   Result: {'✓ ALL VALID' if is_valid else f'✗ INVALID: {invalid}'}")
    
    invalid_set = {"Doctor", "InvalidDept", "ClearanceLevel:L9"}
    is_valid, invalid = manager.validate_attribute_set(invalid_set)
    print(f"\n   Set 2: {', '.join(invalid_set)}")
    print(f"   Result: {'✓ ALL VALID' if is_valid else f'✗ INVALID: {invalid}'}\n")
    
    # Cleanup
    print("9. Cleaning up...")
    import shutil
    shutil.rmtree("test_attributes")
    print("   ✓ Cleanup complete\n")
    
    print("=== Test Complete ===")
