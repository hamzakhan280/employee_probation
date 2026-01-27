# Google Cloud Platform (Cloud Run) Deployment Guide for HR Portal

This guide explains how to deploy your HR Portal application to Google Cloud Platform using Cloud Run, which offers a generous free tier.

## Why Google Cloud Platform (Cloud Run)?

- Generous free tier: 2 million requests/month, 360 CPU hours/month, 1 GB storage
- Reliable infrastructure from Google
- Easy scaling based on demand
- Integrated with other Google Cloud services
- Custom domain support
- Robust security features

## Prerequisites

1. A Google Cloud Platform account (requires credit card for verification, but many services remain free)
2. A GitHub repository with your HR Portal code
3. Google Cloud SDK installed locally (optional but recommended)

## Step-by-Step Deployment

### Step 1: Set Up Google Cloud Account

1. Go to https://console.cloud.google.com/
2. Create a new Google Cloud account (requires credit card for verification)
3. Create a new project or select an existing one
4. Enable billing for the project (required even for free tier usage)

### Step 2: Enable Required APIs

1. In your Google Cloud Console, go to "APIs & Services" → "Library"
2. Enable the following APIs:
   - Cloud Run API
   - Artifact Registry API
   - Cloud Build API

### Step 3: Prepare Your Repository

1. Make sure your project is in a GitHub repository
2. Ensure all the following files are in your repository:
   - `manage.py` (in the root of your repo)
   - `requirements.txt` (in the root of your repo)
   - `hr_project/settings.py` (Django settings)
   - `hr_project/wsgi.py` (WSGI configuration)
   - `Dockerfile` (created for containerization)
   - All your application code

### Step 4: Configure Your Django Application

Update your Django settings to work in a containerized environment:

1. In `settings.py`, ensure you have:
   - Proper ALLOWED_HOSTS configuration
   - Environment variable-based configuration
   - Database configuration for production

Example settings for GCP:
```python
import os
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

# Detect if running on Google Cloud
ON_GCP = os.getenv('K_SERVICE') is not None

if ON_GCP:
    # Production settings for Google Cloud
    DEBUG = False
    
    # Use Cloud SQL proxy if connecting to Cloud SQL
    if os.getenv('CLOUD_SQL_CONNECTION_NAME'):
        # Configure for Cloud SQL
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': f'/cloudsql/{os.getenv("CLOUD_SQL_CONNECTION_NAME")}',
                'USER': os.getenv('DB_USER'),
                'PASSWORD': os.getenv('DB_PASS'),
                'NAME': os.getenv('DB_NAME'),
            }
        }
    else:
        # Use environment variable for database URL
        import dj_database_url
        DATABASES = {
            'default': dj_database_url.config(
                default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
            )
        }
else:
    # Local development settings
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Allow all hosts in Cloud Run
ALLOWED_HOSTS = ['*']
```

### Step 5: Create a Cloud Build Configuration

Create a `cloudbuild.yaml` file in your repository:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/hr-portal', '.']
  
  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/hr-portal']
  
  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'hr-portal'
      - '--image'
      - 'gcr.io/$PROJECT_ID/hr-portal'
      - '--region'
      - 'us-central1'
      - '--port'
      - '8080'
      - '--set-env-vars'
      - 'DEBUG=False'
      - '--set-secrets'
      - 'SECRET_KEY=SECRET_KEY:latest,EMAIL_HOST_USER=EMAIL_HOST_USER:latest,EMAIL_HOST_PASSWORD=EMAIL_HOST_PASSWORD:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest'
      - '--allow-unauthenticated'
      - '--platform'
      - 'managed'
images:
  - 'gcr.io/$PROJECT_ID/hr-portal'
```

### Step 6: Set Up Secret Manager (Recommended)

1. In Google Cloud Console, go to "Security" → "Secret Manager"
2. Create the following secrets:
   - SECRET_KEY
   - EMAIL_HOST_USER
   - EMAIL_HOST_PASSWORD
   - OPENAI_API_KEY

### Step 7: Deploy Using Cloud Build

1. In Google Cloud Console, go to "Cloud Build" → "Triggers"
2. Create a new trigger:
   - Name: "HR Portal Deploy"
   - Source: Your GitHub repository
   - Branch: `^main$` (or your default branch)
   - Configuration type: "Cloud Build configuration file"
   - Cloud Build configuration file location: `/cloudbuild.yaml`

### Step 8: Alternative - Deploy Directly from Console

1. In Google Cloud Console, go to "Cloud Run"
2. Click "Create Service"
3. Choose "Deploy one revision from an existing container image"
4. If you haven't built your image yet, select "Build from source":
   - Source repository: Your GitHub repository
   - Dockerfile path: `./Dockerfile`
5. Configure the service:
   - Container port: 8080
   - Uncheck "Allow unauthenticated invocations" if you want to restrict access
   - Set environment variables:
     - DEBUG: False
     - Other required variables
   - Set CPU allocation: 1 vCPU (minimum for Django)
   - Set Memory: 512 MB or more (recommended for Django)
   - Set maximum instances: 1 (to stay within free tier)

### Step 9: Configure Database (Optional but Recommended)

For production use, set up Cloud SQL:

1. In Google Cloud Console, go to "SQL"
2. Click "Create Instance" → "PostgreSQL"
3. Configure your instance with the free tier options
4. Create a database and user
5. Update your deployment to connect to Cloud SQL

### Step 10: Run Initial Setup Commands

After deployment, you'll need to run Django management commands:

1. Use Cloud Shell or local gcloud CLI:
```bash
gcloud run jobs execute --region=us-central1 --project=YOUR_PROJECT_ID --command="python,manage.py,migrate" hr-portal-job
```

Or alternatively, temporarily enable Cloud Shell SSH access and run:
```bash
# SSH into Cloud Shell
gcloud run services update hr-portal --add-cloudsql-instances=YOUR_INSTANCE_CONNECTION_NAME --region=us-central1

# Run management commands
gcloud run services update hr-portal --set-env-vars="COMMAND=migrate" --region=us-central1
```

More commonly, you'd run these commands locally after setting up the database connection, or use Cloud Functions/Cloud Run Jobs.

### Step 11: Access Your Application

1. In Cloud Run, find your service URL
2. Visit your application at the provided URL
3. Log in using the superuser credentials you created

## Important Notes

- **Free Tier Limitations**: GCP free tier includes 2 million requests/month, 360 CPU hours/month, and 5 GB storage
- **Billing**: Requires credit card verification, but staying within free tier limits keeps costs at $0
- **Build Time**: The first build may take 5-10 minutes as it builds the container
- **Environment Variables**: Use Secret Manager for sensitive information

## Troubleshooting

### Application won't start
- Check the logs in Cloud Run → Logs
- Verify your container listens on port 8080
- Ensure all dependencies are in requirements.txt

### Database issues
- If using Cloud SQL, verify connection settings
- Check that your database user has proper permissions

### High resource usage
- Monitor your usage in the Google Cloud Console
- Adjust instance settings to stay within free tier limits

## Updating Your Application

After making changes to your code:
1. Commit and push to your GitHub repository
2. If using triggers, Cloud Build will automatically rebuild and redeploy
3. Monitor the build logs to ensure the deployment succeeds

## Scaling Beyond Free Tier

When your application grows, GCP offers:
- Higher compute resources
- More storage
- Advanced networking options
- Premium support
- Custom SLAs