# Admin Panel Guide

## Overview
The Admin Panel allows administrators to control system-wide settings and manage users. Email confirmation is now **optional** and can be toggled on/off by admins.

## Key Changes

### 1. Email Confirmation is Optional
- **Default**: DISABLED (users can login immediately after registration)
- **Control**: Admins can enable/disable via Admin Panel
- **Benefit**: Normal users can login easily without email confirmation hassle

### 2. Admin Panel Access
- Only users with `is_admin=True` can access the admin panel
- Default admin account: `admin` / `Admin@123`
- Access at: `http://localhost:5000/admin`

## Features

### System Settings
- **Email Confirmation Toggle**
  - Enable: Users must confirm email before login
  - Disable: Users can login immediately (default)
  - Real-time toggle with visual feedback

### User Management
- View all registered users
- See user status (email confirmed/pending)
- See user roles (Admin/User)
- Make users admins
  - Remove admin privileges
- View user statistics

### Statistics Dashboard
- Total users count
- Confirmed emails count
- Admin users count
- Total password checks

## How to Use

### Setup (First Time)

1. **Recreate Database** (adds new columns and tables):
```bash
python init_postgres.py
```

2. **Run Application**:
```bash
python app.py
```

3. **Login as Admin**:
- Username: `admin`
- Password: `Admin@123`
- The admin user is automatically created with admin privileges

### Access Admin Panel

1. Login as admin
2. Click "Admin Panel" button in dashboard (red button)
3. Or navigate to: `http://localhost:5000/admin`

### Toggle Email Confirmation

1. Go to Admin Panel
2. Find "Email Confirmation Requirement" setting
3. Click the toggle button
4. Status changes immediately:
   - **ENABLED** (green): Users must confirm email
   - **DISABLED** (red): Users can login immediately

### Make a User Admin

1. Go to Admin Panel
2. Scroll to "User Management" section
3. Find the user in the table
4. Click "Make Admin" button
5. User now has admin privileges

### Remove Admin Privileges

1. Go to Admin Panel
2. Find the admin user in the table
3. Click "Remove Admin" button
4. Note: You cannot remove your own admin privileges

## Database Changes

### New Columns
- `user.is_admin` (BOOLEAN) - Identifies admin users

### New Tables
- `system_settings` - Stores system-wide settings
  - `setting_key` - Setting identifier
  - `setting_value` - Setting value
  - `description` - Setting description
  - `updated_at` - Last update timestamp

## Default Settings

### Email Confirmation
- **Key**: `require_email_confirmation`
- **Default Value**: `false`
- **Description**: Require users to confirm email before login

## User Experience

### For Normal Users (Email Confirmation Disabled)
1. Register with username, email, password
2. Login immediately ✅
3. No email confirmation needed
4. Start using the app right away

### For Normal Users (Email Confirmation Enabled)
1. Register with username, email, password
2. Receive confirmation link (shown in flash message for testing)
3. Click confirmation link
4. Now can login ✅

### For Admin Users
1. Login as admin
2. Access Admin Panel
3. Control system settings
4. Manage users
5. View statistics

## Security Notes

### Admin Access Control
- Only users with `is_admin=True` can access admin panel
- Attempting to access without admin privileges redirects to dashboard
- Admin status is checked on every admin route

### Email Confirmation
- When disabled: Users can login immediately (easier onboarding)
- When enabled: Users must confirm email (more secure)
- Setting applies to all new logins
- Existing logged-in users are not affected

### Admin Privileges
- Cannot remove your own admin privileges (prevents lockout)
- Admin users can make other users admins
- Admin users can remove admin privileges from others

## Testing

### Test Email Confirmation Toggle

1. **Disable Email Confirmation** (default):
```
- Register new user
- Login immediately ✅ (works)
```

2. **Enable Email Confirmation**:
```
- Admin: Toggle setting to "Enabled"
- Register new user
- Try to login ❌ (blocked - "Please confirm your email")
- Click confirmation link
- Login ✅ (works)
```

3. **Disable Again**:
```
- Admin: Toggle setting to "Disabled"
- Register new user
- Login immediately ✅ (works)
```

### Test Admin Functions

1. **Make User Admin**:
```
- Register normal user
- Admin: Click "Make Admin" on that user
- Logout and login as that user
- See "Admin Panel" button ✅
```

2. **Remove Admin**:
```
- Admin: Click "Remove Admin" on a user
- That user loses admin access
- "Admin Panel" button disappears
```

## API Changes

### New Routes
- `GET /admin` - Admin panel page (admin only)
- `POST /admin/toggle-email-confirmation` - Toggle email confirmation (admin only)
- `POST /admin/make-admin/<user_id>` - Make user admin (admin only)
- `POST /admin/remove-admin/<user_id>` - Remove admin privileges (admin only)

### Updated Routes
- `POST /login` - Now checks if email confirmation is required before blocking

## Files Modified

### Backend
- `models.py` - Added `SystemSettings` model and `is_admin` field
- `app.py` - Added admin routes and `admin_required` decorator
- `auth.py` - Updated login to check email confirmation setting
- `init_postgres.py` - Added `is_admin` column and `system_settings` table

### Frontend
- `templates/admin_panel.html` - New admin panel interface
- `templates/dashboard.html` - Added admin panel link for admins

## Troubleshooting

### "Admin access required" error
- You're not logged in as admin
- Login with admin account or ask an admin to make you admin

### Email confirmation still required after disabling
- Logout and login again
- Clear browser cache
- Check admin panel shows "DISABLED"

### Cannot access admin panel
- Make sure you're logged in
- Make sure your user has `is_admin=True`
- Check database: `SELECT is_admin FROM "user" WHERE username='your_username';`

### Admin panel link not showing
- Make sure you're logged in as admin
- Refresh the page
- Check if `is_admin` is True in database

## Production Recommendations

### Security
- Change default admin password immediately
- Use strong passwords for admin accounts
- Limit number of admin users
- Monitor admin actions in logs
- Consider adding 2FA for admin accounts

### Settings
- Enable email confirmation for production (more secure)
- Set up real email server (not just flash messages)
- Configure proper email templates
- Add email rate limiting

### Monitoring
- Log all admin actions
- Monitor setting changes
- Alert on suspicious admin activity
- Regular security audits

## Future Enhancements

Possible additions:
- More system settings (rate limits, session timeout, etc.)
- User deletion by admin
- User password reset by admin
- Bulk user operations
- Activity logs viewer
- Email template editor
- Role-based permissions (beyond just admin/user)

---

**Note**: Email confirmation is now optional and controlled by admins. This makes it easy for normal users to login while still providing security when needed!
