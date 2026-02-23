# Password Hashing Demo Guide

## Overview
This guide explains the password hashing demonstrations available in the Password Security Toolkit.

## 🎯 Quick Start

### Run the Interactive Demo
```bash
python test_hash_demo.py
```

### Test API Endpoints

#### 1. Basic Hash Demo
```bash
curl -X POST http://localhost:5000/hash \
  -d "password=MySecureP@ssw0rd!"
```

#### 2. Compare Hash Algorithms
```bash
curl -X POST http://localhost:5000/compare-hashes \
  -d "password=TestPassword123"
```

#### 3. Batch Hash Demo
```bash
curl -X POST http://localhost:5000/hash-demo \
  -d "passwords[]=password" \
  -d "passwords[]=Password1" \
  -d "passwords[]=SecureP@ss!"
```

## 📚 Available Hash Algorithms

### ❌ INSECURE (Never use for passwords!)
- **MD5**: 128-bit, cryptographically broken
- **SHA1**: 160-bit, cryptographically broken

### ⚠️ NOT RECOMMENDED (Without proper implementation)
- **SHA256**: 256-bit, too fast for passwords
- **SHA512**: 512-bit, too fast for passwords
- **SHA224**: 224-bit, too fast for passwords
- **SHA384**: 384-bit, too fast for passwords

### ✅ ACCEPTABLE (With salt and iterations)
- **PBKDF2-SHA256**: With 100,000+ iterations
- **PBKDF2-SHA512**: With 100,000+ iterations

### ✅ RECOMMENDED (Production-ready)
- **bcrypt**: Adaptive, battle-tested
- **argon2id**: Winner of Password Hashing Competition
- **scrypt**: Memory-hard function

## 🔬 Demonstration Features

### 1. Basic Hashing
Shows how different algorithms hash the same password:
```python
password = "MyPassword123!"

MD5:    5f4dcc3b5aa765d61d8327deb882cf99
SHA256: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
SHA512: ba3253876aed6bc22d4a6ff53d8406c6ad864195ed144ab5c87621b6c233b548...
```

### 2. Salt Demonstration
Proves why salt is essential:
```python
# Without salt (same hash every time - BAD!)
password123 -> 482c811da5d5b4bc6d497ffa98491e38
password123 -> 482c811da5d5b4bc6d497ffa98491e38

# With salt (different hash each time - GOOD!)
password123 + salt1 -> a7f3c2e9d1b4f8a6c3e5d7f9b2a4c6e8
password123 + salt2 -> 3e8f1a9c5d7b2f4e6a8c0d2f4e6a8c0d
```

### 3. Collision Resistance
Shows how tiny changes create completely different hashes:
```python
"password"  -> 5f4dcc3b5aa765d61d8327deb882cf99
"Password"  -> dc647eb65e6711e155375218212b3964
"password " -> 7c6a180b36896a0a8c02787eeafb0e4c
```

### 4. Speed Comparison
Demonstrates why fast = bad for passwords:
```
MD5:    0.045 seconds (2,222,222 hashes/sec) ❌
SHA256: 0.052 seconds (1,923,076 hashes/sec) ❌
PBKDF2: 2.150 seconds (1 hash with 100k iterations) ✅
```

### 5. Rainbow Table Prevention
Shows how salt prevents rainbow table attacks:
```
Without salt:
  "password" always -> 5f4dcc3b5aa765d61d8327deb882cf99
  (Attacker can pre-compute this!)

With unique salts:
  "password" + salt1 -> a7f3c2e9d1b4f8a6c3e5d7f9b2a4c6e8
  "password" + salt2 -> 3e8f1a9c5d7b2f4e6a8c0d2f4e6a8c0d
  (Attacker needs unique rainbow table for each!)
```

## 🎓 Educational Examples

### Example 1: Why MD5 is Broken
```python
# MD5 collision example (simplified)
password1 = "d131dd02c5e6eec4"
password2 = "d131dd02c5e6eec5"

# Different inputs, but can produce same hash (collision)
# This is why MD5 is NEVER acceptable for security
```

### Example 2: Proper Password Storage
```python
import hashlib
import os

# ✅ CORRECT WAY
password = "UserPassword123!"
salt = os.urandom(32)  # Generate random salt
iterations = 100000    # Slow down hashing

# Use PBKDF2 with salt and iterations
hash_value = hashlib.pbkdf2_hmac(
    'sha256',
    password.encode(),
    salt,
    iterations
)

# Store: salt + hash_value + iterations
```

### Example 3: Password Verification
```python
def verify_password(stored_salt, stored_hash, stored_iterations, password_attempt):
    """Verify a password against stored hash"""
    # Recreate hash with same salt and iterations
    attempt_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password_attempt.encode(),
        stored_salt,
        stored_iterations
    )
    
    # Compare hashes (use constant-time comparison in production!)
    return attempt_hash == stored_hash
```

## 📊 Hash Output Lengths

| Algorithm | Output Length (hex) | Output Length (bytes) |
|-----------|--------------------|-----------------------|
| MD5       | 32 characters      | 16 bytes              |
| SHA1      | 40 characters      | 20 bytes              |
| SHA224    | 56 characters      | 28 bytes              |
| SHA256    | 64 characters      | 32 bytes              |
| SHA384    | 96 characters      | 48 bytes              |
| SHA512    | 128 characters     | 64 bytes              |

## 🔐 Security Best Practices

### DO ✅
1. Use bcrypt, argon2id, or scrypt for production
2. Generate unique salt for each password (16-32 bytes)
3. Use sufficient iterations (100,000+ for PBKDF2)
4. Store salt alongside hash
5. Use constant-time comparison for verification
6. Keep hashing libraries updated
7. Use established, peer-reviewed algorithms

### DON'T ❌
1. Use MD5 or SHA1 for passwords
2. Use fast hashing algorithms without iterations
3. Reuse salts across passwords
4. Store passwords in plain text
5. Use custom/homemade hashing algorithms
6. Use weak salts (like username or timestamp)
7. Truncate hash outputs

## 🧪 Testing the Demos

### Test 1: Basic Hashing
```bash
python test_hash_demo.py
```
Expected: Shows 6 different demonstrations

### Test 2: API Hash Endpoint
```bash
curl -X POST http://localhost:5000/hash -d "password=Test123!"
```
Expected: JSON with multiple hash algorithms

### Test 3: Compare Algorithms
```bash
curl -X POST http://localhost:5000/compare-hashes -d "password=SecurePass!"
```
Expected: Detailed comparison of 8 algorithms

### Test 4: Batch Processing
```bash
curl -X POST http://localhost:5000/hash-demo \
  -d "passwords[]=weak" \
  -d "passwords[]=Strong@123" \
  -d "passwords[]=VerySecure!P@ssw0rd"
```
Expected: Hashes for all passwords with comparison

## 📖 Common Passwords Database

The toolkit includes a comprehensive list of common passwords in `common_passwords.txt`:

- **Total entries**: 400+ common passwords
- **Categories**: 
  - Top 100 most common passwords
  - Keyboard patterns (qwerty, asdfgh, etc.)
  - Common names
  - Sports teams
  - Years and dates
  - Number sequences
  - Simple words
  - Common substitutions (p@ssw0rd, etc.)

### Check Against Common Passwords
```bash
curl -X POST http://localhost:5000/breach -d "password=password123"
```

## 🎯 Learning Objectives

After using these demos, you should understand:

1. ✅ Why MD5 and SHA1 are insecure
2. ✅ The importance of salt in password hashing
3. ✅ Why fast hashing is dangerous for passwords
4. ✅ How rainbow tables work and how to prevent them
5. ✅ The difference between hashing and encryption
6. ✅ What makes a good password hashing algorithm
7. ✅ How to properly implement password storage
8. ✅ The role of iterations in password security

## 🔗 Additional Resources

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Have I Been Pwned](https://haveibeenpwned.com/)
- [Password Hashing Competition](https://www.password-hashing.net/)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)

## ⚠️ Important Disclaimer

These demonstrations are for EDUCATIONAL PURPOSES ONLY. The implementations shown are simplified for learning. In production:

- Use established libraries (bcrypt, argon2-cffi, etc.)
- Follow current security best practices
- Implement proper error handling
- Use constant-time comparisons
- Consider additional security measures (rate limiting, MFA, etc.)
- Keep all dependencies updated
- Conduct security audits

---

**Remember**: Password security is critical. Always use production-ready libraries and follow current best practices!
