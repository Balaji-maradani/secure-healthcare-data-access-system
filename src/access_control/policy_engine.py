"""
Policy Engine
Manages access policies for CP-ABE encryption
"""

import os
import json
import secrets
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from ..models.policy import Policy, PolicyTemplates


class PolicyEngine:
    """
    Policy Management and Validation Engine
    
    Handles creation, validation, and management of access policies.
    """
    
    def __init__(self, storage_dir: str = "storage/policies"):
        """
        Initialize policy engine
        
        Args:
            storage_dir: Directory to store policy data
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        self._policies: Dict[str, Policy] = {}
        self._load_policies()
    
    def create_policy(self,
                     name: str,
                     policy_expression: str,
                     description: Optional[str] = None,
                     resource_type: Optional[str] = None,
                     department: Optional[str] = None,
                     clearance_required: Optional[str] = None,
                     created_by: Optional[str] = None,
                     expires_in_days: Optional[int] = None) -> Policy:
        """
        Create a new access policy
        
        Args:
            name: Policy name
            policy_expression: Boolean expression (e.g., "Doctor AND Cardiology")
            description: Policy description
            resource_type: Type of resource (patient_records, lab_reports, etc.)
            department: Associated department
            clearance_required: Required clearance level
            created_by: User who created the policy
            expires_in_days: Number of days until policy expires
            
        Returns:
            Created Policy object
            
        Example:
            >>> policy = engine.create_policy(
            ...     "Cardiology Access",
            ...     "Doctor AND Cardiology",
            ...     description="Access to cardiology patient records"
            ... )
        """
        # Generate policy ID
        policy_id = self._generate_policy_id()
        
        # Calculate expiry
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Create policy
        policy = Policy(
            policy_id=policy_id,
            name=name,
            policy_expression=policy_expression,
            description=description,
            resource_type=resource_type,
            department=department,
            clearance_required=clearance_required,
            created_by=created_by,
            expires_at=expires_at
        )
        
        # Store policy
        self._policies[policy_id] = policy
        self._save_policy(policy)
        
        return policy
    
    def get_policy(self, policy_id: str) -> Optional[Policy]:
        """
        Get policy by ID
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            Policy object or None
        """
        return self._policies.get(policy_id)
    
    def get_policy_by_name(self, name: str) -> Optional[Policy]:
        """
        Get policy by name
        
        Args:
            name: Policy name
            
        Returns:
            Policy object or None
        """
        for policy in self._policies.values():
            if policy.name == name:
                return policy
        return None
    
    def update_policy(self, policy_id: str, **kwargs) -> Optional[Policy]:
        """
        Update policy
        
        Args:
            policy_id: Policy identifier
            **kwargs: Fields to update
            
        Returns:
            Updated Policy object or None
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return None
        
        # Update allowed fields
        allowed_fields = ['description', 'is_active', 'expires_at']
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(policy, key, value)
        
        policy.updated_at = datetime.now()
        self._save_policy(policy)
        return policy
    
    def deactivate_policy(self, policy_id: str) -> bool:
        """
        Deactivate a policy
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            True if deactivated, False if not found
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return False
        
        policy.is_active = False
        policy.updated_at = datetime.now()
        self._save_policy(policy)
        return True
    
    def list_policies(self,
                     resource_type: Optional[str] = None,
                     department: Optional[str] = None,
                     is_active: Optional[bool] = None) -> List[Policy]:
        """
        List policies with optional filters
        
        Args:
            resource_type: Filter by resource type
            department: Filter by department
            is_active: Filter by active status
            
        Returns:
            List of Policy objects
        """
        policies = list(self._policies.values())
        
        if resource_type:
            policies = [p for p in policies if p.resource_type == resource_type]
        
        if department:
            policies = [p for p in policies if p.department == department]
        
        if is_active is not None:
            policies = [p for p in policies if p.is_active == is_active and not p.is_expired()]
        
        return policies
    
    def validate_policy_expression(self, expression: str) -> tuple[bool, Optional[str]]:
        """
        Validate policy expression syntax
        
        Args:
            expression: Policy expression to validate
            
        Returns:
            (is_valid: bool, error_message: Optional[str])
        """
        try:
            # Create temporary policy to validate
            temp_policy = Policy(
                policy_id="TEMP",
                name="Temp",
                policy_expression=expression
            )
            return True, None
        except ValueError as e:
            return False, str(e)
    
    def evaluate_policy(self, policy_id: str, user_attributes: Set[str]) -> bool:
        """
        Evaluate if user attributes satisfy policy
        
        Args:
            policy_id: Policy identifier
            user_attributes: Set of user attributes
            
        Returns:
            True if policy is satisfied, False otherwise
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return False
        
        if not policy.is_active or policy.is_expired():
            return False
        
        # Parse and evaluate policy expression
        return self._evaluate_expression(policy.policy_expression, user_attributes)
    
    def _evaluate_expression(self, expression: str, attributes: Set[str]) -> bool:
        """
        Evaluate policy expression against user attributes
        
        Args:
            expression: Policy expression
            attributes: User attributes
            
        Returns:
            True if satisfied, False otherwise
        """
        # Convert to uppercase for case-insensitive matching
        expr_upper = expression.upper()
        
        # Replace AND/OR with Python operators
        eval_expr = expr_upper.replace(' AND ', ' and ').replace(' OR ', ' or ')
        
        # Replace attributes with True/False
        for attr in attributes:
            eval_expr = eval_expr.replace(attr.upper(), 'True')
        
        # Replace remaining tokens (missing attributes) with False
        tokens = eval_expr.split()
        for i, token in enumerate(tokens):
            if token not in ['True', 'False', 'and', 'or', '(', ')']:
                if token.replace('_', '').replace(':', '').isalnum():
                    tokens[i] = 'False'
        
        eval_expr = ' '.join(tokens)
        
        try:
            return eval(eval_expr)
        except:
            return False
    
    def get_required_attributes(self, policy_id: str) -> List[str]:
        """
        Get list of attributes required by policy
        
        Args:
            policy_id: Policy identifier
            
        Returns:
            List of required attributes
        """
        policy = self.get_policy(policy_id)
        if not policy:
            return []
        
        return policy.get_required_attributes()
    
    def find_matching_policies(self, user_attributes: Set[str]) -> List[Policy]:
        """
        Find all policies that user satisfies
        
        Args:
            user_attributes: User's attributes
            
        Returns:
            List of matching Policy objects
        """
        matching = []
        
        for policy in self._policies.values():
            if policy.is_active and not policy.is_expired():
                if self._evaluate_expression(policy.policy_expression, user_attributes):
                    matching.append(policy)
        
        return matching
    
    def create_from_template(self,
                           template_name: str,
                           name: str,
                           **kwargs) -> Policy:
        """
        Create policy from predefined template
        
        Args:
            template_name: Name of template (e.g., "doctor_only", "emergency_access")
            name: Policy name
            **kwargs: Additional arguments for template
            
        Returns:
            Created Policy object
        """
        templates = {
            'doctor_only': PolicyTemplates.doctor_only,
            'doctor_or_nurse': PolicyTemplates.doctor_or_nurse,
            'high_clearance': PolicyTemplates.high_clearance,
            'emergency_access': PolicyTemplates.emergency_access,
            'lab_results': PolicyTemplates.lab_results,
            'surgical_records': PolicyTemplates.surgical_records,
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        # Get template expression
        template_func = templates[template_name]
        
        # Call template function with appropriate arguments
        import inspect
        sig = inspect.signature(template_func)
        template_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        expression = template_func(**template_kwargs)
        
        # Create policy
        return self.create_policy(
            name=name,
            policy_expression=expression,
            **{k: v for k, v in kwargs.items() if k not in template_kwargs}
        )
    
    def _generate_policy_id(self) -> str:
        """Generate unique policy ID"""
        return f"POL{secrets.token_hex(6).upper()}"
    
    def_save_policy(self, policy: Policy):
        """Save policy to file"""
        policy_file = os.path.join(self.storage_dir, f"{policy.policy_id}.json")
        with open(policy_file, 'w') as f:
            f.write(policy.to_json())
    
    def _load_policies(self):
        """Load all policies from storage"""
        if not os.path.exists(self.storage_dir):
            return
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                policy_file = os.path.join(self.storage_dir, filename)
                with open(policy_file, 'r') as f:
                    policy = Policy.from_json(f.read())
                    self._policies[policy.policy_id] = policy


# Example usage
if __name__ == "__main__":
    print("=== Policy Engine Test ===\n")
    
    # Initialize engine
    engine = PolicyEngine("test_policies")
    
    # Create policies
    print("1. Creating policies...\n")
    
    cardiology_policy = engine.create_policy(
        name="Cardiology Patient Records",
        policy_expression="Doctor AND Cardiology",
        description="Access to cardiology patient records",
        resource_type="patient_records",
        department="Cardiology",
        created_by="admin"
    )
    print(f"   Created: {cardiology_policy.name}")
    print(f"   Expression: {cardiology_policy.policy_expression}")
    print(f"   Required attributes: {', '.join(cardiology_policy.get_required_attributes())}\n")
    
    emergency_policy = engine.create_policy(
        name="Emergency Department",
        policy_expression="(Doctor OR Nurse) AND Emergency",
        description="Emergency department access",
        resource_type="patient_records",
        department="Emergency",
        created_by="admin"
    )
    print(f"   Created: {emergency_policy.name}")
    print(f"   Expression: {emergency_policy.policy_expression}\n")
    
    # Create from template
    print("2. Creating policy from template...")
    lab_policy = engine.create_from_template(
        template_name="lab_results",
        name="Lab Results Access",
        description="Access to laboratory test results",
        resource_type="lab_reports",
        created_by="admin"
    )
    print(f"   Created: {lab_policy.name}")
    print(f"   Expression: {lab_policy.policy_expression}\n")
    
    # List policies
    print("3. Listing all policies:")
    all_policies = engine.list_policies()
    for policy in all_policies:
        print(f"   - {policy.name} ({policy.policy_id})")
    print()
    
    # Test policy evaluation
    print("4. Testing policy evaluation:\n")
    
    # Doctor in cardiology
    doctor_attrs = {'Doctor', 'Cardiology', 'ClearanceLevel:L2'}
    result = engine.evaluate_policy(cardiology_policy.policy_id, doctor_attrs)
    print(f"   Doctor (Cardiology) vs Cardiology Policy: {'✓ PASS' if result else '✗ FAIL'}")
    
    # Nurse in emergency
    nurse_attrs = {'Nurse', 'Emergency', 'ClearanceLevel:L1'}
    result = engine.evaluate_policy(emergency_policy.policy_id, nurse_attrs)
    print(f"   Nurse (Emergency) vs Emergency Policy: {'✓ PASS' if result else '✗ FAIL'}")
    
    # Nurse vs Cardiology (should fail)
    result = engine.evaluate_policy(cardiology_policy.policy_id, nurse_attrs)
    print(f"   Nurse (Emergency) vs Cardiology Policy: {'✗ FAIL (Expected)' if not result else '✓ PASS'}\n")
    
    # Find matching policies
    print("5. Finding matching policies for Doctor (Cardiology):")
    matching = engine.find_matching_policies(doctor_attrs)
    for policy in matching:
        print(f"   - {policy.name}")
    print()
    
    # Validate expressions
    print("6. Validating policy expressions:")
    
    valid_expr = "Doctor AND (Cardiology OR Emergency)"
    is_valid, error = engine.validate_policy_expression(valid_expr)
    print(f"   '{valid_expr}': {'✓ VALID' if is_valid else f'✗ INVALID: {error}'}")
    
    invalid_expr = "Doctor AND ((Cardiology"  # Unbalanced parentheses
    is_valid, error = engine.validate_policy_expression(invalid_expr)
    print(f"   '{invalid_expr}': {'✗ INVALID: {error}' if not is_valid else '✓ VALID'}\n")
    
    # Cleanup
    print("7. Cleaning up...")
    import shutil
    shutil.rmtree("test_policies")
    print("   ✓ Cleanup complete\n")
    
    print("=== Test Complete ===")
