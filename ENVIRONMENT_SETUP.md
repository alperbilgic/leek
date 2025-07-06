# Environment-Aware Leek Deployment & Setup Guide

This guide explains how to deploy Leek with **Searchbox Elasticsearch** across different environments (test, staging, production).

## 🌍 Environment Configuration

### Environment Variables

The scripts automatically detect and configure based on these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` or `ENV` | Environment type | `production`, `staging`, `test` |
| `LEEK_APP_NAME` | Heroku app name for Leek | `funly-prod-leek` |
| `DJANGO_APP_NAME` | Heroku app name for Django | `funly-manage-prod` |

### Auto-Detection Rules

If environment variables are not set, the scripts use these patterns:

#### Production Environment
- **Leek App**: `funly-prod-leek`
- **Django App**: `funly-manage-prod`
- **Triggers**: `ENVIRONMENT=production` or `ENV=prod`

#### Staging Environment  
- **Leek App**: `funly-staging-leek`
- **Django App**: `funly-manage-staging`
- **Triggers**: `ENVIRONMENT=staging` or `ENV=staging`

#### Test/Development Environment (Default)
- **Leek App**: `funly-manage-test-leek`
- **Django App**: `funly-manage-test`
- **Triggers**: Any other value or no environment set

## 🚀 Deployment Workflows

### Option 1: Automatic Deployment (Recommended)

```bash
# Set environment first
export ENV=production  # or staging, test

# Run deployment
./quick-deploy.sh
```

### Option 2: Manual Step-by-Step

```bash
# 1. Set environment
export ENV=production
export LEEK_APP_NAME="funly-prod-leek"
export DJANGO_APP_NAME="funly-manage-prod"

# 2. Run setup (includes Searchbox addon)
./heroku-setup.sh

# 3. Deploy manually
git push heroku-leek main
```

### Option 3: Environment-Specific Variables

```bash
# Production deployment
LEEK_APP_NAME="funly-prod-leek" \
DJANGO_APP_NAME="funly-manage-prod" \
./quick-deploy.sh

# Staging deployment  
LEEK_APP_NAME="funly-staging-leek" \
DJANGO_APP_NAME="funly-manage-staging" \
./quick-deploy.sh
```

## 🔍 Searchbox Elasticsearch Configuration

### Automatic Setup
All deployment scripts automatically:
- ✅ **Add Searchbox addon** to your Heroku app
- ✅ **Configure persistent storage** for your Elasticsearch data
- ✅ **Set environment variables** for optimal performance
- ✅ **Enable dashboard access** for monitoring

### Environment-Specific Searchbox Settings
```bash
# Production - Higher performance plan
heroku addons:upgrade searchbox:professional --app funly-prod-leek

# Staging - Standard plan
heroku addons:upgrade searchbox:starter --app funly-staging-leek

# Test - Starter plan (default)
# Already configured automatically
```

## 📊 Monitoring and Analytics

### Searchbox Dashboard Access
```bash
# Open Searchbox dashboard for any environment
heroku addons:open searchbox --app funly-prod-leek
heroku addons:open searchbox --app funly-staging-leek
heroku addons:open searchbox --app funly-manage-test-leek
```

### Performance Monitoring
```bash
# Check Searchbox performance metrics
heroku addons:info searchbox --app funly-prod-leek

# Monitor resource usage
heroku ps --app funly-prod-leek
```

## 📁 File Structure

```
leek/
├── heroku-setup.sh                 # Sets up Heroku app with Searchbox addon
├── quick-deploy.sh                 # Deploys with automatic bootstrap
├── release.py                      # Automatic Heroku release task
├── heroku.yml                      # Heroku deployment configuration
├── ENVIRONMENT_SETUP.md            # This guide
├── SEARCHBOX_DEPLOYMENT_GUIDE.md   # Detailed Searchbox guide
└── Dockerfile                      # Docker configuration (no local ES)
```

## 🔧 Environment-Specific Configuration Examples

### Production Setup
```bash
export ENV=production
export LEEK_APP_NAME="funly-prod-leek"
export DJANGO_APP_NAME="funly-manage-prod" 
./quick-deploy.sh

# Upgrade to professional plan for production
heroku addons:upgrade searchbox:professional --app funly-prod-leek
```

### Staging Setup
```bash
export ENV=staging
export LEEK_APP_NAME="funly-staging-leek"
export DJANGO_APP_NAME="funly-manage-staging"
./quick-deploy.sh
```

### Development Setup  
```bash
export ENV=test
export LEEK_APP_NAME="funly-dev-leek"
export DJANGO_APP_NAME="funly-manage-dev"
./quick-deploy.sh
```

## 🐛 Troubleshooting

### App Names Not Detected
```bash
# Check current detection
echo "Environment: $ENV"
echo "Leek App: $LEEK_APP_NAME"  
echo "Django App: $DJANGO_APP_NAME"

# Manual override
export LEEK_APP_NAME="your-leek-app"
export DJANGO_APP_NAME="your-django-app"
```

### Searchbox Issues
```bash
# Check Searchbox addon status
heroku addons:info searchbox --app your-leek-app

# Test Searchbox connectivity
curl -s "$(heroku config:get SEARCHBOX_URL --app your-leek-app)"

# Access Searchbox dashboard
heroku addons:open searchbox --app your-leek-app
```

### Bootstrap Issues
```bash
# Check bootstrap logs
heroku logs --app your-leek-app | grep bootstrap

# Check Leek is ready
curl -s https://your-leek-app.herokuapp.com/v1/events/process \
  -H "x-leek-org-name: palnea.com" \
  -H "x-leek-app-name: funly" \
  -H "x-leek-app-env: prod"
```

### Config Variables
```bash
# Check stored config
heroku config:get SEARCHBOX_URL --app your-leek-app
heroku config:get LEEK_ES_URL --app your-leek-app

# Update if needed
heroku config:set LEEK_ES_URL=$(heroku config:get SEARCHBOX_URL --app your-leek-app) --app your-leek-app
```

## 🎯 Best Practices

1. **Use environment variables** for CI/CD pipelines
2. **Monitor release logs** for bootstrap status
3. **Check Searchbox dashboard** for performance metrics
4. **Use appropriate Searchbox plans** for each environment
5. **Configure Celery workers** to send events to Leek

## 📊 Verification

After deployment:

1. **Check Leek Dashboard**: Visit your Leek URL
2. **Test Celery Integration**: Run a Celery task and verify it appears in Leek
3. **Check Data Persistence**: Restart the app and verify data survives
4. **Monitor Searchbox**: Use dashboard to verify data storage and performance

## 💰 Cost Optimization by Environment

### Production
- **Searchbox Professional**: $49/month (10GB storage, 4GB RAM)
- **Heroku Standard-2X**: $50/month (high availability)
- **Total**: ~$99/month

### Staging
- **Searchbox Starter**: $9/month (1GB storage, 1GB RAM)
- **Heroku Standard-1X**: $25/month
- **Total**: ~$34/month

### Test/Development
- **Searchbox Starter**: $9/month
- **Heroku Standard-1X**: $25/month
- **Total**: ~$34/month

## 🔍 Advanced Configuration

### Custom Searchbox Settings
```bash
# Configure custom Elasticsearch settings per environment
heroku config:set LEEK_ES_TIMEOUT=30 --app your-leek-app
heroku config:set LEEK_ES_MAX_RETRIES=3 --app your-leek-app

# Environment-specific index settings
heroku config:set LEEK_ES_INDEX_PATTERN="leek-prod-*" --app funly-prod-leek
heroku config:set LEEK_ES_INDEX_PATTERN="leek-staging-*" --app funly-staging-leek
```

### Backup and Recovery
```bash
# Searchbox provides automated backups
# Access via dashboard for restore operations
heroku addons:open searchbox --app your-leek-app
```

---

**🎉 Success!** Your Leek deployment with Searchbox Elasticsearch is now configured for persistent, reliable task monitoring across all environments. 