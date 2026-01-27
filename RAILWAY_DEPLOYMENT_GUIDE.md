# Railway Deployment Guide for HR Portal

This guide explains how to deploy your HR Portal application to Railway, a modern cloud platform that provides a free tier for web applications.

## Why Railway?

- Generous free tier with 500 free hours/month
- Modern developer experience
- Easy environment variable management
- Built-in database options
- Git-based deployments
- Great for developers who want a modern workflow

## Prerequisites

1. A GitHub repository with your HR Portal code
2. A Railway account (sign up at https://railway.app)

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. Make sure your project is in a GitHub repository
2. Ensure all the following files are in your repository:
   - `manage.py` (in the root of your repo)
   - `requirements.txt` (in the root of your repo)
   - `hr_project/settings.py` (Django settings)
   - `hr_project/wsgi.py` (WSGI configuration)
   - All your application code

### Step 2: Sign Up for Railway

1. Go to https://railway.app
2. Sign up using your GitHub account
3. Install the Railway GitHub app when prompted

### Step 3: Create a New Project

1. From your Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your HR Portal repository
4. Select the branch you want to deploy (typically "main" or "master")

### Step 4: Configure the Project

#### Build & Deploy Settings:
Railway will automatically detect that this is a Python project.

#### Variables Configuration:
Go to the "Variables" tab and add the following environment variables:

```
DEBUG=False
SECRET_KEY=your_very_long_random_secret_key_here_much_longer_than_this_example
EMAIL_HOST_USER=hamzamarwat46@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
OPENAI_API_KEY=your-openai-api-key-if-using-ai-features
```

> **Important**: For SECRET_KEY, EMAIL_HOST_PASSWORD, and OPENAI_API_KEY, make sure to toggle them as "Secret" so they're not visible.

### Step 5: Set Up a Database (Optional but Recommended)

1. From your project dashboard, click "+ New" → "Database"
2. Select "PostgreSQL" (or another database option)
3. Choose "Provision from scratch"
4. Give your database a name and provision it

After the database is created, Railway will automatically inject database connection variables into your application.

### Step 6: Configure Django Settings for Railway

You'll need to update your Django settings to work with Railway's database. In your `settings.py`, make sure you have the database configuration that handles Railway's injected environment variables:

```python
import os
import dj_database_url

# Database configuration for Railway
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Local development settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

### Step 7: Configure Static Files

Railway doesn't serve static files directly, so you'll need to:

1. Enable WhiteNoise in your Django settings (which your project already has)
2. Make sure `whitenoise.middleware.WhiteNoiseMiddleware` is in your middleware

### Step 8: Deploy

1. Railway will automatically build and deploy your application
2. You'll see the build logs in real-time
3. Once complete, your application will be deployed at a URL like:
   `https://your-project-name.up.railway.app`

### Step 9: Run Initial Setup Commands

After the first successful deployment, you'll need to run Django management commands:

1. In your Railway project dashboard, go to "Deployments"
2. Click on the most recent deployment
3. Click "Configure" and then "Run command"
4. Run the following commands one by one:

```bash
python manage.py migrate
```

```bash
python manage.py collectstatic --noinput
```

```bash
python manage.py createsuperuser
```

For the createsuperuser command, you'll need to provide:
- Username
- Email address
- Password (entered twice)

### Step 10: Access Your Application

Visit your application at the URL provided by Railway (e.g., `https://your-project-name.up.railway.app`)

Log in using the superuser credentials you created.

## Important Notes

- **Free Tier Limitations**: Railway's free tier has 500 free hours per month and goes to sleep after 5 minutes of inactivity
- **Database**: If using Railway's PostgreSQL, it has a 100MB storage limit on the free tier
- **Build Time**: The first build may take 5-10 minutes as it installs all dependencies
- **Environment Variables**: Never commit sensitive information like passwords or API keys to your repository

## Troubleshooting

### Application won't start
- Check the logs in your Railway dashboard
- Verify your start command is correct (should be handled automatically)
- Ensure all dependencies are in requirements.txt

### Database issues
- If using Railway's database, make sure you've configured dj_database_url properly
- Check that your DATABASE_URL is properly formatted

### Static files not loading
- Verify that collectstatic was run after deployment
- Check that your Django settings have proper static file configuration with WhiteNoise

## Updating Your Application

After making changes to your code:
1. Commit and push to your GitHub repository
2. Railway will automatically detect the changes and deploy a new version
3. Monitor the build logs to ensure the deployment succeeds

## Scaling Beyond Free Tier

When your application grows, Railway offers paid plans with:
- More compute hours
- Increased storage
- Better performance
- Custom domains
- Zero downtime deploys
- More concurrent connections