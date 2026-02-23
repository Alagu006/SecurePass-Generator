# 🔐 Password Security Toolkit

A comprehensive web-based password security application built with Flask and PostgreSQL. This project provides password strength analysis, secure password generation, hash demonstrations, and breach checking capabilities with enterprise-grade security features.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### Core Features
- **Password Strength Analyzer**: Real-time password strength analysis with detailed feedback
- **Secure Password Generator**: Generate cryptographically secure passwords using Python's `secrets` module
- **Hash Password Demo**: Educational demonstration of various hashing algorithms (MD5, SHA-1, SHA-256, SHA-512, PBKDF2)
- **Breach Checker**: Check passwords against 400+ common passwords database
- **User Dashboard**: Track password check history and statistics
- **Admin Panel**: Manage users and system settings

### Security Features
- ✅ **Cryptographically Secure Random Generation** (`secrets` module)
- ✅ **Bcrypt Password Hashing** (industry standard via Werkzeug)
- ✅ **CSRF Protection** (Flask-WTF)
- ✅ **Rate Limiting** (Flask-Limiter)
  - Login: 5 attempts per minute
  - Password check: 30 per minute
  - Password generation: 20 per minute
- ✅ **Security Headers**
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Content-Security-Policy
  - X-XSS-Protection
  - Strict-Transport-Security
- ✅ **Input Validation** (8-64 character limits, type checking)
- ✅ **Password Strength Requirements** (uppercase, lowercase, digit, special char)
- ✅ **Account Lockout** (5 failed attempts = 15-minute lockout)
- ✅ **Secure Session Management** (HTTPOnly, SameSite cookies)
- ✅ **Email Confirmation** (optional)
- ✅ **Password Reset** (token-based)
- ✅ **Comprehensive Logging** (security events tracked)
- ✅ **Debug Mode Disabled** (no stack trace exposure)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd password-security-toolkit
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
python init_postgres.py
```
Follow the prompts to create the database and user.

5. **Configure environment variables**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your settings
# IMPORTANT: Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `.env` file:
```env
SECRET_KEY=<paste-generated-key-here>
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=password_security_db
DB_PORT=5555
```

6. **Run the application**
```bash
python app.py
```

7. **Open in browser**
```
http://localhost:6001
```

### Default Admin Account
- Username: `admin`
- Password: `Admin@123`
- Change this password immediately after first login!

## 📁 Project Structure

```
password-security-toolkit/
├── app.py                      # Main Flask application
├── auth.py                     # Authentication routes and logic
├── models.py                   # Database models
├── config.py                   # Configuration settings
├── init_postgres.py            # Database initialization script
├── common_passwords.txt        # Common passwords database (400+ entries)
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create from .env.example)
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules
│
├── templates/                  # HTML templates
│   ├── index.html             # Home page with password tools
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # User dashboard
│   ├── admin_panel.html       # Admin control panel
│   ├── forgot_password.html   # Password reset request
│   └── reset_password.html    # Password reset form
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Stylesheet
│   └── js/
│       └── script.js          # JavaScript functionality
│
├── docs/                       # Documentation
│   ├── ADMIN_PANEL_GUIDE.md
│   ├── HASH_DEMO_GUIDE.md
│   ├── SECURITY_FEATURES.md
│   └── USER_ACTIVITY_UPDATE.md
│
└── logs/                       # Application logs (auto-created)
```

## 🎯 API Endpoints

### Public Endpoints
- `POST /check` - Check password strength (30 requests/min)
- `GET /generate` - Generate secure password (20 requests/min)
- `POST /hash` - Hash password demo (20 requests/min)
- `POST /breach` - Check for breaches (10 requests/min)

### Authentication Endpoints
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout
- `GET/POST /forgot-password` - Request password reset
- `GET/POST /reset-password/<token>` - Reset password
- `GET /confirm/<token>` - Confirm email

### Protected Endpoints
- `GET /dashboard` - User dashboard (requires login)
- `GET /admin` - Admin panel (requires admin role)

## 🛠️ Tech Stack

### Backend
- **Flask 3.0** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Production-grade database
- **Flask-Login** - User session management
- **Flask-WTF** - CSRF protection
- **Flask-Limiter** - Rate limiting
- **Bcrypt** - Password hashing (via Werkzeug)
- **Secrets module** - Cryptographically secure random generation

### Frontend
- **HTML5/CSS3** - Structure and styling
- **JavaScript** - Interactive functionality
- **Font Awesome** - Icons

### Security
- **itsdangerous** - Token generation
- **Werkzeug** - Password hashing utilities
- **Redis** (optional) - Rate limiting storage

## 🔒 Security Best Practices

### Implemented
- ✅ Cryptographically secure password generation (`secrets` module)
- ✅ Bcrypt password hashing (industry standard)
- ✅ Input validation (8-64 character limits)
- ✅ Password complexity requirements
- ✅ CSRF protection on all forms
- ✅ Rate limiting on all endpoints
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ Account lockout after failed attempts
- ✅ Secure session management
- ✅ No hardcoded secrets (environment variables)
- ✅ Debug mode disabled
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (Jinja2 auto-escaping)
- ✅ Error handling (JSON responses, no raw exceptions)

### For Production Deployment
- [ ] Enable HTTPS (set `SESSION_COOKIE_SECURE=True`)
- [ ] Use strong SECRET_KEY (generate with `secrets.token_hex(32)`)
- [ ] Configure real email server for password resets
- [ ] Set up Redis for distributed rate limiting
- [ ] Configure log rotation and monitoring
- [ ] Set up automated database backups
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Set up monitoring and security alerts
- [ ] Review and update security headers for your domain

## 📊 Database Schema

### User Table
- id, username, email, password_hash
- email_confirmed, email_confirmed_at
- is_admin
- failed_login_attempts, account_locked_until
- last_login, created_at

### Password History Table
- id, user_id, password_length
- strength_score, strength_level
- feedback, analyzed_at

### Login Attempt Table
- id, user_id, username_attempted
- ip_address, user_agent
- success, failure_reason, attempted_at

### System Settings Table
- id, setting_key, setting_value
- description, updated_at

### User Activity Table
- id, user_id, activity_type
- details, created_at

## 🧪 Testing

### Test Password Strength
```bash
curl -X POST http://localhost:6001/check -d "password=MySecureP@ssw0rd!"
```

### Generate Password
```bash
curl http://localhost:6001/generate?length=16
```

### Check for Breaches
```bash
curl -X POST http://localhost:6001/breach -d "password=password123"
```

## 📚 Documentation

- **[SECURITY_FEATURES.md](docs/SECURITY_FEATURES.md)** - Complete security documentation
- **[ADMIN_PANEL_GUIDE.md](docs/ADMIN_PANEL_GUIDE.md)** - Admin panel usage guide
- **[HASH_DEMO_GUIDE.md](docs/HASH_DEMO_GUIDE.md)** - Hash demonstration guide

## 🤝 Contributing

This is a college project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is created for educational purposes as a college cybersecurity project.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- OWASP for security best practices
- Have I Been Pwned for breach checking inspiration
- Flask community for excellent documentation

## 📞 Support

For issues or questions:
1. Check the documentation in the `docs/` folder
2. Review the troubleshooting section in SECURITY_FEATURES.md
3. Open an issue on GitHub

## 🎓 Educational Use

This project demonstrates:
- Secure web application development
- Password security best practices
- Database design and management
- User authentication and authorization
- API development and rate limiting
- Security feature implementation

Perfect for:
- Cybersecurity courses
- Web development projects
- Security awareness training
- Portfolio demonstrations

---

**⚠️ Disclaimer**: This is an educational project. While it implements security best practices, always conduct thorough security audits before deploying any application to production.

**🔐 Security Note**: Never store plain text passwords. Always use bcrypt, argon2, or scrypt for password hashing in production systems.
