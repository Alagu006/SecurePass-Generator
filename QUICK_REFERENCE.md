# 🚀 Quick Reference Card

## One-Page Guide to Password Security Toolkit

### 📦 Installation (3 Steps)
```bash
# 1. Setup
python setup.py

# 2. Install
pip install -r requirements.txt

# 3. Run
python app.py
```

### 🔑 Default Credentials
```
Username: admin
Password: Admin@123
URL: http://localhost:6001
```

### 🔒 Security Features
- ✅ Bcrypt password hashing
- ✅ Cryptographic random generation (`secrets`)
- ✅ Rate limiting (5-30 req/min)
- ✅ CSRF protection
- ✅ Security headers (CSP, XSS, etc.)
- ✅ Account lockout (5 failed attempts)
- ✅ Input validation (8-64 chars)

### 📡 API Endpoints
```bash
# Check password strength
curl -X POST http://localhost:6001/check -d "password=Test123!"

# Generate password
curl http://localhost:6001/generate?length=16

# Check breach
curl -X POST http://localhost:6001/breach -d "password=password123"
```

### 🛠️ Configuration
```env
# .env file
SECRET_KEY=<generate-with-secrets.token_hex(32)>
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=password_security_db
DB_PORT=5555
```

### 📁 Key Files
- `app.py` - Main application
- `auth.py` - Authentication
- `models.py` - Database models
- `config.py` - Configuration
- `requirements.txt` - Dependencies
- `.env` - Environment variables (create from .env.example)

### 🔧 Common Commands
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Setup database
python init_postgres.py

# View users
python view_users.py

# Run application
python app.py
```

### 📊 Database Tables
- `user` - User accounts
- `password_history` - Password checks
- `login_attempt` - Login tracking
- `system_settings` - App settings
- `user_activity` - User actions

### 🎯 Rate Limits
- Login: 5/min
- Check: 30/min
- Generate: 20/min
- Hash: 20/min
- Breach: 10/min

### 🔐 Password Requirements
- Length: 8-64 characters
- Must have: uppercase, lowercase, digit, special char
- Not in common passwords list (400+)

### 📚 Documentation
- `README.md` - Full documentation
- `SECURITY.md` - Security policy
- `CONTRIBUTING.md` - How to contribute
- `GITHUB_READY.md` - GitHub checklist
- `FINAL_SUMMARY.md` - Complete summary

### 🐛 Troubleshooting
```bash
# Port already in use
# Change port in app.py (line ~907): app.run(port=6001)

# Database connection error
# Check PostgreSQL is running: pg_ctl status

# Missing dependencies
pip install -r requirements.txt

# Permission denied
# Run as admin or check file permissions
```

### 🚀 GitHub Push
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

### ✅ Pre-Push Checklist
- [ ] .env in .gitignore
- [ ] No hardcoded secrets
- [ ] requirements.txt updated
- [ ] README.md complete
- [ ] Tests pass
- [ ] Documentation updated

### 🎓 Learning Resources
- Flask: https://flask.palletsprojects.com/
- OWASP: https://owasp.org/
- Python Security: https://docs.python.org/3/library/secrets.html
- Bcrypt: https://pypi.org/project/bcrypt/

### 📞 Quick Help
- Check README.md first
- Review SECURITY.md for security questions
- See CONTRIBUTING.md for development
- Open issue on GitHub for bugs

---

**Status**: ✅ Production-Ready | **Security**: 🔒 Enterprise-Grade | **Docs**: 📚 Complete
