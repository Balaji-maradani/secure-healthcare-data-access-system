"""
FastAPI Backend for Healthcare Data Security System
Provides REST API for file encryption, decryption, and management
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import secrets
import hashlib
import json
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Data Security System",
    description="Secure file encryption with AES-256 and access control",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage directories
STORAGE_DIR = "app_storage"
ENCRYPTED_DIR = os.path.join(STORAGE_DIR, "encrypted")
KEYS_DIR = os.path.join(STORAGE_DIR, "keys")
METADATA_DIR = os.path.join(STORAGE_DIR, "metadata")
USERS_FILE = os.path.join(STORAGE_DIR, "users.json")
AUDIT_LOG = os.path.join(STORAGE_DIR, "audit_log.txt")

# Create directories
for directory in [STORAGE_DIR, ENCRYPTED_DIR, KEYS_DIR, METADATA_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize users file
if not os.path.exists(USERS_FILE):
    default_users = {
        "dr.carter": {
            "name": "Dr. Emily Carter",
            "role": "Doctor",
            "department": "Cardiology",
            "clearance": "L3",
            "attributes": ["Doctor", "Cardiology", "ClearanceLevel:L3"],
            "password": "doctor123"
        },
        "nurse.brown": {
            "name": "Nurse Michael Brown",
            "role": "Nurse",
            "department": "Emergency",
            "clearance": "L2",
            "attributes": ["Nurse", "Emergency", "ClearanceLevel:L2"],
            "password": "nurse123"
        },
        "admin": {
            "name": "Admin User",
            "role": "Admin",
            "department": "IT",
            "clearance": "L3",
            "attributes": ["Admin", "IT", "ClearanceLevel:L3"],
            "password": "admin123"
        }
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(default_users, f, indent=2)

# Pydantic models
class User(BaseModel):
    username: str
    password: str

class FileMetadata(BaseModel):
    file_id: str
    original_filename: str
    patient_id: str
    policy: str
    department: str
    encrypted_at: str
    encrypted_by: str
    file_size: int

# Helper functions
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def log_audit(entry: str):
    with open(AUDIT_LOG, 'a') as f:
        timestamp = datetime.now().isoformat()
        f.write(f"[{timestamp}] {entry}\n")

def check_policy(user_attrs: List[str], policy: str) -> bool:
    """Simple policy checker for 'X AND Y' format"""
    policy = policy.replace("(", "").replace(")", "")
    
    if " OR " in policy:
        conditions = policy.split(" OR ")
        for condition in conditions:
            if check_policy(user_attrs, condition.strip()):
                return True
        return False
    
    if " AND " in policy:
        required = [attr.strip() for attr in policy.split(" AND ")]
        return all(attr in user_attrs for attr in required)
    
    return policy.strip() in user_attrs

def encrypt_file_content(content: bytes) -> tuple:
    """Encrypt file content with AES-256"""
    key = secrets.token_bytes(32)
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(content, AES.block_size))
    return encrypted, key, iv

def decrypt_file_content(encrypted: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypt file content"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    return decrypted

def compute_hash(data: bytes) -> str:
    """Compute SHA-3 hash"""
    return hashlib.sha3_256(data).hexdigest()

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "Healthcare Data Security System API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/api/login")
async def login(user: User):
    """User login"""
    users = load_users()
    
    if user.username not in users:
        log_audit(f"Failed login attempt: {user.username} (user not found)")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if users[user.username]["password"] != user.password:
        log_audit(f"Failed login attempt: {user.username} (wrong password)")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    log_audit(f"Successful login: {user.username}")
    
    return {
        "success": True,
        "user": {
            "username": user.username,
            "name": users[user.username]["name"],
            "role": users[user.username]["role"],
            "department": users[user.username]["department"],
            "attributes": users[user.username]["attributes"]
        }
    }

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    policy: str = Form(...),
    department: str = Form(...),
    username: str = Form(...)
):
    """Upload and encrypt a file"""
    
    # Read file content
    content = await file.read()
    
    # Generate file ID
    file_id = secrets.token_hex(16)
    
    # Encrypt file
    encrypted_content, key, iv = encrypt_file_content(content)
    
    # Compute integrity hash
    file_hash = compute_hash(encrypted_content)
    
    # Save encrypted file
    encrypted_path = os.path.join(ENCRYPTED_DIR, f"{file_id}.enc")
    with open(encrypted_path, 'wb') as f:
        f.write(encrypted_content)
    
    # Save encryption key
    key_path = os.path.join(KEYS_DIR, f"{file_id}.key")
    with open(key_path, 'wb') as f:
        f.write(key)
    
    # Save metadata
    metadata = {
        "file_id": file_id,
        "original_filename": file.filename,
        "patient_id": patient_id,
        "policy": policy,
        "department": department,
        "encrypted_by": username,
        "encrypted_at": datetime.now().isoformat(),
        "file_size_original": len(content),
        "file_size_encrypted": len(encrypted_content),
        "iv": iv.hex(),
        "integrity_hash": file_hash,
        "encryption_algorithm": "AES-256-CBC",
        "hash_algorithm": "SHA3-256"
    }
    
    metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    log_audit(f"File encrypted: {file.filename} (ID: {file_id}) by {username}")
    
    return {
        "success": True,
        "file_id": file_id,
        "message": f"File '{file.filename}' encrypted successfully",
        "metadata": metadata
    }

@app.get("/api/files")
async def list_files(username: str):
    """List all encrypted files"""
    users = load_users()
    
    if username not in users:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_attrs = users[username]["attributes"]
    files = []
    
    # Read all metadata files
    for filename in os.listdir(METADATA_DIR):
        if filename.endswith('.json'):
            metadata_path = os.path.join(METADATA_DIR, filename)
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Check if user can access this file
            can_access = check_policy(user_attrs, metadata["policy"])
            
            files.append({
                **metadata,
                "can_access": can_access
            })
    
    # Sort by encrypted_at (newest first)
    files.sort(key=lambda x: x["encrypted_at"], reverse=True)
    
    return {"files": files}

@app.get("/api/decrypt/{file_id}")
async def decrypt_file(file_id: str, username: str):
    """Decrypt and download a file"""
    users = load_users()
    
    if username not in users:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_attrs = users[username]["attributes"]
    user_name = users[username]["name"]
    
    # Load metadata
    metadata_path = os.path.join(METADATA_DIR, f"{file_id}.json")
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    # Check access policy
    can_access = check_policy(user_attrs, metadata["policy"])
    
    if not can_access:
        log_audit(f"Access DENIED: {username} ({user_name}) tried to access {file_id} - Policy: {metadata['policy']}")
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Your attributes {user_attrs} don't match policy: {metadata['policy']}"
        )
    
    # Load encrypted file
    encrypted_path = os.path.join(ENCRYPTED_DIR, f"{file_id}.enc")
    with open(encrypted_path, 'rb') as f:
        encrypted_content = f.read()
    
    # Verify integrity
    current_hash = compute_hash(encrypted_content)
    if current_hash != metadata["integrity_hash"]:
        log_audit(f"INTEGRITY FAILURE: {file_id} - Hash mismatch!")
        raise HTTPException(status_code=500, detail="File integrity check failed - possible tampering")
    
    # Load decryption key
    key_path = os.path.join(KEYS_DIR, f"{file_id}.key")
    with open(key_path, 'rb') as f:
        key = f.read()
    
    # Decrypt
    iv = bytes.fromhex(metadata["iv"])
    decrypted_content = decrypt_file_content(encrypted_content, key, iv)
    
    # Save temporarily
    temp_path = os.path.join(STORAGE_DIR, f"temp_{file_id}_{metadata['original_filename']}")
    with open(temp_path, 'wb') as f:
        f.write(decrypted_content)
    
    log_audit(f"Access GRANTED: {username} ({user_name}) decrypted {metadata['original_filename']} (ID: {file_id})")
    
    return FileResponse(
        temp_path,
        filename=metadata['original_filename'],
        media_type='application/octet-stream'
    )

@app.get("/api/users")
async def list_users():
    """List all users"""
    users = load_users()
    return {
        "users": [
            {
                "username": username,
                "name": info["name"],
                "role": info["role"],
                "department": info["department"],
                "clearance": info["clearance"],
                "attributes": info["attributes"]
            }
            for username, info in users.items()
        ]
    }

@app.get("/api/audit")
async def get_audit_log(limit: int = 50):
    """Get recent audit log entries"""
    if not os.path.exists(AUDIT_LOG):
        return {"entries": []}
    
    with open(AUDIT_LOG, 'r') as f:
        lines = f.readlines()
    
    # Return last N entries
    return {"entries": lines[-limit:]}

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    users = load_users()
    
    metadata_files = [f for f in os.listdir(METADATA_DIR) if f.endswith('.json')]
    
    total_size = 0
    for filename in metadata_files:
        metadata_path = os.path.join(METADATA_DIR, filename)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            total_size += metadata.get('file_size_original', 0)
    
    return {
        "total_users": len(users),
        "total_files": len(metadata_files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "encryption_algorithm": "AES-256-CBC",
        "hash_algorithm": "SHA3-256"
    }

# Mount static files (for frontend)
app.mount("/static", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.environ.get("PORT", 8000))
    
    print("=" * 70)
    print("  HEALTHCARE DATA SECURITY SYSTEM - WEB APPLICATION")
    print("=" * 70)
    print()
    print("🚀 Starting server...")
    print("📂 Storage directory:", STORAGE_DIR)
    print("🔐 Default users:")
    print("   • Username: admin, Password: admin123 (Admin)")
    print("   • Username: dr.carter, Password: doctor123 (Doctor - Cardiology)")
    print("   • Username: nurse.brown, Password: nurse123 (Nurse - Emergency)")
    print()
    print(f"✅ Server running on port: {port}")
    print()
    print("🌐 OPEN THIS URL IN YOUR BROWSER:")
    print(f"   👉 http://localhost:{port}/static/index.html")
    print()
    print("   Or use: http://127.0.0.1:{}/static/index.html".format(port))
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)
