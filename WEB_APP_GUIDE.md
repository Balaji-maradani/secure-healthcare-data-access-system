# Healthcare Data Security System - Web Application

## 🚀 Quick Start

### 1. Install Required Package

```bash
pip install fastapi uvicorn python-multipart
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open Your Browser

Go to: **http://localhost:8000/static/index.html**

---

## 🔐 Default Login Credentials

| Username | Password | Role | Department |
|----------|----------|------|------------|
| `admin` | `admin123` | Admin | IT |
| `dr.carter` | `doctor123` | Doctor | Cardiology |
| `nurse.brown` | `nurse123` | Nurse | Emergency |

---

## ✨ Features

### 📤 File Upload & Encryption
- Drag & drop file upload
- AES-256 encryption
- SHA-3 integrity verification
- Policy-based access control
- Automatic metadata storage

### 📁 File Management
- View all encrypted files
- See which files you can access
- Download/decrypt authorized files
- Access denied for non-matching policies

### 🔒 Access Control
- Attribute-based policies (ABAC)
- Role-based access (Doctor, Nurse, Lab, Admin)
- Department-level restrictions
- Clearance levels (L1, L2, L3)

### 👥 User Management
- View all system users
- See user roles and attributes
- Understand access permissions

### 📊 System Statistics
- Total encrypted files
- Total data size
- Encryption algorithms
- Real-time updates

---

## 🎯 How to Use

### Uploading a File

1. **Login** with one of the demo accounts
2. Go to **"Upload File"** tab
3. **Drag & drop** a file or click "Choose File"
4. Fill in:
   - **Patient ID** (e.g., P12345)
   - **Department** (select from dropdown)
   - **Access Policy** (who can access this file)
5. Click **"Encrypt & Upload"**

### Example Policies

- `Doctor AND Cardiology` - Only cardiologists
- `Doctor AND Emergency` - Emergency doctors only
- `Nurse AND Emergency` - Emergency nurses
- `Lab` - Lab technicians
- `Admin` - Administrators only
- `Doctor OR Nurse` - Any medical staff
- `(Doctor OR Nurse) AND Emergency` - Emergency medical staff

### Viewing Files

1. Go to **"My Files"** tab
2. See all encrypted files in the system
3. **Green badge (✓ Granted)** = You can access
4. **Red badge (✗ Denied)** = Access denied
5. Click **"Decrypt"** to download and decrypt

### Testing Access Control

**Scenario 1:** Upload as Admin with policy "Doctor AND Cardiology"
- Login as `dr.carter` → Can decrypt ✓
- Login as `nurse.brown` → Cannot decrypt ✗

**Scenario 2:** Upload as Admin with policy "Nurse AND Emergency"
- Login as `nurse.brown` → Can decrypt ✓
- Login as `dr.carter` → Cannot decrypt ✗

---

## 📁 Project Structure

```
cys/
├── app.py                    # FastAPI backend server
├── web/
│   └── index.html           # Web frontend interface
├── app_storage/             # Created when app runs
│   ├── encrypted/           # Encrypted files
│   ├── keys/                # AES encryption keys
│   ├── metadata/            # File metadata
│   ├── users.json           # User database
│   └── audit_log.txt        # Access audit log
```

---

## 🔧 API Endpoints

### Authentication
- `POST /api/login` - User login

### File Operations
- `POST /api/upload` - Upload and encrypt file
- `GET /api/files?username={user}` - List all files
- `GET /api/decrypt/{file_id}?username={user}` - Decrypt and download

### System
- `GET /api/users` - List all users
- `GET /api/stats` - System statistics
- `GET /api/audit` - Audit log

---

## 📊 Security Features Implemented

| Feature | Status | Implementation |
|---------|--------|----------------|
| **AES-256 Encryption** | ✅ | Symmetric file encryption |
| **SHA-3 Hashing** | ✅ | File integrity verification |
| **Access Control** | ✅ | Attribute-based policies |
| **Audit Logging** | ✅ | All access attempts logged |
| **Secure Storage** | ✅ | Encrypted files + keys separated |
| **Policy Enforcement** | ✅ | Application-layer checks |
| **Metadata Storage** | ✅ | JSON-based file metadata |

---

## 🧪 Testing Scenarios

### Test 1: Basic Upload and Download

1. Login as `admin`
2. Upload a text file with policy "Admin"
3. Logout and login as `dr.carter`
4. Try to download → Should be **DENIED** ✗
5. Logout and login as `admin`
6. Download → Should **SUCCEED** ✓

### Test 2: Department-Based Access

1. Login as `admin`
2. Upload file with policy "Doctor AND Cardiology"
3. Logout and login as `dr.carter` (Doctor, Cardiology)
4. Download → Should **SUCCEED** ✓
5. Logout and login as `nurse.brown` (Nurse, Emergency)
6. Try to download → Should be **DENIED** ✗

### Test 3: Complex Policies

1. Login as `admin`
2. Upload with policy "(Doctor OR Nurse) AND Emergency"
3. Test with different users:
   - `nurse.brown` (Nurse + Emergency) → ✓ GRANTED
   - `dr.carter` (Doctor + Cardiology) → ✗ DENIED
   - Emergency doctor → ✓ GRANTED

---

## 📝 Audit Trail

All access attempts are logged in `app_storage/audit_log.txt`:

```
[2024-01-20T10:30:45] File encrypted: patient_record.pdf (ID: abc123) by admin
[2024-01-20T10:31:12] Access GRANTED: dr.carter (Dr. Emily Carter) decrypted patient_record.pdf
[2024-01-20T10:32:05] Access DENIED: nurse.brown tried to access abc123 - Policy: Doctor AND Cardiology
```

---

## 🎨 Web Interface Features

- ✅ Modern, responsive design
- ✅ Drag & drop file upload
- ✅ Real-time statistics
- ✅ Color-coded access badges
- ✅ Tabbed navigation
- ✅ Alert notifications
- ✅ Mobile-friendly
- ✅ Beautiful gradients and animations

---

## 🚀 Production Deployment

For production use:

1. **Change default passwords** in `app_storage/users.json`
2. **Use HTTPS** (TLS/SSL) for all connections
3. **Add authentication tokens** (JWT)
4. **Use PostgreSQL** instead of JSON files
5. **Deploy on Linux server** for better security
6. **Add rate limiting** to prevent abuse
7. **Enable CORS** only for trusted domains
8. **Regular backups** of encrypted files and keys

---

## 💡 Tips

- **Encryption is automatic** - Just upload and it's encrypted
- **Policies are flexible** - Use AND/OR for complex rules
- **Access is logged** - Every attempt is recorded
- **Files are safe** - AES-256 + SHA-3 protection
- **No CP-ABE needed** - Works perfectly without charm-crypto!

---

## ✅ System Status

**Backend:** ✅ FastAPI running on http://localhost:8000  
**Frontend:** ✅ Web interface at http://localhost:8000/static/index.html  
**Storage:** ✅ app_storage/ directory  
**Security:** ✅ AES-256 + SHA-3  
**Access Control:** ✅ Policy-based ABAC  

---

**Enjoy your secure healthcare data system!** 🎉
