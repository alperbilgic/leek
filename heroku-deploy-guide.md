# Leek Heroku Docker Deployment Guide

This guide will help you deploy Leek to Heroku using Docker with Searchbox Elasticsearch, Firebase authentication, Redis broker integration, and the full web UI.

## Prerequisites

1. Heroku CLI installed
2. A Heroku account
3. A Google Firebase project
4. Redis connection details from your existing Heroku app

## Step 1: Firebase Setup

### 1.1 Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or use an existing project
3. Enable Google Analytics (optional)

### 1.2 Enable Authentication
1. In your Firebase project, go to "Authentication" → "Sign-in method"
2. Enable "Google" sign-in provider
3. Add your domain to authorized domains (you'll get this after Heroku deployment)

### 1.3 Register Web App
1. Go to Project Settings (gear icon)
2. Click "Add app" → Web app
3. Register app with a name (e.g., "leek-heroku")
4. Copy the Firebase configuration values:
   - `apiKey`
   - `authDomain` 
   - `projectId`
   - `appId`

### 1.4 Set up Service Account (for server-side auth)
1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save the JSON file securely (you'll need the project ID)

## Step 2: Heroku App Creation

### 2.1 Create New Heroku App
```bash
# Create new app for Leek with container stack
heroku create funly-manage-test-leek
heroku stack:set container --app funly-manage-test-leek

# Check for existing addons to avoid duplicates
heroku addons --app funly-manage-test-leek
```

### 2.2 Add Searchbox Elasticsearch
```bash
# Add Searchbox Elasticsearch addon
heroku addons:create searchbox:starter --app funly-manage-test-leek

# Wait for addon to be provisioned
heroku addons:wait searchbox --app funly-manage-test-leek

# Verify addon is ready
heroku addons:info searchbox --app funly-manage-test-leek
```

### 2.3 Get Redis Connection Details
Get your Redis URL from your existing app:
```bash
heroku config:get REDIS_URL --app funly-manage-test
```

## Step 3: Environment Configuration

Set the following environment variables on your Heroku app:

```bash
# Basic Configuration
heroku config:set LEEK_API_LOG_LEVEL=INFO --app funly-manage-test-leek
heroku config:set LEEK_AGENT_LOG_LEVEL=INFO --app funly-manage-test-leek
heroku config:set LEEK_ENABLE_API=true --app funly-manage-test-leek
heroku config:set LEEK_ENABLE_AGENT=true --app funly-manage-test-leek
heroku config:set LEEK_ENABLE_WEB=true --app funly-manage-test-leek

# Authentication Configuration
heroku config:set LEEK_API_ENABLE_AUTH=true --app funly-manage-test-leek
heroku config:set LEEK_FIREBASE_PROJECT_ID=your-project-id --app funly-manage-test-leek
heroku config:set LEEK_FIREBASE_API_KEY=your-api-key --app funly-manage-test-leek
heroku config:set LEEK_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com --app funly-manage-test-leek
heroku config:set LEEK_FIREBASE_APP_ID=your-app-id --app funly-manage-test-leek

# Authorization (replace with your email domain)
heroku config:set LEEK_API_OWNER_ORG=yourdomain.com --app funly-manage-test-leek
heroku config:set LEEK_API_WHITELISTED_ORGS=yourdomain.com --app funly-manage-test-leek

# URLs (will be set after deployment)
heroku config:set LEEK_API_URL=https://funly-manage-test-leek.herokuapp.com --app funly-manage-test-leek
heroku config:set LEEK_WEB_URL=https://funly-manage-test-leek.herokuapp.com --app funly-manage-test-leek

# Elasticsearch URL (from Searchbox addon)
heroku config:set LEEK_ES_URL=$(heroku config:get SEARCHBOX_URL --app funly-manage-test-leek) --app funly-manage-test-leek

# Searchbox-optimized settings
heroku config:set LEEK_ES_IM_ENABLE=false --app funly-manage-test-leek
heroku config:set LEEK_ES_INDEX_CLEANUP_ENABLED=false --app funly-manage-test-leek
heroku config:set LEEK_CLEAN_DATABASE_ON_STARTUP=false --app funly-manage-test-leek

# Agent Configuration
heroku config:set LEEK_AGENT_API_SECRET=$(openssl rand -hex 32) --app funly-manage-test-leek

# Celery Broker Subscription (IMPORTANT: Replace with your actual Redis URL)
heroku config:set LEEK_AGENT_SUBSCRIPTIONS='[
  {
    "broker": "YOUR_REDIS_URL_HERE",
    "broker_management_url": "YOUR_REDIS_URL_HERE",
    "backend": null,
    "exchange": "celeryev",
    "queue": "leek.fanout",
    "routing_key": "#",
    "org_name": "yourdomain.com",
    "app_name": "funly-manage",
    "app_env": "prod",
    "prefetch_count": 1000,
    "concurrency_pool_size": 2,
    "batch_max_size_in_mb": 1,
    "batch_max_number_of_messages": 1000,
    "batch_max_window_in_seconds": 5
  }
]' --app funly-manage-test-leek
```

## Step 4: Configure Your Celery Workers

In your main app (`funly-manage-test`), ensure your Celery workers are configured to send events:

```python
# In your Celery configuration
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True
app.conf.task_track_started = True
```

## Step 5: Deploy to Heroku with Docker

```bash
# From the project root directory, initialize git if not already done
git init
git add .
git commit -m "Initial Leek Docker deployment with Searchbox"

# Add Heroku remote
heroku git:remote -a funly-manage-test-leek

# Deploy using Docker (heroku.yml will be used automatically)
git push heroku main
```

## Step 6: Scale Services

```bash
# Scale web dyno (includes API, Agent, and Web UI)
heroku ps:scale web=1 --app funly-manage-test-leek

# The bootstrap process runs automatically as a release task
# You can check logs to ensure it completed successfully
heroku logs --app funly-manage-test-leek
```

## Step 7: Update Firebase Authorized Domains

1. Go back to Firebase Console → Authentication → Settings
2. Add your Heroku app domain to authorized domains:
   - `funly-manage-test-leek.herokuapp.com`

## Step 8: Access Leek Web UI and Create Application

1. Visit your Leek web UI: `https://funly-manage-test-leek.herokuapp.com`
2. Sign in with your Google account (Firebase authentication)
3. Create a new application:
   - Organization: Your domain (e.g., `yourdomain.com`)
   - App Name: `funly-manage`
   - Environment: `prod`

The web UI provides:
- Real-time task monitoring
- Task statistics and analytics
- Worker performance metrics
- Task retry and control features
- Beautiful dashboards and charts

## Step 9: Access Searchbox Dashboard

```bash
# Open Searchbox dashboard
heroku addons:open searchbox --app funly-manage-test-leek
```

The Searchbox dashboard provides:
- 🔍 **Search and query** your Elasticsearch data
- 📈 **Performance metrics** and monitoring
- 🔧 **Index management** and settings
- 📊 **Usage statistics** and analytics
- 🚨 **Alerts and notifications**

## Step 10: Verify Integration

1. In your main app, trigger some Celery tasks
2. Check the Leek dashboard to see if events are being received
3. Monitor logs: `heroku logs --tail --app funly-manage-test-leek`
4. Check Searchbox dashboard for data storage

## Architecture

The deployment creates:

```
┌─────────────────────────────────────────┐
│ Heroku Container (Single Dyno)         │
├─────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────────┐ │
│ │ Nginx   │ │ API     │ │ Agent       │ │
│ │ :$PORT  │ │ :5000   │ │ (Consumer)  │ │
│ └─────────┘ └─────────┘ └─────────────┘ │
├─────────────────────────────────────────┤
│ Web UI (Static Files)                   │
├─────────────────────────────────────────┤
│ Supervisord (Process Manager)           │
└─────────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────────┐
        │ Searchbox Elasticsearch │
        │ (Managed Service)       │
        └─────────────────────────┘
```

## Components

### API Server (Port 5000)
- Flask REST API for Leek
- Handles authentication via Firebase
- Stores data in Searchbox Elasticsearch

### Agent (Background Process)
- Consumes Celery events from Redis
- Forwards events to API for processing
- Monitors your existing Celery workers

### Web UI (Nginx)
- Beautiful React-based dashboard
- Real-time monitoring and analytics
- Task management and control

### Reverse Proxy (Nginx on $PORT)
- Routes `/v1/*` → API server
- Routes `/*` → Static web files
- Handles Firebase config injection

### Searchbox Elasticsearch
- Persistent data storage
- Managed Elasticsearch service
- Professional monitoring and alerting

## Troubleshooting

### Common Issues

1. **Searchbox Connection Issues**
   - Check if addon is provisioned: `heroku addons:info searchbox --app your-app-name`
   - Verify Searchbox URL: `heroku config:get SEARCHBOX_URL --app your-app-name`
   - Test connectivity: `curl -s "$(heroku config:get SEARCHBOX_URL --app your-app-name)"`

2. **Authentication Issues**
   - Verify Firebase configuration
   - Check authorized domains in Firebase console
   - Ensure email domain matches `LEEK_API_OWNER_ORG`

3. **Agent Not Receiving Events**
   - Verify Redis URL is correct
   - Check that Celery workers have events enabled
   - Monitor agent logs for connection errors

### Useful Commands

```bash
# Check app status
heroku ps --app funly-manage-test-leek

# View logs
heroku logs --tail --app funly-manage-test-leek

# Restart app
heroku restart --app funly-manage-test-leek

# Check config
heroku config --app funly-manage-test-leek

# Access Searchbox dashboard
heroku addons:open searchbox --app funly-manage-test-leek

# Check Searchbox status
heroku addons:info searchbox --app funly-manage-test-leek
```

## Security Notes

1. Keep your Firebase credentials secure
2. Use environment variables for all sensitive data
3. Regularly rotate your `LEEK_AGENT_API_SECRET`
4. Monitor access logs in Firebase Console
5. Use Searchbox dashboard for Elasticsearch monitoring

## Cost Considerations

- Searchbox Elasticsearch (Starter): **$9/month**
- Single web dyno: ~$7/month (Standard-1X)
- Redis: **FREE** (using your existing Redis from `funly-manage-test`)

Total estimated cost: ~$16/month

## Benefits of This Architecture

- **Persistent Data**: Searchbox ensures data survives app restarts
- **Managed Service**: No Elasticsearch maintenance required
- **Professional Monitoring**: Searchbox dashboard for analytics
- **Cost-Effective**: Single dyno deployment with external storage
- **Scalable**: Easy to scale both app and Elasticsearch independently
- **Reliable**: Managed services with SLA guarantees 