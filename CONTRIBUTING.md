# Contributing to Password Security Toolkit

Thank you for your interest in contributing to the Password Security Toolkit! This document provides guidelines for contributing to this project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Any relevant examples

### Security Vulnerabilities

**DO NOT** create public issues for security vulnerabilities!

Instead:
1. Email security concerns to: [your-email@example.com]
2. Include detailed description
3. Wait for response before public disclosure

See [SECURITY.md](SECURITY.md) for more details.

## 🔧 Development Setup

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
git clone https://github.com/your-username/password-security-toolkit.git
cd password-security-toolkit
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment
```bash
# Copy example environment file
cp .env.example .env

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env file
```

### 5. Setup Database
```bash
python init_postgres.py
```

### 6. Run Application
```bash
python app.py
```

## 📝 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://pep8.org/)
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### Code Quality
- Write clear, self-documenting code
- Add comments for complex logic
- Include docstrings for functions
- Keep functions focused and small

### Example
```python
def analyze_password(password):
    """
    Analyze password strength and provide feedback.
    
    Args:
        password (str): The password to analyze
        
    Returns:
        dict: Analysis results including score, strength, and feedback
    """
    score = 0
    feedback_items = []
    
    # Check length
    if len(password) >= 12:
        score += 2
        feedback_items.append("✅ Excellent length")
    
    return {
        'score': score,
        'feedback': feedback_items
    }
```

## 🔒 Security Guidelines

### Must Follow
- ✅ Never commit secrets or credentials
- ✅ Use `secrets` module for random generation
- ✅ Always hash passwords with bcrypt
- ✅ Validate all user inputs
- ✅ Use parameterized queries (SQLAlchemy ORM)
- ✅ Implement rate limiting for new endpoints
- ✅ Add CSRF protection to forms
- ✅ Return generic error messages

### Never Do
- ❌ Use `random` module for security
- ❌ Store plain text passwords
- ❌ Expose stack traces
- ❌ Hardcode secrets
- ❌ Skip input validation
- ❌ Use raw SQL queries
- ❌ Disable security features

## 🧪 Testing

### Before Submitting
- Test all new features
- Test edge cases
- Test error handling
- Test security features
- Test on different browsers (if UI changes)

### Manual Testing
```bash
# Test password generation
curl http://localhost:6001/generate?length=16

# Test password check
curl -X POST http://localhost:6001/check -d "password=Test123!"

# Test rate limiting
for i in {1..10}; do curl http://localhost:6001/generate; done
```

## 📋 Pull Request Process

### 1. Create Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes
- Write clean, documented code
- Follow coding standards
- Test thoroughly
- Update documentation if needed

### 3. Commit Changes
```bash
git add .
git commit -m "Add feature: description"
```

Use clear commit messages:
- `Add feature: password complexity checker`
- `Fix bug: rate limiting not working`
- `Update docs: installation instructions`
- `Refactor: improve password generation logic`

### 4. Push to Fork
```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request
- Go to GitHub repository
- Click "New Pull Request"
- Select your branch
- Fill in the template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Security improvement

## Testing
- [ ] Tested locally
- [ ] All tests pass
- [ ] No security issues

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🎯 Areas for Contribution

### High Priority
- Additional password strength algorithms
- More hash algorithm demonstrations
- Improved breach checking (API integration)
- Email service integration
- Two-factor authentication
- Password history tracking

### Medium Priority
- UI/UX improvements
- Mobile responsiveness enhancements
- Additional security headers
- Performance optimizations
- Internationalization (i18n)

### Low Priority
- Dark mode theme
- Export password history
- Password strength visualization
- Custom password policies

## 📚 Documentation

### When to Update Docs
- Adding new features
- Changing API endpoints
- Modifying configuration
- Adding dependencies
- Changing security features

### Documentation Files
- `README.md` - Main documentation
- `SECURITY.md` - Security policy
- `docs/` - Detailed guides
- Code comments - Inline documentation

## 🐛 Bug Fix Guidelines

### 1. Reproduce the Bug
- Confirm the bug exists
- Document steps to reproduce
- Identify affected versions

### 2. Fix the Bug
- Create a branch
- Write the fix
- Test thoroughly
- Add regression test if possible

### 3. Document the Fix
- Update CHANGELOG (if exists)
- Reference issue number
- Explain the fix in commit message

## ✨ Feature Guidelines

### 1. Discuss First
- Create an issue to discuss
- Get feedback from maintainers
- Ensure it fits project scope

### 2. Implement Feature
- Follow coding standards
- Add documentation
- Include tests
- Update README if needed

### 3. Submit PR
- Reference issue number
- Explain implementation
- Show examples/screenshots

## 🔄 Review Process

### What We Look For
- Code quality and style
- Security considerations
- Test coverage
- Documentation
- Breaking changes

### Timeline
- Initial review: 2-3 days
- Feedback provided
- Revisions requested if needed
- Merge when approved

## 📞 Getting Help

### Questions?
- Check existing issues
- Read documentation
- Ask in discussions
- Contact maintainers

### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OWASP Guidelines](https://owasp.org/)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Questions?** Open an issue or contact the maintainers.

**Happy Contributing!** 🎉
