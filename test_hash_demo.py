#!/usr/bin/env python3
"""
Hash Password Demo Script
Demonstrates various hashing algorithms and their properties
"""

import hashlib
import os
import time

def print_separator(char="=", length=70):
    """Print a separator line"""
    print(char * length)

def demo_basic_hashing():
    """Demonstrate basic hashing algorithms"""
    print("\n🔐 DEMO 1: Basic Hashing Algorithms")
    print_separator()
    
    passwords = [
        "password",
        "Password",
        "password1",
        "MySecureP@ssw0rd!",
        "123456"
    ]
    
    print("\nNotice how similar passwords produce completely different hashes:\n")
    
    for pwd in passwords:
        print(f"Password: '{pwd}'")
        print(f"  MD5:    {hashlib.md5(pwd.encode()).hexdigest()}")
        print(f"  SHA256: {hashlib.sha256(pwd.encode()).hexdigest()}")
        print()

def demo_salt():
    """Demonstrate the importance of salt"""
    print("\n🧂 DEMO 2: Why Salt Matters")
    print_separator()
    
    password = "password123"
    
    print(f"\nSame password: '{password}'")
    print("\nWithout salt (same hash every time - BAD!):")
    print(f"  Hash 1: {hashlib.sha256(password.encode()).hexdigest()}")
    print(f"  Hash 2: {hashlib.sha256(password.encode()).hexdigest()}")
    print(f"  Hash 3: {hashlib.sha256(password.encode()).hexdigest()}")
    
    print("\nWith different salts (different hash each time - GOOD!):")
    for i in range(3):
        salt = os.urandom(16).hex()
        salted = hashlib.sha256((password + salt).encode()).hexdigest()
        print(f"  Salt {i+1}: {salt}")
        print(f"  Hash {i+1}: {salted}")
        print()

def demo_collision_resistance():
    """Demonstrate hash collision resistance"""
    print("\n💥 DEMO 3: Collision Resistance")
    print_separator()
    
    print("\nEven tiny changes create completely different hashes:\n")
    
    base_password = "SecurePassword123!"
    variations = [
        base_password,
        base_password + " ",  # Added space
        base_password + ".",  # Added period
        base_password.lower(),  # Lowercase
        base_password[:-1],  # Removed last char
    ]
    
    for pwd in variations:
        print(f"Password: '{pwd}'")
        print(f"SHA256:   {hashlib.sha256(pwd.encode()).hexdigest()}")
        print()

def demo_hash_speed():
    """Demonstrate why fast hashing is bad for passwords"""
    print("\n⚡ DEMO 4: Hash Speed (Why Fast = Bad for Passwords)")
    print_separator()
    
    password = "TestPassword123!"
    iterations = 100000
    
    print(f"\nHashing '{password}' {iterations:,} times:\n")
    
    # MD5 (fast - bad for passwords)
    start = time.time()
    for _ in range(iterations):
        hashlib.md5(password.encode()).hexdigest()
    md5_time = time.time() - start
    print(f"MD5:    {md5_time:.3f} seconds ({iterations/md5_time:,.0f} hashes/sec)")
    
    # SHA256 (fast - bad for passwords)
    start = time.time()
    for _ in range(iterations):
        hashlib.sha256(password.encode()).hexdigest()
    sha256_time = time.time() - start
    print(f"SHA256: {sha256_time:.3f} seconds ({iterations/sha256_time:,.0f} hashes/sec)")
    
    # PBKDF2 (slow - good for passwords)
    start = time.time()
    salt = os.urandom(16)
    hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    pbkdf2_time = time.time() - start
    print(f"PBKDF2: {pbkdf2_time:.3f} seconds (1 hash with {iterations:,} iterations)")
    
    print("\n⚠️  Fast hashing allows attackers to try billions of passwords per second!")
    print("✅  Slow hashing (PBKDF2, bcrypt, argon2) makes brute-force attacks impractical.")

def demo_rainbow_tables():
    """Demonstrate rainbow table vulnerability"""
    print("\n🌈 DEMO 5: Rainbow Table Attack Prevention")
    print_separator()
    
    common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
    
    print("\nWithout salt - vulnerable to rainbow tables:")
    print("(Attacker can pre-compute hashes for common passwords)\n")
    
    for pwd in common_passwords:
        hash_val = hashlib.sha256(pwd.encode()).hexdigest()
        print(f"'{pwd}' -> {hash_val}")
    
    print("\n\nWith unique salts - rainbow tables are useless:")
    print("(Each password needs a unique rainbow table)\n")
    
    for pwd in common_passwords:
        salt = os.urandom(16).hex()
        hash_val = hashlib.sha256((pwd + salt).encode()).hexdigest()
        print(f"'{pwd}' + salt({salt[:16]}...) -> {hash_val}")

def demo_algorithm_comparison():
    """Compare different hashing algorithms"""
    print("\n📊 DEMO 6: Algorithm Comparison")
    print_separator()
    
    password = "MyP@ssw0rd123!"
    salt = os.urandom(32)
    
    print(f"\nPassword: '{password}'")
    print(f"Salt: {salt.hex()}\n")
    
    algorithms = {
        'MD5': lambda: hashlib.md5(password.encode()).hexdigest(),
        'SHA1': lambda: hashlib.sha1(password.encode()).hexdigest(),
        'SHA224': lambda: hashlib.sha224(password.encode()).hexdigest(),
        'SHA256': lambda: hashlib.sha256(password.encode()).hexdigest(),
        'SHA384': lambda: hashlib.sha384(password.encode()).hexdigest(),
        'SHA512': lambda: hashlib.sha512(password.encode()).hexdigest(),
        'SHA256+Salt': lambda: hashlib.sha256((password + salt.hex()).encode()).hexdigest(),
        'PBKDF2-SHA256': lambda: hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex(),
    }
    
    security_status = {
        'MD5': '❌ BROKEN',
        'SHA1': '❌ BROKEN',
        'SHA224': '⚠️  Not recommended',
        'SHA256': '⚠️  Needs salt + iterations',
        'SHA384': '⚠️  Needs salt + iterations',
        'SHA512': '⚠️  Needs salt + iterations',
        'SHA256+Salt': '⚠️  Better, but needs iterations',
        'PBKDF2-SHA256': '✅ Good for passwords',
    }
    
    for name, func in algorithms.items():
        hash_val = func()
        status = security_status[name]
        print(f"{name:20} {status:30} {len(hash_val)} chars")
        print(f"  {hash_val[:80]}{'...' if len(hash_val) > 80 else ''}")
        print()

def main():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("🔐 PASSWORD HASHING DEMONSTRATION")
    print("Educational tool to understand password security")
    print("=" * 70)
    
    demo_basic_hashing()
    demo_salt()
    demo_collision_resistance()
    demo_hash_speed()
    demo_rainbow_tables()
    demo_algorithm_comparison()
    
    print("\n" + "=" * 70)
    print("📚 KEY TAKEAWAYS:")
    print("=" * 70)
    print("""
1. ❌ NEVER use MD5 or SHA1 for passwords (cryptographically broken)
2. ❌ NEVER store passwords in plain text
3. ❌ NEVER use fast hashing algorithms (SHA256, SHA512) alone
4. ✅ ALWAYS use a unique salt for each password
5. ✅ ALWAYS use slow hashing (bcrypt, argon2id, scrypt, or PBKDF2)
6. ✅ ALWAYS use sufficient iterations (100,000+ for PBKDF2)
7. ✅ Keep your hashing library updated
8. ✅ Use established libraries (don't roll your own crypto!)

🎯 PRODUCTION RECOMMENDATIONS:
   - First choice: Argon2id (winner of Password Hashing Competition)
   - Second choice: bcrypt (battle-tested, widely supported)
   - Third choice: scrypt (good memory-hard function)
   - Acceptable: PBKDF2-SHA256 with 100k+ iterations
""")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
