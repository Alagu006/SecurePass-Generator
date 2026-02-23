# Security Policy

## 🔒 Security Features

This Password Security Toolkit implements multiple layers of security to protect user data and prevent common web vulnerabilities.

## ✅ Implemented Security Measures

### 1. Cryptographically Secure Random Generation
- Uses Python's `secrets` module (not `random`)
- `secrets.choice()` for password character selection
- `os.urandom()` for salt generation
- Ensures unpredictable password generation

### 2. Password Hashing
- **Bcrypt** via Werkzeug's `generate_password_hash()`
- Industry-standard password hashing
- Automatic salt generation
- Configurable work factor
- **Never stores plain text passwords**

### 3. Input Validation
- Password length: 8-64 characters
- Type checking for all inputs
- Prevents negative or non-integer values
- Email format validation
- Username format validation

### 4. Password Strength Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character
- Checked against 400+ common passwords

### 5. Rate Limiting
- Login: 5 attempts per minute
- Password check: 30 per minute
- Password generation: 20 per minute
- Hash demo: 15 per minute
- Breach check: 10 per minute
- Prevents brute force attacks

### 6. Account Security
- Account lockout after 5 failed login attempts
- 15-minute lockout duration
- Failed attempt tracking
- Login attempt logging with IP and user agent

### 7. Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'; ...
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 8. CSRF Protection
- Flask-WTF CSRF tokens on all forms
- Protects against Cross-Site Request Forgery
- Automatic token validation

### 9. Session Security
- HTTPOnly cookies (prevents XSS cookie theft)
- SameSite cookies (prevents CSRF)
- Secure cookies in production (HTTPS only)
- Session timeout (1 hour default)
- Strong session protection

### 10. SQL Injection Prevention
- SQLAlchemy ORM (parameterized queries)
- No raw SQL queries
- Input sanitization

### 11. XSS Prevention
- Jinja2 auto-escaping
- Content Security Policy
- Input validation and sanitization

### 12. Error Handling
- JSON error responses
- No stack trace exposure
- Generic error messages (prevents user enumeration)
- Comprehensive logging

### 13. Secure Configuration
- No hardcoded secrets
- Environment variables for sensitive data
- Debug mode disabled
- Separate development/production configs

## 🚨 Known Limitations

### Educational Hash Demo
The `/hash` endpoint demonstrates various hashing algorithms including MD5 and SHA1 for **educational purposes only**. These are clearly marked as insecure and should never be used for password storage in production.

### Email Confirmation
Email confirmation is optional and can be toggled by admins. For production use, implement a real email service (currently shows confirmation links in flash messages for testing).

### Rate Limiting Storage
Uses in-memory storage by default. For production with multiple servers, configure Redis:
```env
REDIS_URL=redis://localhost:6379/0
```

## 🔐 Security Best Practices for Deployment

### 1. Environment Variables
```bash
# Generate a strong SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

Set in `.env`:
```env
SECRET_KEY=<your-generated-key>
SESSION_COOKIE_SECURE=True  # Enable for HTTPS
```

### 2. HTTPS Configuration
- Always use HTTPS in production
- Set `SESSION_COOKIE_SECURE=True`
- Configure SSL/TLS certificates
- Use HSTS header (already implemented)

### 3. Database Security
- Use strong database passwords
- Limit database user permissions
- Enable PostgreSQL SSL connections
- Regular backups
- Keep PostgreSQL updated

### 4. Server Configuration
- Use production WSGI server (Gunicorn/uWSGI)
- Configure firewall rules
- Disable unnecessary services
- Keep system packages updated
- Use fail2ban for brute force protection

### 5. Monitoring and Logging
- Monitor failed login attempts
- Set up alerts for suspicious activity
- Regular log review
- Use log rotation
- Monitor rate limit violations

### 6. Regular Updates
- Keep Python packages updated
- Monitor security advisories
- Update dependencies regularly
- Test updates in staging first

## 🐛 Reporting Security Vulnerabilities

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email security concerns to: [your-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work on a fix.

## 📋 Security Checklist for Production

- [ ] Generate strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set SESSION_COOKIE_SECURE=True
- [ ] Configure real email service
- [ ] Set up Redis for rate limiting
- [ ] Configure database backups
- [ ] Set up monitoring and alerts
- [ ] Review and update security headers
- [ ] Change default admin password
- [ ] Disable email confirmation test links
- [ ] Configure log rotation
- [ ] Set up fail2ban
- [ ] Review firewall rules
- [ ] Enable database SSL
- [ ] Set up automated security updates
- [ ] Conduct security audit
- [ ] Perform penetration testing

## 🔍 Security Testing

### Password Generation Test
```python
import secrets
import string

# Test cryptographic randomness
for _ in range(10):
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    print(password)
```

### Rate Limiting Test
```bash
# Test rate limiting (should block after 5 attempts)
for i in {1..10}; do
  curl -X POST http://localhost:6001/check -d "password=test"
  echo "Attempt $i"
done
```

### CSRF Protection Test
```bash
# Should fail without CSRF token
curl -X POST http://localhost:6001/admin/make-admin/2
```

## 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [Have I Been Pwned](https://haveibeenpwned.com/)

## 🔄 Security Update History

### Version 1.0.0 (Current)
- Initial release with comprehensive security features
- Bcrypt password hashing
- Rate limiting
- CSRF protection
- Security headers
- Account lockout
- Input validation

---

**Last Updated**: February 2026

**Security Contact**: [your-email@example.com]
