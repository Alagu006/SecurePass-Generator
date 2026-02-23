from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, LoginAttempt, SystemSettings
from datetime import datetime, timedelta
import re
import logging

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def log_login_attempt(username, success, failure_reason=None, user_id=None):
    """Log login attempt for security monitoring"""
    try:
        attempt = LoginAttempt(
            user_id=user_id,
            username_attempted=username,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:200],
            success=success,
            failure_reason=failure_reason
        )
        db.session.add(attempt)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log login attempt: {str(e)}")
        db.session.rollback()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login with account lockout protection"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        if not username or not password:
            flash('Please provide both username and password', 'danger')
            log_login_attempt(username or 'unknown', False, 'Missing credentials')
            return render_template('login.html')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # Generic error message for security
            flash('Invalid credentials', 'danger')
            log_login_attempt(username, False, 'User not found')
            logger.warning(f"Login attempt for non-existent user: {username} from {request.remote_addr}")
            return render_template('login.html')
        
        # Check if account is locked
        if user.is_account_locked():
            time_remaining = (user.account_locked_until - datetime.utcnow()).total_seconds()
            minutes = int(time_remaining / 60)
            flash(f'Account is locked. Please try again in {minutes} minutes.', 'danger')
            log_login_attempt(username, False, 'Account locked', user.id)
            logger.warning(f"Login attempt for locked account: {username} from {request.remote_addr}")
            return render_template('login.html')
        
        # Check if email is confirmed (only if setting is enabled)
        if SystemSettings.is_email_confirmation_required() and not user.email_confirmed:
            flash('Please confirm your email address before logging in.', 'warning')
            log_login_attempt(username, False, 'Email not confirmed', user.id)
            return render_template('login.html')
        
        # Verify password
        if user.check_password(password):
            # Successful login
            user.reset_failed_login()
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            log_login_attempt(username, True, user_id=user.id)
            logger.info(f"Successful login: {username} from {request.remote_addr}")
            
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            # Failed login
            user.increment_failed_login()
            log_login_attempt(username, False, 'Invalid password', user.id)
            logger.warning(f"Failed login attempt: {username} from {request.remote_addr}")
            
            max_attempts = int(current_app.config.get('MAX_LOGIN_ATTEMPTS', 5))
            remaining = max_attempts - user.failed_login_attempts
            
            if user.failed_login_attempts >= max_attempts:
                lockout_duration = int(current_app.config.get('ACCOUNT_LOCKOUT_DURATION', 900))
                user.lock_account(lockout_duration)
                flash('Too many failed attempts. Account locked for 15 minutes.', 'danger')
                logger.warning(f"Account locked due to failed attempts: {username}")
            elif remaining > 0:
                flash(f'Invalid credentials. {remaining} attempts remaining.', 'danger')
            else:
                flash('Invalid credentials', 'danger')
    
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with email confirmation"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        # Username validation
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        elif len(username) > 80:
            errors.append('Username must be less than 80 characters')
        elif not re.match(r'^[a-zA-Z0-9_-]+$', username):
            errors.append('Username can only contain letters, numbers, underscores, and hyphens')
        
        # Email validation
        if not email:
            errors.append('Email is required')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Invalid email format')
        
        # Check if user exists
        if username and User.query.filter_by(username=username).first():
            errors.append('Username already exists')
        
        if email and User.query.filter_by(email=email).first():
            errors.append('Email already registered')
        
        # Password strength validation
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            try:
                # Create new user
                new_user = User(username=username, email=email)
                new_user.set_password(password)
                new_user.email_confirmed = False  # Require email confirmation
                
                db.session.add(new_user)
                db.session.commit()
                
                # Generate confirmation token
                token = new_user.generate_confirmation_token()
                
                # In production, send email here
                # For now, just show the token (remove this in production!)
                confirmation_url = url_for('auth.confirm_email', token=token, _external=True)
                
                logger.info(f"New user registered: {username} ({email})")
                flash('Registration successful! Please check your email to confirm your account.', 'success')
                flash(f'Confirmation link (for testing): {confirmation_url}', 'info')
                
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Registration error: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('register.html')

@auth.route('/confirm/<token>')
def confirm_email(token):
    """Confirm email address"""
    try:
        email = User.verify_token(token, salt='email-confirm', expiration=86400)  # 24 hours
        if not email:
            flash('Invalid or expired confirmation link.', 'danger')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.login'))
        
        if user.email_confirmed:
            flash('Email already confirmed. Please login.', 'info')
        else:
            user.email_confirmed = True
            user.email_confirmed_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Email confirmed for user: {user.username}")
            flash('Email confirmed successfully! You can now login.', 'success')
        
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Email confirmation error: {str(e)}")
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address', 'danger')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        # Always show success message for security (don't reveal if email exists)
        flash('If an account exists with that email, you will receive password reset instructions.', 'info')
        
        if user:
            # Generate reset token
            token = user.generate_reset_token()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            # In production, send email here
            # For now, just log it
            logger.info(f"Password reset requested for: {user.username}")
            flash(f'Reset link (for testing): {reset_url}', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Verify token
    email = User.verify_token(token, salt='password-reset', expiration=3600)  # 1 hour
    if not email:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        
        # Password strength validation
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            try:
                user.set_password(password)
                user.reset_failed_login()  # Reset any lockouts
                db.session.commit()
                
                logger.info(f"Password reset successful for: {user.username}")
                flash('Password reset successful! You can now login.', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Password reset error: {str(e)}")
                flash('An error occurred. Please try again.', 'danger')
    
    return render_template('reset_password.html', token=token)

@auth.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))
