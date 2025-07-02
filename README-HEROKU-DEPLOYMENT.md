# Leek Heroku Docker Deployment

This repository has been configured for deploying Leek (Celery monitoring tool) to Heroku using Docker with full web UI support.

## 🎯 What's Included

### Docker Configuration
- **`heroku.yml`**: Heroku container deployment configuration
- **`app/dockers/Dockerfile.heroku`**: Heroku-optimized Docker image
- **`app/conf/supervisord-heroku.conf`**: Process management for Heroku
- **`app/bin/start-nginx-heroku.sh`**: Dynamic nginx configuration for Heroku

### Deployment Scripts
- **`heroku-setup.sh`**: Interactive setup script for Heroku app and environment (with duplicate prevention)
- **`quick-deploy.sh`**: One-command setup and deployment
- **`cleanup-duplicate-addons.sh`**: Cleanup script to remove duplicate addons and optimize costs
- **`heroku-deploy-guide.md`**: Detailed deployment guide

### 🛡️ Addon Duplicate Prevention
All deployment scripts include smart checks to:
- ✅ Detect existing Bonsai Elasticsearch addons before creating new ones
- ✅ Warn about unnecessary Redis addons (we use your existing Redis)
- ✅ Prevent duplicate addon costs and configuration conflicts
- ✅ Show clear status messages about what's being created vs. reused

## 🚀 Quick Start

### Option 1: Quick Deployment (Recommended)
```bash
# Make scripts executable
chmod +x heroku-setup.sh quick-deploy.sh

# Run the quick deployment script
./quick-deploy.sh
```

### Option 2: Step-by-Step
```bash
# 1. Setup Heroku app and environment
chmod +x heroku-setup.sh
./heroku-setup.sh

# 2. Deploy
git add .
git commit -m "Deploy Leek"
git push heroku-leek main

# 3. Scale
heroku ps:scale web=1 --app your-app-name
```

## 📋 Prerequisites

Before running the deployment:

1. **Heroku CLI** installed and logged in
2. **Firebase Project** set up with:
   - Google Authentication enabled
   - Web app registered
   - Configuration values ready (API key, project ID, etc.)
3. **Redis URL** from your existing Heroku app (`funly-manage-test`)

## 🏗️ Architecture

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
```

## 🔧 Components

### API Server (Port 5000)
- Flask REST API for Leek
- Handles authentication via Firebase
- Stores data in Elasticsearch (Bonsai addon)

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

## 🎛️ Environment Variables

Key environment variables set during deployment:

```bash
# Components
LEEK_ENABLE_API=true
LEEK_ENABLE_AGENT=true
LEEK_ENABLE_WEB=true

# Firebase Authentication
LEEK_FIREBASE_PROJECT_ID=your-project-id
LEEK_FIREBASE_API_KEY=your-api-key
LEEK_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
LEEK_FIREBASE_APP_ID=your-app-id

# Data Storage
LEEK_ES_URL=<from-bonsai-addon>

# Broker Integration
LEEK_AGENT_SUBSCRIPTIONS=[{...}]  # Redis connection for Celery events
```

## 📱 Accessing Leek

Once deployed:
1. Visit `https://your-app-name.herokuapp.com`
2. Sign in with Google (Firebase auth)
3. Create an application to start monitoring

## 🔍 Monitoring Your Celery Workers

To enable monitoring of your existing Celery workers in `funly-manage-test`:

```python
# In your Celery configuration
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True  
app.conf.task_track_started = True
```

## 💰 Cost Estimation

- **Bonsai Elasticsearch (Sandbox)**: **FREE** for development/testing
- **Bonsai Elasticsearch (Staging)**: ~$15/month for production
- **Single Web Dyno**: ~$7/month (Standard-1X)  
- **Redis**: **FREE** (using your existing Redis from `funly-manage-test`)

**Total**: ~$7-22/month depending on Elasticsearch plan

## 🐛 Troubleshooting

### Check Logs
```bash
heroku logs --tail --app your-app-name
```

### Common Issues
1. **Bootstrap fails**: Check Elasticsearch connectivity
2. **Agent not connecting**: Verify Redis URL and Celery events enabled
3. **Auth issues**: Check Firebase configuration and authorized domains

### Restart Services
```bash
heroku restart --app your-app-name
```

### Clean Up Duplicate Addons
If you accidentally created duplicate addons, use the cleanup script:
```bash
chmod +x cleanup-duplicate-addons.sh
./cleanup-duplicate-addons.sh
```

This script will:
- ✅ Analyze your current addon setup
- ✅ Identify duplicate or unnecessary addons  
- ✅ Help you remove them safely
- ✅ Show cost optimization recommendations

## 📚 Additional Resources

- **Detailed Guide**: See `heroku-deploy-guide.md`
- **Leek Documentation**: https://tryleek.com/docs/
- **Firebase Setup**: https://tryleek.com/docs/getting-started/firebase

## 🤝 Support

If you encounter issues:
1. Check the deployment guide
2. Review Heroku logs
3. Verify Firebase configuration
4. Ensure Celery workers are sending events 