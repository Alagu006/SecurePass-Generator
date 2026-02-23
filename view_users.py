#!/usr/bin/env python3
"""View all users in the database"""

from app import app
from models import db, User, PasswordHistory, LoginAttempt, UserActivity

def view_all_users():
    """Display all users with their details"""
    with app.app_context():
        users = User.query.order_by(User.id).all()
        
        print("\n" + "="*100)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<8} {'Confirmed':<10} {'Created':<20}")
        print("="*100)
        
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} "
                  f"{'Yes' if user.is_admin else 'No':<8} "
                  f"{'Yes' if user.email_confirmed else 'No':<10} "
                  f"{user.created_at.strftime('%Y-%m-%d %H:%M'):<20}")
        
        print("="*100)
        print(f"\nTotal Users: {len(users)}")
        print(f"Admin Users: {sum(1 for u in users if u.is_admin)}")
        print(f"Confirmed Emails: {sum(1 for u in users if u.email_confirmed)}")
        
        # Show password check stats
        total_checks = PasswordHistory.query.count()
        print(f"\nTotal Password Checks: {total_checks}")
        
        # Show login attempts
        total_logins = LoginAttempt.query.count()
        successful_logins = LoginAttempt.query.filter_by(success=True).count()
        print(f"Total Login Attempts: {total_logins}")
        print(f"Successful Logins: {successful_logins}")

if __name__ == '__main__':
    view_all_users()
