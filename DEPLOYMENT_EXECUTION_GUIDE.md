# 🚀 Leek with Searchbox Deployment - Complete Execution Guide

This guide provides step-by-step instructions for deploying Leek with Searchbox Elasticsearch from scratch.

## ✅ **Requirements Checklist**

Before starting, ensure you have:

### 1. System Requirements
- [ ] **Heroku CLI** installed and configured
- [ ] **Git** installed
- [ ] **Terminal/Command Line** access
- [ ] **Heroku account** with billing enabled

### 2. External Services
- [ ] **Firebase project** created
- [ ] **Google Authentication** enabled in Firebase
- [ ] **Firebase web app** registered
- [ ] **Existing Django app** on Heroku with Redis

### 3. Configuration Data
- [ ] Firebase Project ID
- [ ] Firebase API Key  
- [ ] Firebase App ID
- [ ] Your email domain
- [ ] Redis URL from existing Django app

## 🎯 **Step-by-Step Execution**

### **Step 1: Prepare Your Environment**

```bash
# 1. Clone or navigate to your Leek directory
cd /path/to/your/leek

# 2. Verify Heroku CLI is working
heroku --version

# 3. Login to Heroku
heroku login

# 4. Make scripts executable
chmod +x heroku-setup.sh quick-deploy.sh
```

### **Step 2: Quick Deployment (Recommended)**

```bash
# Set your environment (optional)
export ENV=production  # or staging, test

# Run the automated deployment
./quick-deploy.sh
```

**What this does:**
1. ✅ Runs `heroku-setup.sh` interactively
2. ✅ Creates Heroku app with Searchbox addon
3. ✅ Configures all environment variables
4. ✅ Deploys Docker container to Heroku
5. ✅ Scales the application
6. ✅ Provides access URLs and next steps

### **Step 3: Manual Deployment (Alternative)**

If you prefer step-by-step control:

#### 3.1 Run Setup Script
```bash
./heroku-setup.sh
```

This will ask for:
- Heroku app name (e.g., `funly-manage-test-leek`)
- Original Django app name (e.g., `funly-manage-test`) 
- Firebase Project ID
- Firebase API Key
- Firebase App ID
- Your email domain

#### 3.2 Deploy to Heroku
```bash
# Commit changes
git add .
git commit -m "Deploy Leek with Searchbox"

# Push to Heroku
git push heroku-leek main
```

#### 3.3 Scale Application
```bash
# Scale web dyno
heroku ps:scale web=1 --app your-app-name
```

## 📊 **Verification Steps**

### **1. Check Deployment Status**
```bash
# Check app status
heroku ps --app your-app-name

# View logs
heroku logs --tail --app your-app-name

# Check release status
heroku releases --app your-app-name
```

### **2. Verify Searchbox Integration**
```bash
# Check Searchbox addon
heroku addons:info searchbox --app your-app-name

# Get Searchbox URL
heroku config:get SEARCHBOX_URL --app your-app-name

# Test Searchbox connectivity
curl -s "$(heroku config:get SEARCHBOX_URL --app your-app-name)"
```

### **3. Test Leek Application**
```bash
# Get app URL
heroku info --app your-app-name

# Open in browser
heroku open --app your-app-name
```

### **4. Access Searchbox Dashboard**
```bash
# Open Searchbox dashboard
heroku addons:open searchbox --app your-app-name
```

## 🔧 **Post-Deployment Configuration**

### **1. Firebase Authorization**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to Authentication → Settings
4. Add your Heroku app domain to authorized domains:
   - `your-app-name.herokuapp.com`

### **2. Celery Worker Configuration**
In your Django app, ensure Celery is configured to send events:

```python
# In your Celery settings
app.conf.worker_send_task_events = True
app.conf.task_send_sent_event = True
app.conf.task_track_started = True
```

### **3. Create Leek Application**
1. Visit your Leek URL: `https://your-app-name.herokuapp.com`
2. Sign in with Google (Firebase authentication)
3. Create a new application:
   - **Organization**: Your email domain
   - **App Name**: Your Django app name (e.g., `funly`)
   - **Environment**: `prod` (or appropriate environment)

## 📈 **Monitoring and Maintenance**

### **Daily Monitoring**
```bash
# Check app health
heroku ps --app your-app-name

# Monitor logs
heroku logs --tail --app your-app-name

# Check Searchbox metrics
heroku addons:open searchbox --app your-app-name
```

### **Weekly Tasks**
```bash
# Check dyno usage
heroku ps:type --app your-app-name

# Review Searchbox usage
heroku addons:info searchbox --app your-app-name

# Check release history
heroku releases --app your-app-name
```

### **Monthly Reviews**
- Review Searchbox usage and consider plan adjustments
- Check Firebase usage and security logs
- Review Celery task patterns and optimize if needed

## 💰 **Cost Management**

### **Current Costs**
- **Searchbox Starter**: $9/month
- **Heroku Standard-1X**: $25/month
- **Total**: ~$34/month

### **Optimization Options**
```bash
# Upgrade Searchbox for better performance
heroku addons:upgrade searchbox:professional --app your-app-name

# Upgrade dyno for better reliability
heroku ps:resize web=standard-2x --app your-app-name

# Scale additional dynos if needed
heroku ps:scale web=2 --app your-app-name
```

## 🐛 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Searchbox Not Provisioned**
```bash
# Check addon status
heroku addons:info searchbox --app your-app-name

# Wait for provisioning
heroku addons:wait searchbox --app your-app-name
```

#### **2. Environment Variables Missing**
```bash
# Check all config vars
heroku config --app your-app-name

# Set missing variables
heroku config:set LEEK_ES_URL=$(heroku config:get SEARCHBOX_URL --app your-app-name) --app your-app-name
```

#### **3. Bootstrap Failures**
```bash
# Check bootstrap logs
heroku logs --app your-app-name | grep bootstrap

# Restart application
heroku restart --app your-app-name
```

#### **4. Celery Integration Issues**
```bash
# Check Celery worker configuration
heroku run python manage.py shell --app your-django-app
# In shell: from celery import current_app; print(current_app.conf.worker_send_task_events)

# Test Celery task
heroku run python manage.py shell --app your-django-app
# Run a simple Celery task and check if it appears in Leek
```

## 📚 **Additional Resources**

### **Documentation**
- [Searchbox Deployment Guide](SEARCHBOX_DEPLOYMENT_GUIDE.md)
- [Environment Setup Guide](ENVIRONMENT_SETUP.md)
- [Heroku Deploy Guide](heroku-deploy-guide.md)

### **Support Commands**
```bash
# Get help with scripts
./heroku-setup.sh --help
./quick-deploy.sh --help

# Heroku support
heroku help
heroku logs --help
```

### **External Resources**
- [Heroku Documentation](https://devcenter.heroku.com/)
- [Searchbox Documentation](https://elements.heroku.com/addons/searchbox)
- [Firebase Documentation](https://firebase.google.com/docs)

## ✅ **Success Criteria**

Your deployment is successful when:

1. ✅ **Heroku app is running** (`heroku ps --app your-app-name`)
2. ✅ **Searchbox addon is active** (`heroku addons:info searchbox --app your-app-name`)
3. ✅ **Leek UI is accessible** (visit your app URL)
4. ✅ **Firebase authentication works** (can sign in with Google)
5. ✅ **Celery tasks appear in Leek** (after triggering tasks in Django)
6. ✅ **Data persists after restart** (`heroku restart --app your-app-name`)
7. ✅ **Searchbox dashboard is accessible** (`heroku addons:open searchbox --app your-app-name`)

## 🎉 **Congratulations!**

You've successfully deployed Leek with Searchbox Elasticsearch! Your Celery task monitoring is now:

- **Persistent**: Data survives app restarts
- **Managed**: No Elasticsearch maintenance required
- **Monitored**: Professional dashboard and alerting
- **Scalable**: Easy to upgrade plans and dynos
- **Reliable**: Backed by managed services

---

**Need help?** Check the troubleshooting section or review the detailed guides in the documentation. 