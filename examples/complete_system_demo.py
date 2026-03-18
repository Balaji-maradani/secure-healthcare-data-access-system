"""
Complete System Integration Example
Demonstrates the full workflow of the Healthcare CP-ABE System
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.crypto.cpabe import CPABEEngine
from src.crypto.key_manager import KeyManager
from src.access_control.user_manager import UserManager
from src.access_control.policy_engine import PolicyEngine
from src.access_control.attribute_manager import AttributeManager
from src.services.encryption_service import EncryptionService
from src.services.decryption_service import DecryptionService


def print_section(title: str):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def main():
    print_section("HEALTHCARE DATA ACCESS SYSTEM - COMPLETE DEMO")
    
    # ========== STEP 1: INITIALIZE SYSTEM ==========
    print_section("STEP 1: System Initialization")
    
    print("Initializing CP-ABE engine...")
    cpabe = CPABEEngine()
    pk, msk = cpabe.setup()
    print("✓ CP-ABE master keys generated")
    
    print("\nInitializing system components...")
    key_manager = KeyManager("demo_storage/keys")
    user_manager = UserManager("demo_storage/users")
    policy_engine = PolicyEngine("demo_storage/policies")
    attr_manager = AttributeManager("demo_storage/attributes")
    encryption_service = EncryptionService(cpabe, key_manager, "demo_storage")
    decryption_service = DecryptionService(cpabe, "demo_storage")
    print("✓ All components initialized")
    
    # ========== STEP 2: CREATE USERS ==========
    print_section("STEP 2: Creating Healthcare Users")
    
    # Create doctor
    print("Creating Dr. Emily Carter (Cardiologist)...")
    dr_carter = user_manager.create_user(
        username="dr.carter",
        full_name="Dr. Emily Carter",
        role="Doctor",
        department="Cardiology",
        clearance_level="L3",
        specialty="Surgeon",
        email="emily.carter@hospital.com"
    )
    print(f"✓ Created: {dr_carter.full_name}")
    print(f"  Attributes: {', '.join(dr_carter.attributes)}")
    
    # Create nurse
    print("\nCreating Nurse Michael Brown (Emergency)...")
    nurse_brown = user_manager.create_user(
        username="nurse.brown",
        full_name="Nurse Michael Brown",
        role="Nurse",
        department="Emergency",
        clearance_level="L2",
        email="michael.brown@hospital.com"
    )
    print(f"✓ Created: {nurse_brown.full_name}")
    print(f"  Attributes: {', '.join(nurse_brown.attributes)}")
    
    # Create lab technician
    print("\nCreating Lab Tech Sarah Lee (Pathology)...")
    lab_lee = user_manager.create_user(
        username="lab.lee",
        full_name="Sarah Lee",
        role="Lab",
        department="Pathology",
        clearance_level="L1",
        email="sarah.lee@hospital.com"
    )
    print(f"✓ Created: {lab_lee.full_name}")
    print(f"  Attributes: {', '.join(lab_lee.attributes)}")
    
    # Create admin
    print("\nCreating Admin Lisa Wang...")
    admin_wang = user_manager.create_user(
        username="admin.wang",
        full_name="Lisa Wang",
        role="Admin",
        department="IT",
        clearance_level="L3",
        email="lisa.wang@hospital.com"
    )
    print(f"✓ Created: {admin_wang.full_name}")
    print(f"  Attributes: {', '.join(admin_wang.attributes)}")
    
    # ========== STEP 3: GENERATE USER KEYS ==========
    print_section("STEP 3: Generating CP-ABE User Keys")
    
    print("Generating private keys for users...")
    dr_carter_key = cpabe.generate_user_key(dr_carter.attributes)
    nurse_brown_key = cpabe.generate_user_key(nurse_brown.attributes)
    lab_lee_key = cpabe.generate_user_key(lab_lee.attributes)
    admin_wang_key = cpabe.generate_user_key(admin_wang.attributes)
    print("✓ All user keys generated")
    
    # ========== STEP 4: CREATE ACCESS POLICIES ==========
    print_section("STEP 4: Creating Access Policies")
    
    # Policy 1: Cardiology records
    cardiology_policy = policy_engine.create_policy(
        name="Cardiology Patient Records",
        policy_expression="Doctor AND Cardiology",
        description="Access to cardiology department patient records",
        resource_type="patient_records",
        department="Cardiology",
        created_by=admin_wang.user_id
    )
    print(f"✓ Created: {cardiology_policy.name}")
    print(f"  Expression: {cardiology_policy.policy_expression}")
    
    # Policy 2: Emergency access
    emergency_policy = policy_engine.create_policy(
        name="Emergency Patient Data",
        policy_expression="(Doctor OR Nurse) AND Emergency",
        description="Emergency department staff access",
        resource_type="patient_records",
        department="Emergency",
        created_by=admin_wang.user_id
    )
    print(f"\n✓ Created: {emergency_policy.name}")
    print(f"  Expression: {emergency_policy.policy_expression}")
    
    # Policy 3: Lab results
    lab_policy = policy_engine.create_from_template(
        template_name="lab_results",
        name="Laboratory Test Results",
        description="Access to lab test results",
        resource_type="lab_reports",
        created_by=admin_wang.user_id
    )
    print(f"\n✓ Created: {lab_policy.name}")
    print(f"  Expression: {lab_policy.policy_expression}")
    
    # Policy 4: High-level admin
    admin_policy = policy_engine.create_policy(
        name="Administrative Full Access",
        policy_expression="Admin AND ClearanceLevel:L3",
        description="Full administrative access",
        resource_type="all",
        created_by=admin_wang.user_id
    )
    print(f"\n✓ Created: {admin_policy.name}")
    print(f"  Expression: {admin_policy.policy_expression}")
    
    # ========== STEP 5: CREATE SAMPLE PATIENT FILES ==========
    print_section("STEP 5: Creating Sample Patient Files")
    
    # Cardiology patient file
    print("Creating cardiology patient record...")
    cardiology_file = "demo_cardiology_record.txt"
    with open(cardiology_file, 'w') as f:
        f.write("""
CONFIDENTIAL CARDIOLOGY PATIENT RECORD
=======================================
Patient ID: P20240001
Name: John Doe
DOB: 1968-05-15
Admission Date: 2024-01-20

DIAGNOSIS:
- Acute Myocardial Infarction (Heart Attack)
- Coronary Artery Disease
- Hypertension

PROCEDURES:
- Emergency Cardiac Catheterization (2024-01-20)
- Percutaneous Coronary Intervention (PCI) with Stent Placement
- ECG Monitoring

CURRENT MEDICATIONS:
- Aspirin 81mg daily
- Clopidogrel 75mg daily
- Atorvastatin 80mg daily
- Metoprolol 50mg twice daily
- Lisinopril 10mg daily

VITAL SIGNS (Latest):
- BP: 128/78 mmHg
- HR: 72 bpm
- Temp: 98.6°F
- O2 Sat: 97%

PROGNOSIS:
Patient is stable and responding well to treatment.
Scheduled for follow-up in 2 weeks.

ATTENDING PHYSICIAN: Dr. Emily Carter, MD
CARDIOLOGIST: Department of Cardiology

CONFIDENTIALITY NOTICE:
This document contains sensitive medical information protected by HIPAA.
Unauthorized access or disclosure is strictly prohibited.
        """)
    print(f"✓ Created: {cardiology_file}")
    
    # Lab report file
    lab_file = "demo_lab_report.txt"
    with open(lab_file, 'w') as f:
        f.write("""
LABORATORY TEST REPORT
======================
Patient ID: P20240001
Patient Name: John Doe
Test Date: 2024-01-21
Report Date: 2024-01-22

CARDIAC BIOMARKERS:
- Troponin I: 2.8 ng/mL (Elevated - indicates myocardial damage)
- CK-MB: 15.2 ng/mL (Elevated)
- BNP: 450 pg/mL (Elevated - heart failure marker)

LIPID PANEL:
- Total Cholesterol: 240 mg/dL (High)
- LDL Cholesterol: 160 mg/dL (High)
- HDL Cholesterol: 38 mg/dL (Low)
- Triglycerides: 210 mg/dL (High)

COMPLETE BLOOD COUNT:
- WBC: 8.5 K/µL (Normal)
- RBC: 4.8 M/µL (Normal)
- Hemoglobin: 14.2 g/dL (Normal)
- Platelets: 225 K/µL (Normal)

INTERPRETATION:
Results consistent with recent myocardial infarction.
Lipid levels require aggressive management.

PROCESSED BY: Sarah Lee, Lab Technician
DEPARTMENT: Clinical PathologyLABORATORY: City General Hospital
        """)
    print(f"✓ Created: {lab_file}")
    
    # ========== STEP 6: ENCRYPT FILES ==========
    print_section("STEP 6: Encrypting Patient Files with CP-ABE")
    
    print("Encrypting cardiology record with policy...")
    print(f"Policy: {cardiology_policy.policy_expression}")
    encrypted_cardio = encryption_service.encrypt_file(
        input_file_path=cardiology_file,
        patient_id="P20240001",
        policy_expression=cardiology_policy.policy_expression,
        encrypted_by=admin_wang.user_id,
        file_type="medical_record",
        department="Cardiology",
        policy_id=cardiology_policy.policy_id,
        metadata={'importance': 'high', 'diagnosis': 'myocardial_infarction'}
    )
    print(f"✓ File encrypted: {encrypted_cardio.file_id}")
    print(f"  Original size: {encrypted_cardio.original_size} bytes")
    print(f"  Encrypted size: {encrypted_cardio.encrypted_size} bytes")
    print(f"  Integrity hash: {encrypted_cardio.integrity_hash[:32]}...")
    
    print(f"\nEncrypting lab report with policy...")
    print(f"Policy: {lab_policy.policy_expression}")
    encrypted_lab = encryption_service.encrypt_file(
        input_file_path=lab_file,
        patient_id="P20240001",
        policy_expression=lab_policy.policy_expression,
        encrypted_by=admin_wang.user_id,
        file_type="lab_report",
        department="Pathology",
        policy_id=lab_policy.policy_id,
        metadata={'test_type': 'cardiac_biomarkers'}
    )
    print(f"✓ File encrypted: {encrypted_lab.file_id}")
    print(f"  Original size: {encrypted_lab.original_size} bytes")
    print(f"  Encrypted size: {encrypted_lab.encrypted_size} bytes")
    
    # ========== STEP 7: ACCESS CONTROL TESTING ==========
    print_section("STEP 7: Testing Access Control")
    
    print("Testing who can access cardiology record...")
    print(f"Policy: {cardiology_policy.policy_expression}\n")
    
    # Test Dr. Carter (should succeed)
    can_access, reason = decryption_service.check_access(encrypted_cardio.file_id, dr_carter)
    print(f"Dr. Carter ({', '.join(dr_carter.attributes[:3])})")
    print(f"  Result: {'✓ ACCESS GRANTED' if can_access else '✗ ACCESS DENIED'}")
    print(f"  Reason: {reason}")
    
    # Test Nurse Brown (should fail)
    can_access, reason = decryption_service.check_access(encrypted_cardio.file_id, nurse_brown)
    print(f"\nNurse Brown ({', '.join(nurse_brown.attributes[:3])})")
    print(f"  Result: {'✓ ACCESS GRANTED' if can_access else '✗ ACCESS DENIED'}")
    print(f"  Reason: {reason}")
    
    # Test Lab Tech (should fail)
    can_access, reason = decryption_service.check_access(encrypted_cardio.file_id, lab_lee)
    print(f"\nLab Tech Lee ({', '.join(lab_lee.attributes[:3])})")
    print(f"  Result: {'✓ ACCESS GRANTED' if can_access else '✗ ACCESS DENIED'}")
    print(f"  Reason: {reason}")
    
    # Test Admin (should fail - not in cardiology)
    can_access, reason = decryption_service.check_access(encrypted_cardio.file_id, admin_wang)
    print(f"\nAdmin Wang ({', '.join(admin_wang.attributes[:3])})")
    print(f"  Result: {'✓ ACCESS GRANTED' if can_access else '✗ ACCESS DENIED'}")
    print(f"  Reason: {reason}")
    
    print("\n" + "-"*60)
    print("Testing who can access lab report...")
    print(f"Policy: {lab_policy.policy_expression}\n")
    
    # Test all users for lab report
    users = [
        (dr_carter, dr_carter_key),
        (nurse_brown, nurse_brown_key),
        (lab_lee, lab_lee_key),
        (admin_wang, admin_wang_key)
    ]
    
    for user, _ in users:
        can_access, reason = decryption_service.check_access(encrypted_lab.file_id, user)
        status = "✓ ACCESS GRANTED" if can_access else "✗ ACCESS DENIED"
        print(f"{user.full_name}: {status}")
    
    # ========== STEP 8: ACTUAL DECRYPTION ==========
    print_section("STEP 8: Decrypting Files")
    
    # Dr. Carter decrypts cardiology record
    print("Dr. Carter attempting to decrypt cardiology record...")
    success, error = decryption_service.decrypt_file(
        encrypted_cardio.file_id,
        dr_carter,
        dr_carter_key,
        "decrypted_cardiology.txt"
    )
    
    if success:
        print("✓ Decryption successful!")
        print("\nFirst 200 characters of decrypted file:")
        with open("decrypted_cardiology.txt", 'r') as f:
            content = f.read()
            print(f"  {content[:200]}...")
    else:
        print(f"✗ Decryption failed: {error}")
    
    # Nurse Brown attempts to decrypt cardiology record (should fail)
    print("\n" + "-"*60)
    print("Nurse Brown attempting to decrypt cardiology record...")
    success, error = decryption_service.decrypt_file(
        encrypted_cardio.file_id,
        nurse_brown,
        nurse_brown_key,
        "nurse_attempt.txt"
    )
    
    if success:
        print("✗ Unexpected success - security breach!")
    else:
        print(f"✓ Correctly denied: {error}")
    
    # Lab Tech decrypts lab report (should succeed)
    print("\n" + "-"*60)
    print("Lab Tech Lee attempting to decrypt lab report...")
    success, error = decryption_service.decrypt_file(
        encrypted_lab.file_id,
        lab_lee,
        lab_lee_key,
        "decrypted_lab_report.txt"
    )
    
    if success:
        print("✓ Decryption successful!")
        print("\nFirst 200 characters of decrypted file:")
        with open("decrypted_lab_report.txt", 'r') as f:
            content = f.read()
            print(f"  {content[:200]}...")
    else:
        print(f"✗ Decryption failed: {error}")
    
    # ========== STEP 9: AUDIT LOG ==========
    print_section("STEP 9: Audit Log Review")
    
    print("Access attempts logged:\n")
    audit_log_path = "demo_storage/audit_logs/access_log.txt"
    if os.path.exists(audit_log_path):
        with open(audit_log_path, 'r') as f:
            for line in f:
                print(f"  {line.rstrip()}")
    else:
        print("  No audit log found")
    
    # ========== STEP 10: STATISTICS ==========
    print_section("STEP 10: System Statistics")
    
    print(f"Total Users: {len(user_manager.list_users())}")
    print(f"Total Policies: {len(policy_engine.list_policies())}")
    print(f"Total Encrypted Files: {len(encryption_service.list_encrypted_files())}")
    
    print("\nEncrypted Files:")
    for ef in encryption_service.list_encrypted_files():
        print(f"  - {ef.file_id}: {ef.original_filename}")
        print(f"    Patient: {ef.patient_id}")
        print(f"    Policy: {ef.policy_expression}")
        print(f"    Accesses: {ef.access_count}")
    
    # ========== CLEANUP ==========
    print_section("Demo Complete!")
    
    print("To clean up demo files, delete the following:")
    print("  - demo_storage/")
    print("  - demo_cardiology_record.txt")
    print("  - demo_lab_report.txt")
    print("  - decrypted_*.txt")
    
    print("\n" + "="*60)
    print("  SYSTEM SUCCESSFULLY DEMONSTRATED")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
