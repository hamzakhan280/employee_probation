# Railway Deployment Guide

## Deploying the HR Portal to Railway

### Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub account (Railway connects to GitHub for deployment)

### Steps to Deploy

1. **Sign Up/Log In to Railway**
   - Go to https://railway.app
   - Sign up or log in to your account

2. **Create a New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your HR Portal repository

3. **Configure the Project**
   - On the "Variables" tab, add the following environment variables:
     - `SECRET_KEY`: Generate a strong secret key
     - `DEBUG`: Set to `False` for production
     - `EMAIL_HOST_USER`: Your email address for sending notifications
     - `EMAIL_HOST_PASSWORD`: Your email app password
     - `ALLOWED_HOSTS`: Your railway domain (e.g., `your-project-name.up.railway.app`)

4. **Set Build and Start Commands**
   - Go to the "Settings" tab
   - Under "Build Configuration":
     - Build Command: `pip install -r requirements.txt`
   - Under "Deploy Configuration":
     - Start Command: `python manage.py migrate && gunicorn hr_project.wsgi:application`

5. **Deploy**
   - Click "Deploy" to start the deployment process
   - Monitor the deployment logs in the "Logs" tab

### Post-Deployment Steps

1. **Run Initial Setup**
   - After deployment, you may need to run initial setup commands
   - Use the Railway console to run: `python manage.py migrate`
   - Create a superuser: `python manage.py createsuperuser`

2. **Access Your Application**
   - Your application will be available at the domain provided by Railway
   - Access the admin panel at `/admin/`
   - Main application at the root URL

### Environment Variables Reference

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST_USER`: Email address for sending notifications
- `EMAIL_HOST_PASSWORD`: App password for email account
- `DATABASE_URL`: PostgreSQL database URL (provided by Railway if using their database)

### Troubleshooting

- If you encounter issues with static files, make sure to run `collectstatic` after deployment
- Check logs regularly for any errors during deployment or runtime
- Ensure all required environment variables are set correctly

### Scaling

- Railway allows you to scale your application based on traffic needs
- Adjust instance size in the "Settings" tab as needed