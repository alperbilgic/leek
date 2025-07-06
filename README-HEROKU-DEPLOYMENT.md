# Leek Heroku Docker Deployment

This repository has been configured for deploying Leek (Celery monitoring tool) to Heroku using Docker with **Searchbox Elasticsearch** and full web UI support.

## 🎯 What's Included

### Docker Configuration
- **`heroku.yml`**: Heroku container deployment configuration
- **`Dockerfile`**: Heroku-optimized Docker image with Searchbox support
- **`app/conf/supervisord-heroku.conf`**: Process management for Heroku
- **`app/bin/start-nginx-heroku.sh`**: Dynamic nginx configuration for Heroku

### Deployment Scripts
- **`heroku-setup.sh`**: Interactive setup script for Heroku app with Searchbox addon
- **`quick-deploy.sh`**: One-command setup and deployment
- **`heroku-deploy-guide.md`**: Detailed deployment guide

### 🔍 Searchbox Elasticsearch Integration
All deployment scripts include:
- ✅ Automatic Searchbox addon provisioning
- ✅ Persistent data storage configuration
- ✅ Professional monitoring and alerting
- ✅ Optimized settings for managed Elasticsearch
- ✅ Dashboard access for data management

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
# 1. Setup Heroku app with Searchbox
chmod +x heroku-setup.sh
./heroku-setup.sh

# 2. Deploy
git add .
git commit -m "Deploy Leek with Searchbox"
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
                    │
                    ▼
        ┌─────────────────────────┐
        │ Searchbox Elasticsearch │
        │ (Managed Service)       │
        └─────────────────────────┘
```

## 🔧 Components

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

# Searchbox Data Storage
LEEK_ES_URL=<from-searchbox-addon>
LEEK_ES_IM_ENABLE=false
LEEK_ES_INDEX_CLEANUP_ENABLED=false
LEEK_CLEAN_DATABASE_ON_STARTUP=false

# Broker Integration
LEEK_AGENT_SUBSCRIPTIONS=[{...}]  # Redis connection for Celery events
```

## 📱 Accessing Leek

Once deployed:
1. Visit `https://your-app-name.herokuapp.com`
2. Sign in with Google (Firebase auth)
3. Create an application to start monitoring

## 📊 Accessing Searchbox Dashboard

```bash
# Open Searchbox dashboard
heroku addons:open searchbox --app your-app-name

# Check Searchbox status
heroku addons:info searchbox --app your-app-name
```

Dashboard features:
- 🔍 **Search and query** your Elasticsearch data
- 📈 **Performance metrics** and monitoring
- 🔧 **Index management** and settings
- 📊 **Usage statistics** and analytics
- 🚨 **Alerts and notifications**

## 🔍 Monitoring Your Celery Workers

To enable monitoring of your existing Celery workers in `funly-manage-test`:

```python
# In your Celery configuration
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True  
app.conf.task_track_started = True
```

## 💰 Cost Estimation

- **Searchbox Elasticsearch (Starter)**: $9/month
- **Single Web Dyno**: ~$7/month (Standard-1X)  
- **Redis**: **FREE** (using your existing Redis from `funly-manage-test`)

**Total**: ~$16/month

## 🐛 Troubleshooting

### Check Logs
```bash
heroku logs --tail --app your-app-name
```

### Common Issues
1. **Bootstrap fails**: Check Searchbox connectivity
2. **Agent not connecting**: Verify Redis URL and Celery events enabled
3. **Auth issues**: Check Firebase configuration and authorized domains
4. **Data not persisting**: Verify Searchbox URL configuration

### Restart Services
```bash
heroku restart --app your-app-name
```

### Searchbox Issues
```bash
# Check Searchbox status
heroku addons:info searchbox --app your-app-name

# Access Searchbox dashboard
heroku addons:open searchbox --app your-app-name

# Test connectivity
curl -s "$(heroku config:get SEARCHBOX_URL --app your-app-name)"
```

## 🎯 Benefits of This Architecture

- **Persistent Data**: Searchbox ensures data survives app restarts
- **Managed Service**: No Elasticsearch maintenance required
- **Professional Monitoring**: Searchbox dashboard for analytics
- **Cost-Effective**: Single dyno deployment with external storage
- **Scalable**: Easy to scale both app and Elasticsearch independently
- **Reliable**: Managed services with SLA guarantees

## 📚 Additional Resources

- **Detailed Guide**: See `heroku-deploy-guide.md`
- **Searchbox Guide**: See `SEARCHBOX_DEPLOYMENT_GUIDE.md`
- **Leek Documentation**: https://tryleek.com/docs/
- **Firebase Setup**: https://tryleek.com/docs/getting-started/firebase
- **Searchbox Documentation**: https://elements.heroku.com/addons/searchbox

## 🤝 Support

If you encounter issues:
1. Check the deployment guide
2. Review Heroku logs
3. Verify Firebase configuration
4. Ensure Celery workers are sending events
5. Check Searchbox dashboard for Elasticsearch issues 