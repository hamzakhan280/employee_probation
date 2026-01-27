# HR Portal - Complete System Documentation

## Table of Contents
1. [Overview](#overview)
2. [Email Management System](#email-management-system)
3. [How to Manage Email Addresses](#how-to-manage-email-addresses)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Security Best Practices](#security-best-practices)

## Overview

The HR Portal is a comprehensive employee management system with a focus on probation tracking and document management. The system has been enhanced with a robust email management system that allows for dynamic department email configuration.

## Email Management System

### Key Features
- **Dynamic Department Management**: Departments and their email addresses are now stored in the database
- **Admin Interface**: Manage departments and emails through Django admin
- **Automatic Email Routing**: System automatically routes notifications to the correct department email
- **Fallback System**: If a department email isn't configured, falls back to HR email
- **Environment-Based Configuration**: Email settings are managed through environment variables

### Database Schema Changes
- Added `Department` model with fields: name, email, description
- Modified `Employee` model to link to Department via foreign key
- Preserved all existing employee data during migration

## How to Manage Email Addresses

### Method 1: Using Django Admin Interface (Recommended)

1. **Access the Admin Panel**
   - Navigate to `http://127.0.0.1:8000/admin/`
   - Log in with your admin credentials

2. **Navigate to Departments**
   - In the admin panel, find and click on "Departments" under the "Hr portal" section

3. **Add a New Department**
   - Click "ADD DEPARTMENT" button
   - Fill in the required fields:
     - **Name**: The name of the department (e.g., "Computer Science")
     - **Email**: The email address for the department head
     - **Description**: Optional description of the department
   - Click "SAVE"

4. **Edit Existing Department**
   - Click on the department name in the list
   - Update the email address or other information
   - Click "SAVE"

### Method 2: Using Management Command

1. **Run the Setup Command**
   ```bash
   python manage.py setup_departments
   ```
   This command will create default departments with placeholder email addresses.

2. **Manually Add Departments via Shell**
   ```bash
   python manage.py shell
   ```
   Then run:
   ```python
   from hr_portal.models import Department
   
   # Create a new department
   dept = Department.objects.create(
       name="New Department Name",
       email="hamzamarwat46@gmail.com",
       description="Description of the department"
   )
   ```

## Configuration

### Environment Variables (.env file)

Update your `.env` file with the following email configuration:

```
# Security
SECRET_KEY=your-secret-key-here-make-it-long-and-random
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=hamzamarwat46@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=hamzamarwat46@gmail.com

# HR email for notifications
HR_EMAIL=hamzamarwat46@gmail.com
```

### For Gmail Users:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Navigate to Security → App passwords
   - Generate a password for "Mail" and your device
   - Use this 16-character password in EMAIL_HOST_PASSWORD

### For Other Email Providers:
- **Outlook/Hotmail**: Use `smtp-mail.outlook.com` as EMAIL_HOST
- **Yahoo**: Use `smtp.mail.yahoo.com` as EMAIL_HOST
- **Custom SMTP**: Use your provider's SMTP server details

## How the Email System Works

1. **Department-Based Emails**: When sending notifications, the system first checks the Department model for the specific department's email address.

2. **Fallback System**: If a department doesn't have an email configured, the system falls back to the HR_EMAIL defined in settings.

3. **Dynamic Updates**: Changes to department emails in the admin panel take effect immediately without restarting the server.

4. **Probation Notifications**: The system automatically sends notifications to department heads when employees' probation periods are ending soon.

## Testing Email Configuration

To test if your email configuration is working:

1. **Using Django Shell**:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   
   send_mail(
       'Test Subject',
       'Test message.',
       'from@example.com',
       ['to@example.com'],
       fail_silently=False,
   )
   ```

2. **Using Admin Interface**:
   - Add a test department with your email
   - Trigger a probation notification from the dashboard
   - Check if the email is sent successfully

## Troubleshooting Common Issues

### Issue: Email authentication error
**Solution**: Verify your email credentials and ensure you're using an App Password for Gmail, not your regular password.

### Issue: Department emails not showing up
**Solution**: Make sure you've run migrations after updating the models:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Emails not sending
**Solution**: Check your email settings in the `.env` file and ensure your email provider allows sending emails via SMTP.

### Issue: Migration errors
**Solution**: If you encounter migration errors, try:
```bash
python manage.py migrate --fake-initial
```
Or reset the database (WARNING: This will delete all data):
```bash
python manage.py flush
```

## Security Best Practices

- Never commit your `.env` file to version control
- Use strong, unique passwords/App passwords
- Regularly review and rotate your email credentials
- Limit admin access to trusted personnel only
- Monitor email logs for any unauthorized usage
- Use HTTPS in production environments
- Keep Django and dependencies updated

## Updating Employee Records

When adding or updating employees, you can now assign them to departments that have email addresses configured:

1. Go to the Employees section in the admin panel
2. When creating or editing an employee, select the appropriate department from the dropdown
3. The system will automatically use that department's email for notifications

## Running the Application

To start the application:
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

Default login credentials:
- Username: admin
- Password: admin123

## Additional Management Commands

- `python manage.py setup_departments` - Creates default departments
- `python manage.py migrate` - Applies database migrations
- `python manage.py createsuperuser` - Creates a new admin user

## Support

For support, refer to the individual documentation files:
- EMAIL_MANAGEMENT_GUIDE.md - Detailed email management instructions
- EMAIL_CONFIGURATION.md - Email setup guide
- DEPLOYMENT_GUIDE.md - Deployment instructions for various platforms