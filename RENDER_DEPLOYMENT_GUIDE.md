# Render Deployment Guide for HR Portal

This guide explains how to deploy your HR Portal application to Render, a cloud platform that provides a free tier for web applications.

## Why Render?

- Generous free tier with 100GB bandwidth/month
- Easy GitHub integration
- Automatic SSL certificates
- Built-in PostgreSQL database option
- Automatic deploys from Git commits
- Global CDN for static assets

## Prerequisites

1. A GitHub repository with your HR Portal code
2. A Render account (sign up at https://render.com)

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. Make sure your project is in a GitHub repository
2. Ensure all the following files are in your repository:
   - `manage.py` (in the root of your repo)
   - `requirements.txt` (in the root of your repo)
   - `hr_project/settings.py` (Django settings)
   - `hr_project/wsgi.py` (WSGI configuration)
   - `Dockerfile` (created for Render deployment)
   - `render.yaml` (Render service specification)
   - All your application code

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Sign up using your GitHub account
3. Authorize Render to access your repositories

### Step 3: Create a New Web Service

1. From your Render dashboard, click "New +" and select "Web Service"
2. Connect your GitHub account if prompted
3. Select your HR Portal repository
4. Choose the branch you want to deploy (typically "main" or "master")

### Step 4: Configure the Web Service

#### Basic Configuration:
- **Environment**: Python
- **Branch**: main (or your default branch)
- **Root Directory**: Leave empty (if your project root contains manage.py)

#### Build Settings:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn hr_project.wsgi:application --bind 0.0.0.0:$PORT`

#### Environment Variables:
Click "Advanced" to add environment variables:

```
KEY: DEBUG
VALUE: False

KEY: SECRET_KEY
VALUE: [click "Generate" or enter a long random string]

KEY: EMAIL_HOST_USER
VALUE: hamzamarwat46@gmail.com

KEY: EMAIL_HOST_PASSWORD
VALUE: your-gmail-app-password

KEY: OPENAI_API_KEY
VALUE: your-openai-api-key-if-using-ai-features
```

> **Important**: For SECRET_KEY, EMAIL_HOST_PASSWORD, and OPENAI_API_KEY, click the lock icon to keep these values encrypted.

### Step 5: Set Up a Database (Optional but Recommended)

If you want to use a PostgreSQL database instead of SQLite:

1. From your Render dashboard, click "New +" and select "PostgreSQL"
2. Give your database a name (e.g., "hr-portal-db")
3. Set a database password (click the lock icon to encrypt)
4. After creation, copy the External Database URL

Then go back to your web service settings and add an environment variable:
```
KEY: DATABASE_URL
VALUE: [the external database URL you copied]
```

### Step 6: Deploy

1. Click "Create Web Service"
2. Render will start building your application (this may take a few minutes)
3. You'll see the build logs in real-time
4. Once complete, your application will be deployed at a URL like:
   `https://your-service-name.onrender.com`

### Step 7: Run Initial Setup Commands

After the first successful deployment, you'll need to run Django management commands:

1. Go to your web service dashboard
2. Click on "Manual Deploy" → "Run without deploying" 
3. Run the following commands one by one:

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

### Step 8: Access Your Application

Visit your application at the URL provided by Render (e.g., `https://your-service-name.onrender.com`)

Log in using the superuser credentials you created.

## Important Notes

- **Free Tier Limitations**: Render's free tier sleeps after 15 minutes of inactivity and takes a few seconds to wake up
- **Database**: If using the free PostgreSQL instance, it has a 10,000 row limit
- **Build Time**: The first build may take 5-10 minutes as it installs all dependencies
- **Environment Variables**: Never commit sensitive information like passwords or API keys to your repository

## Troubleshooting

### Application won't start
- Check the logs in your Render dashboard
- Verify your start command is correct
- Ensure all dependencies are in requirements.txt

### Database issues
- If switching from SQLite to PostgreSQL, make sure you've run migrations
- Check that your DATABASE_URL is properly formatted

### Static files not loading
- Verify that collectstatic was run after deployment
- Check that your Django settings have proper static file configuration

## Updating Your Application

After making changes to your code:
1. Commit and push to your GitHub repository
2. Render will automatically detect the changes and deploy a new version
3. Monitor the build logs to ensure the deployment succeeds

## Scaling Beyond Free Tier

When your application grows, Render offers paid plans with:
- More CPU and RAM
- Increased storage
- Better performance
- Custom domains
- Zero downtime deploys