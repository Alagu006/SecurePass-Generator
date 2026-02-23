from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import get_config
from models import db, User, PasswordHistory, SystemSettings, UserActivity
from auth import auth as auth_blueprint
import hashlib
import secrets
import string
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from functools import wraps
import socket

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(get_config(config_name))

# Setup logging
def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        # File handler
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            app.config.get('LOG_FILE', 'logs/app.log'),
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL', 'INFO')))
    app.logger.info('Password Security Toolkit startup')

setup_logging(app)

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config['RATELIMIT_STORAGE_URL']
)

# Register blueprints
app.register_blueprint(auth_blueprint)

# ==================== SECURITY HEADERS ====================

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline'; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:"
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# ==================== USER LOADER ====================

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ==================== ADMIN DECORATOR ====================

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== HELPER FUNCTIONS ====================

# Load common passwords from file
def load_common_passwords():
    """Load common passwords from file"""
    passwords = []
    try:
        with open('common_passwords.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    passwords.append(line.lower())
        app.logger.info(f"Loaded {len(passwords)} common passwords from file")
    except FileNotFoundError:
        app.logger.warning("common_passwords.txt not found, using default list")
        passwords = [
            "password", "123456", "12345678", "qwerty", "abc123",
            "password1", "admin", "letmein", "welcome", "monkey",
            "dragon", "baseball", "football", "1234567", "superman",
            "iloveyou", "starwars", "hello", "charlie", "123123"
        ]
    except Exception as e:
        app.logger.error(f"Error loading common passwords: {str(e)}")
        passwords = ["password", "123456", "12345678", "qwerty", "abc123"]
    return passwords

COMMON_PASSWORDS = load_common_passwords()

def analyze_password(password):
    """Analyze password strength"""
    score = 0
    max_score = 7  # Updated: length can give 2 points
    feedback_items = []
    
    # Check length (worth 2 points for excellent, 1 for good)
    if len(password) >= 12:
        score += 2
        feedback_items.append("✅ Excellent length (12+ characters)")
    elif len(password) >= 8:
        score += 1
        feedback_items.append("⚠️ Good length, but 12+ is better")
    else:
        feedback_items.append("❌ Too short! Use at least 8 characters")
    
    # Check uppercase
    if any(c.isupper() for c in password):
        score += 1
        feedback_items.append("✅ Contains uppercase letters")
    else:
        feedback_items.append("❌ Add UPPERCASE letters")
    
    # Check lowercase
    if any(c.islower() for c in password):
        score += 1
        feedback_items.append("✅ Contains lowercase letters")
    else:
        feedback_items.append("❌ Add lowercase letters")
    
    # Check numbers
    if any(c.isdigit() for c in password):
        score += 1
        feedback_items.append("✅ Contains numbers")
    else:
        feedback_items.append("❌ Add numbers (0-9)")
    
    # Check special characters
    special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        score += 1
        feedback_items.append("✅ Contains special characters")
    else:
        feedback_items.append("❌ Add special characters (!@#$...)")
    
    # Check against common passwords
    if password.lower() not in COMMON_PASSWORDS:
        score += 1
        feedback_items.append("✅ Not a commonly used password")
    else:
        feedback_items.append("⚠️ WARNING: This is a very common password!")
    
    # Determine strength level
    if score >= 6:
        strength = "EXCELLENT"
        strength_color = "green"
    elif score >= 4:
        strength = "GOOD"
        strength_color = "blue"
    elif score >= 3:
        strength = "FAIR"
        strength_color = "orange"
    else:
        strength = "WEAK"
        strength_color = "red"
    
    # Time to crack estimate
    if score >= 6:
        crack_time = "Centuries with current technology"
    elif score >= 4:
        crack_time = "Years to decades"
    elif score >= 3:
        crack_time = "Days to months"
    else:
        crack_time = "Seconds to hours"
    
    return {
        'score': score,
        'max_score': max_score,
        'strength': strength,
        'strength_color': strength_color,
        'crack_time': crack_time,
        'feedback': feedback_items,
        'length': len(password)
    }

def generate_secure_password(length=16):
    """Generate a cryptographically secure random password"""
    # Input validation
    if not isinstance(length, int) or length < 8:
        length = 8
    if length > 64:
        length = 64
        
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    all_chars = lower + upper + digits + symbols
    
    # Ensure at least one of each type using secrets module
    password_chars = [
        secrets.choice(lower),
        secrets.choice(upper),
        secrets.choice(digits),
        secrets.choice(symbols)
    ]
    
    # Fill the rest randomly using secrets
    remaining = length - 4
    password_chars.extend(secrets.choice(all_chars) for _ in range(remaining))
    
    # Shuffle to avoid predictable patterns using secrets
    # secrets doesn't have shuffle, so we'll use SystemRandom
    import random
    secure_random = random.SystemRandom()
    secure_random.shuffle(password_chars)
    password = ''.join(password_chars)
    
    # Ensure it's not a common password
    if password.lower() in COMMON_PASSWORDS:
        return generate_secure_password(length)
    
    return password

# ==================== ROUTES ====================

@app.route('/')
def home():
    """Home page"""
    try:
        app.logger.info("Home route accessed")
        recent_activity = []
        if current_user.is_authenticated:
            # Get user's recent 10 activities
            recent_activity = UserActivity.query.filter_by(
                user_id=current_user.id
            ).order_by(UserActivity.created_at.desc()).limit(10).all()
        
        app.logger.info("Rendering index.html")
        return render_template('index.html', recent_activity=recent_activity)
    except Exception as e:
        app.logger.error(f"Error in home route: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/test')
def test():
    """Simple test route"""
    return "Flask is working!", 200

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    try:
        # Get user's history
        history = PasswordHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(PasswordHistory.analyzed_at.desc()).limit(10).all()
        
        # Calculate stats
        total_checks = PasswordHistory.query.filter_by(user_id=current_user.id).count()
        strong_passwords = PasswordHistory.query.filter_by(
            user_id=current_user.id
        ).filter(PasswordHistory.strength_level.in_(['GOOD', 'EXCELLENT'])).count()
        
        return render_template('dashboard.html', 
                             history=history,
                             total_checks=total_checks,
                             strong_passwords=strong_passwords)
    except Exception as e:
        app.logger.error(f"Dashboard error: {str(e)}")
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('home'))

# ==================== API ENDPOINTS ====================

@app.route('/check', methods=['POST'])
@csrf.exempt
@limiter.limit("30 per minute")
def check_password():
    """Check password strength - API endpoint"""
    try:
        password = request.form.get('password', '')
        
        if not password:
            return jsonify({'error': 'No password provided'}), 400
        
        # Input validation
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        if len(password) > 64:
            return jsonify({'error': 'Password too long (max 64 characters)'}), 400
        
        result = analyze_password(password)
        
        # Save to history if user is logged in
        if current_user.is_authenticated:
            try:
                history = PasswordHistory(
                    user_id=current_user.id,
                    password_length=result['length'],
                    strength_score=result['score'],
                    strength_level=result['strength'],
                    feedback='|'.join(result['feedback'])
                )
                db.session.add(history)
                db.session.commit()
                
                result['saved_to_history'] = True
                result['history_id'] = history.id
                
                # Log activity
                UserActivity.log_activity(
                    current_user.id,
                    'check',
                    f"Strength: {result['strength']} | Score: {result['score']}/{result['max_score']}"
                )
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error saving password history: {str(e)}")
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Password check error: {str(e)}")
        return jsonify({'error': 'An error occurred while checking the password'}), 500

@app.route('/generate', methods=['GET'])
@limiter.limit("20 per minute")
def generate():
    """Generate secure password"""
    try:
        length = request.args.get('length', 16, type=int)
        
        # Input validation
        if not isinstance(length, int) or length < 8:
            return jsonify({'error': 'Password length must be at least 8 characters'}), 400
        
        if length > 64:
            return jsonify({'error': 'Password length cannot exceed 64 characters'}), 400
        
        password = generate_secure_password(length)
        
        # Analyze it
        analysis = analyze_password(password)
        
        # Log activity if user is logged in
        if current_user.is_authenticated:
            UserActivity.log_activity(
                current_user.id,
                'generate',
                f"Length: {length} | Strength: {analysis['strength']}"
            )
        
        return jsonify({
            'password': password,
            'analysis': analysis
        })
    
    except Exception as e:
        app.logger.error(f"Password generation error: {str(e)}")
        return jsonify({'error': 'An error occurred while generating the password'}), 500

@app.route('/hash', methods=['POST'])
@csrf.exempt
@limiter.limit("20 per minute")
def hash_password():
    """Hash a password with multiple algorithms - Educational Demo"""
    try:
        password = request.form.get('password', '')
        
        if not password:
            return jsonify({'error': 'No password provided'}), 400
        
        # Input validation
        if len(password) > 64:
            return jsonify({'error': 'Password too long (max 64 characters)'}), 400
        
        # Basic hashes (INSECURE - for educational purposes only!)
        basic_hashes = {
            'md5': hashlib.md5(password.encode()).hexdigest(),
            'sha1': hashlib.sha1(password.encode()).hexdigest(),
            'sha224': hashlib.sha224(password.encode()).hexdigest(),
            'sha256': hashlib.sha256(password.encode()).hexdigest(),
            'sha384': hashlib.sha384(password.encode()).hexdigest(),
            'sha512': hashlib.sha512(password.encode()).hexdigest(),
        }
        
        # Generate multiple salts for demonstration
        salt_16 = os.urandom(16).hex()
        salt_32 = os.urandom(32).hex()
        
        # Salted hashes (better, but still not production-ready)
        salted_hashes = {
            'sha256_salted_16': hashlib.sha256((password + salt_16).encode()).hexdigest(),
            'sha256_salted_32': hashlib.sha256((password + salt_32).encode()).hexdigest(),
            'sha512_salted_16': hashlib.sha512((password + salt_16).encode()).hexdigest(),
            'sha512_salted_32': hashlib.sha512((password + salt_32).encode()).hexdigest(),
        }
        
        # PBKDF2 (better - includes iterations)
        pbkdf2_salt = os.urandom(32)
        pbkdf2_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), pbkdf2_salt, 100000)
        
        # Demonstrate hash collision resistance
        similar_password = password + "1"
        collision_demo = {
            'original_md5': hashlib.md5(password.encode()).hexdigest(),
            'similar_md5': hashlib.md5(similar_password.encode()).hexdigest(),
            'note': 'Notice how a tiny change creates a completely different hash'
        }
        
        # Security recommendations
        security_notes = {
            'insecure': ['MD5', 'SHA1'],
            'not_recommended': ['SHA256 without salt', 'SHA512 without salt'],
            'better': ['SHA256 with salt', 'SHA512 with salt', 'PBKDF2'],
            'production_ready': ['bcrypt', 'argon2', 'scrypt'],
            'recommendation': 'Always use bcrypt, argon2, or scrypt for password storage in production!'
        }
        
        return jsonify({
            'password': password,
            'password_length': len(password),
            'basic_hashes': basic_hashes,
            'salted_hashes': salted_hashes,
            'salts': {
                'salt_16_bytes': salt_16,
                'salt_32_bytes': salt_32,
            },
            'pbkdf2': {
                'hash': pbkdf2_hash.hex(),
                'salt': pbkdf2_salt.hex(),
                'iterations': 100000,
                'algorithm': 'sha256'
            },
            'collision_demo': collision_demo,
            'security_notes': security_notes,
            'warning': '⚠️ This is for EDUCATIONAL purposes only! Never use MD5/SHA1 for passwords in production.',
            'best_practice': '✅ Use bcrypt, argon2id, or scrypt with proper work factors for production systems.'
        })
        
        # Log activity if user is logged in
        if current_user.is_authenticated:
            UserActivity.log_activity(
                current_user.id,
                'hash',
                f"Hashed password with multiple algorithms (MD5, SHA1, SHA256, SHA512, PBKDF2)"
            )
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Password hashing error: {str(e)}")
        return jsonify({'error': 'An error occurred while hashing the password'}), 500

@app.route('/breach', methods=['POST'])
@csrf.exempt
@limiter.limit("10 per minute")
def check_breach():
    """Check if password is in common breaches"""
    try:
        password = request.form.get('password', '')
        
        if not password:
            return jsonify({'error': 'No password provided'}), 400
        
        # Input validation
        if len(password) > 64:
            return jsonify({'error': 'Password too long (max 64 characters)'}), 400
        
        # Check if in common passwords
        in_breach = password.lower() in [p.lower() for p in COMMON_PASSWORDS]
        
        # Check variations
        variations = [
            password.lower(),
            password.upper(),
            password + "123",
            "123" + password,
        ]
        
        found_variations = []
        for var in variations:
            if var.lower() in [p.lower() for p in COMMON_PASSWORDS]:
                found_variations.append(var)
        
        return jsonify({
            'in_breach': in_breach,
            'found_variations': found_variations,
            'message': 'Password found in common breach lists!' if in_breach else 'Not found in common breaches',
            'note': 'This checks against a limited database. For comprehensive checks, use haveibeenpwned.com',
            'database_size': len(COMMON_PASSWORDS)
        })
        
        # Log activity if user is logged in
        if current_user.is_authenticated:
            status = "Found in breach database!" if in_breach else "Not found in breaches"
            UserActivity.log_activity(
                current_user.id,
                'breach',
                status
            )
        
        return jsonify(result)
    
    except Exception as e:
        app.logger.error(f"Breach check error: {str(e)}")
        return jsonify({'error': 'An error occurred while checking for breaches'}), 500

@app.route('/hash-demo', methods=['POST'])
@csrf.exempt
@limiter.limit("15 per minute")
def hash_demo():
    """Interactive hash demonstration with multiple passwords"""
    try:
        passwords = request.form.getlist('passwords[]')
        
        if not passwords:
            return jsonify({'error': 'No passwords provided'}), 400
        
        if len(passwords) > 10:
            return jsonify({'error': 'Maximum 10 passwords allowed'}), 400
        
        results = []
        
        for pwd in passwords:
            # Input validation
            if len(pwd) > 64:
                continue
                
            # Generate consistent salt for comparison
            salt = hashlib.sha256(pwd.encode()).digest()[:16]
            
            result = {
                'password': pwd,
                'length': len(pwd),
                'hashes': {
                    'md5': hashlib.md5(pwd.encode()).hexdigest(),
                    'sha256': hashlib.sha256(pwd.encode()).hexdigest(),
                    'sha512': hashlib.sha512(pwd.encode()).hexdigest()[:64] + '...',  # Truncate for display
                },
                'salted_sha256': hashlib.sha256((pwd + salt.hex()).encode()).hexdigest(),
                'in_common_list': pwd.lower() in [p.lower() for p in COMMON_PASSWORDS]
            }
            results.append(result)
        
        return jsonify({
            'results': results,
            'total_processed': len(results),
            'note': 'Notice how similar passwords produce completely different hashes'
        })
    
    except Exception as e:
        app.logger.error(f"Hash demo error: {str(e)}")
        return jsonify({'error': 'An error occurred during hash demonstration'}), 500

@app.route('/compare-hashes', methods=['POST'])
@csrf.exempt
@limiter.limit("15 per minute")
def compare_hashes():
    """Compare how different algorithms hash the same password"""
    try:
        password = request.form.get('password', '')
        
        if not password:
            return jsonify({'error': 'No password provided'}), 400
        
        # Input validation
        if len(password) > 64:
            return jsonify({'error': 'Password too long (max 64 characters)'}), 400
        
        # Generate different salts
        salt_small = os.urandom(8)
        salt_medium = os.urandom(16)
        salt_large = os.urandom(32)
        
        comparison = {
            'original_password': password,
            'algorithms': {
                'md5': {
                    'hash': hashlib.md5(password.encode()).hexdigest(),
                    'length': 32,
                    'security': 'BROKEN - Do not use!',
                    'speed': 'Very Fast (BAD for passwords)',
                    'collision_resistant': False
                },
                'sha1': {
                    'hash': hashlib.sha1(password.encode()).hexdigest(),
                    'length': 40,
                    'security': 'BROKEN - Do not use!',
                    'speed': 'Very Fast (BAD for passwords)',
                    'collision_resistant': False
                },
                'sha256': {
                    'hash': hashlib.sha256(password.encode()).hexdigest(),
                    'length': 64,
                    'security': 'Good, but needs salt and iterations',
                    'speed': 'Fast (needs slowing down)',
                    'collision_resistant': True
                },
                'sha512': {
                    'hash': hashlib.sha512(password.encode()).hexdigest(),
                    'length': 128,
                    'security': 'Good, but needs salt and iterations',
                    'speed': 'Fast (needs slowing down)',
                    'collision_resistant': True
                },
                'sha256_salted_8': {
                    'hash': hashlib.sha256((password + salt_small.hex()).encode()).hexdigest(),
                    'salt': salt_small.hex(),
                    'length': 64,
                    'security': 'Better - has salt',
                    'speed': 'Fast',
                    'collision_resistant': True
                },
                'sha256_salted_16': {
                    'hash': hashlib.sha256((password + salt_medium.hex()).encode()).hexdigest(),
                    'salt': salt_medium.hex(),
                    'length': 64,
                    'security': 'Better - has good salt',
                    'speed': 'Fast',
                    'collision_resistant': True
                },
                'sha512_salted_32': {
                    'hash': hashlib.sha512((password + salt_large.hex()).encode()).hexdigest(),
                    'salt': salt_large.hex(),
                    'length': 128,
                    'security': 'Better - has strong salt',
                    'speed': 'Fast',
                    'collision_resistant': True
                },
                'pbkdf2_sha256': {
                    'hash': hashlib.pbkdf2_hmac('sha256', password.encode(), salt_medium, 100000).hex(),
                    'salt': salt_medium.hex(),
                    'iterations': 100000,
                    'length': 64,
                    'security': 'Good - has iterations',
                    'speed': 'Slow (GOOD for passwords)',
                    'collision_resistant': True
                }
            },
            'recommendations': {
                'never_use': ['MD5', 'SHA1', 'Plain SHA256/SHA512'],
                'acceptable': ['PBKDF2 with 100k+ iterations'],
                'recommended': ['bcrypt', 'argon2id', 'scrypt'],
                'why_slow_is_good': 'Slow hashing makes brute-force attacks impractical'
            }
        }
        
        return jsonify(comparison)
    
    except Exception as e:
        app.logger.error(f"Hash comparison error: {str(e)}")
        return jsonify({'error': 'An error occurred during comparison'}), 500

# ==================== ADMIN PANEL ====================

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin control panel"""
    try:
        # Get current settings
        email_confirmation_required = SystemSettings.is_email_confirmation_required()
        
        # Get statistics
        total_users = User.query.count()
        total_checks = PasswordHistory.query.count()
        confirmed_users = User.query.filter_by(email_confirmed=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        
        # Get all users
        users = User.query.order_by(User.created_at.desc()).all()
        
        return render_template('admin_panel.html',
                             email_confirmation_required=email_confirmation_required,
                             total_users=total_users,
                             total_checks=total_checks,
                             confirmed_users=confirmed_users,
                             admin_users=admin_users,
                             users=users)
    except Exception as e:
        app.logger.error(f"Admin panel error: {str(e)}")
        flash('Error loading admin panel', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/admin/toggle-email-confirmation', methods=['POST'])
@csrf.exempt
@admin_required
def toggle_email_confirmation():
    """Toggle email confirmation requirement"""
    try:
        current_value = SystemSettings.is_email_confirmation_required()
        new_value = 'false' if current_value else 'true'
        
        SystemSettings.set_setting(
            'require_email_confirmation',
            new_value,
            'Require users to confirm email before login'
        )
        
        status = 'enabled' if new_value == 'true' else 'disabled'
        flash(f'Email confirmation requirement {status}!', 'success')
        app.logger.info(f"Email confirmation requirement {status} by {current_user.username}")
        
    except Exception as e:
        app.logger.error(f"Toggle email confirmation error: {str(e)}")
        flash('Error updating setting', 'danger')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/make-admin/<int:user_id>', methods=['POST'])
@csrf.exempt
@admin_required
def make_admin(user_id):
    """Make a user an admin"""
    try:
        user = db.session.get(User, user_id)
        if user:
            user.is_admin = True
            db.session.commit()
            flash(f'User {user.username} is now an admin!', 'success')
            app.logger.info(f"User {user.username} made admin by {current_user.username}")
        else:
            flash('User not found', 'danger')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Make admin error: {str(e)}")
        flash('Error updating user', 'danger')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/remove-admin/<int:user_id>', methods=['POST'])
@csrf.exempt
@admin_required
def remove_admin(user_id):
    """Remove admin privileges from a user"""
    try:
        if user_id == current_user.id:
            flash('You cannot remove your own admin privileges!', 'danger')
            return redirect(url_for('admin_panel'))
        
        user = db.session.get(User, user_id)
        if user:
            user.is_admin = False
            db.session.commit()
            flash(f'Admin privileges removed from {user.username}!', 'success')
            app.logger.info(f"Admin removed from {user.username} by {current_user.username}")
        else:
            flash('User not found', 'danger')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Remove admin error: {str(e)}")
        flash('Error updating user', 'danger')
    
    return redirect(url_for('admin_panel'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('An internal error occurred. Please try again.', 'danger')
    return render_template('index.html'), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description)
    }), 429

# ==================== DATABASE INITIALIZATION ====================

def init_database():
    """Initialize database with default data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create default system settings
            if not SystemSettings.query.filter_by(setting_key='require_email_confirmation').first():
                SystemSettings.set_setting(
                    'require_email_confirmation',
                    'false',  # Disabled by default for easy user login
                    'Require users to confirm email before login'
                )
                print("✅ Default system settings created")
            
            # Create admin user if not exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@cybersecurity.com',
                    email_confirmed=True,  # Auto-confirm admin
                    email_confirmed_at=datetime.utcnow(),
                    is_admin=True  # Make admin
                )
                admin.set_password('Admin@123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created: username='admin', password='Admin@123'")
                app.logger.info("Admin user created")
            else:
                # Ensure existing admin has admin flag
                if not admin.is_admin:
                    admin.is_admin = True
                    db.session.commit()
                    print("✅ Admin user updated with admin privileges")
                else:
                    print("✅ Admin user already exists")
        except Exception as e:
            print(f"❌ Database initialization error: {str(e)}")
            app.logger.error(f"Database initialization error: {str(e)}")
            print("Make sure PostgreSQL is running and credentials in .env are correct")

# ==================== RUN APPLICATION ====================

def get_local_ip():
    """Get local IP address for network access"""
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "Unable to detect"

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Get local IP for network access
    local_ip = get_local_ip()
    
    print("\n🔐 Password Security Toolkit")
    print("=" * 50)
    print(f"🌐 Environment: {config_name}")
    print(f"\n📍 Access URLs:")
    print(f"   Local:   http://localhost:6001")
    print(f"   Network: http://{local_ip}:6001")
    print(f"\n💡 Other devices on your network can access using:")
    print(f"   http://{local_ip}:6001")
    print("👤 Test user: admin / Admin@123")
    print(f"\n📚 Common Passwords Database: {len(COMMON_PASSWORDS)} entries")
    print("\n📡 API Endpoints:")
    print("   POST /check          - Check password strength")
    print("   GET  /generate       - Generate secure password")
    print("   POST /hash           - Hash password demo (multiple algorithms)")
    print("   POST /hash-demo      - Batch hash demonstration")
    print("   POST /compare-hashes - Compare hash algorithms")
    print("   POST /breach         - Check for breaches")
    print("   GET  /dashboard      - User dashboard (login required)")
    print("\n⚡ Rate Limits:")
    print("   /check: 30 per minute")
    print("   /generate: 20 per minute")
    print("   /hash: 20 per minute")
    print("   /hash-demo: 15 per minute")
    print("   /compare-hashes: 15 per minute")
    print("   /breach: 10 per minute")
    print("=" * 50)
    
    # Run on all network interfaces (0.0.0.0) to allow network access
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=6001)
