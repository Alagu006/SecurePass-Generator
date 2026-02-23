from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
import os

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Email confirmation
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Admin flag
    is_admin = db.Column(db.Boolean, default=False)
    
    # Account security
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Password reset
    password_reset_token = db.Column(db.String(100), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    password_history = db.relationship('PasswordHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    login_attempts = db.relationship('LoginAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.account_locked_until:
            if datetime.utcnow() < self.account_locked_until:
                return True
            else:
                # Lock expired, reset
                self.account_locked_until = None
                self.failed_login_attempts = 0
                db.session.commit()
        return False
    
    def lock_account(self, duration_seconds=900):
        """Lock account for specified duration"""
        self.account_locked_until = datetime.utcnow() + timedelta(seconds=duration_seconds)
        db.session.commit()
    
    def increment_failed_login(self):
        """Increment failed login attempts"""
        self.failed_login_attempts += 1
        db.session.commit()
    
    def reset_failed_login(self):
        """Reset failed login attempts"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        db.session.commit()
    
    def generate_confirmation_token(self):
        """Generate email confirmation token"""
        serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
        return serializer.dumps(self.email, salt='email-confirm')
    
    def generate_reset_token(self):
        """Generate password reset token"""
        serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
        return serializer.dumps(self.email, salt='password-reset')
    
    @staticmethod
    def verify_token(token, salt='email-confirm', expiration=3600):
        """Verify token and return email"""
        serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
        try:
            email = serializer.loads(token, salt=salt, max_age=expiration)
            return email
        except:
            return None
    
    def __repr__(self):
        return f'<User {self.username}>'


class PasswordHistory(db.Model):
    """Store password analysis history"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Password metadata (we don't store actual passwords!)
    password_length = db.Column(db.Integer, nullable=False)
    strength_score = db.Column(db.Integer, nullable=False)
    strength_level = db.Column(db.String(20), nullable=False)  # WEAK/FAIR/GOOD/EXCELLENT
    
    # Analysis results
    feedback = db.Column(db.Text, nullable=False)
    
    # Timestamp
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'id': self.id,
            'password_length': self.password_length,
            'strength_score': self.strength_score,
            'strength_level': self.strength_level,
            'analyzed_at': self.analyzed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'feedback': self.feedback.split('|')  # Stored as pipe-separated
        }


class LoginAttempt(db.Model):
    """Track login attempts for security monitoring"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username_attempted = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(200), nullable=True)
    success = db.Column(db.Boolean, default=False)
    failure_reason = db.Column(db.String(100), nullable=True)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<LoginAttempt {self.username_attempted} - {"Success" if self.success else "Failed"}>'


class SystemSettings(db.Model):
    """System-wide settings controlled by admin"""
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default='false'):
        """Get a setting value"""
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        return setting.setting_value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """Set a setting value"""
        setting = SystemSettings.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = value
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                setting_key=key,
                setting_value=value,
                description=description
            )
            db.session.add(setting)
        db.session.commit()
    
    @staticmethod
    def is_email_confirmation_required():
        """Check if email confirmation is required for login"""
        return SystemSettings.get_setting('require_email_confirmation', 'false').lower() == 'true'
    
    def __repr__(self):
        return f'<SystemSettings {self.setting_key}={self.setting_value}>'


class UserActivity(db.Model):
    """Track user activities on the home page"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # check, generate, hash, breach
    details = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('activities', lazy=True, cascade='all, delete-orphan'))
    
    @staticmethod
    def log_activity(user_id, activity_type, details):
        """Log a user activity"""
        try:
            activity = UserActivity(
                user_id=user_id,
                activity_type=activity_type,
                details=details
            )
            db.session.add(activity)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
    
    def __repr__(self):
        return f'<UserActivity {self.activity_type} by user {self.user_id}>'
