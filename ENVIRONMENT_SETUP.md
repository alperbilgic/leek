# Environment-Aware Leek Deployment & Sync Guide

This guide explains how to deploy Leek and set up automatic Django task syncing across different environments (test, staging, production).

## 🌍 Environment Configuration

### Environment Variables

The scripts automatically detect and configure based on these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` or `ENV` | Environment type | `production`, `staging`, `test` |
| `LEEK_APP_NAME` | Heroku app name for Leek | `funly-prod-leek` |
| `DJANGO_APP_NAME` | Heroku app name for Django | `funly-manage-prod` |
| `SYNC_DAYS` | Days of history to sync | `30` (default) |

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

# Run deployment (Django sync happens automatically on Heroku)
./quick-deploy.sh
```

### Option 2: Manual Step-by-Step

```bash
# 1. Set environment
export ENV=production
export LEEK_APP_NAME="funly-prod-leek"
export DJANGO_APP_NAME="funly-manage-prod"

# 2. Run setup
./heroku-setup.sh

# 3. Deploy manually (sync happens automatically during release)
git push heroku-leek heroku-deployment:main
```

### Option 3: Environment-Specific Variables

```bash
# Production deployment
LEEK_APP_NAME="funly-prod-leek" \
DJANGO_APP_NAME="funly-manage-prod" \
SYNC_DAYS=60 \
./quick-deploy.sh

# Staging deployment  
LEEK_APP_NAME="funly-staging-leek" \
DJANGO_APP_NAME="funly-manage-staging" \
SYNC_DAYS=14 \
./quick-deploy.sh
```

## 🔄 Automatic Sync Operations

### Automatic Sync (Default Behavior)
Django data sync now happens **automatically** during each Leek deployment via Heroku release tasks.

```bash
# Check sync status in release logs
heroku releases:output --app funly-prod-leek

# View real-time release logs
heroku logs --tail --dyno=release --app funly-prod-leek
```

### Manual Sync (If Needed)
```bash
# Direct Django command (if manual sync needed)
heroku run python manage.py sync_tasks_to_leek --days=30 --app funly-manage-prod

# Check if Django app has the sync command
heroku run python manage.py help sync_tasks_to_leek --app funly-manage-prod
```

## 📁 File Structure

```
leek/
├── heroku-setup.sh          # Sets up Heroku app with environment variables
├── quick-deploy.sh          # Deploys with automatic sync
├── release_with_sync.py     # Automatic Heroku release task
├── heroku.yml               # Heroku deployment configuration
├── ENVIRONMENT_SETUP.md     # This guide
└── AUTOMATIC_DEPLOYMENT.md  # Automatic deployment architecture
```

## 🔧 Environment-Specific Configuration Examples

### Production Setup
```bash
export ENV=production
export LEEK_APP_NAME="funly-prod-leek"
export DJANGO_APP_NAME="funly-manage-prod" 
export SYNC_DAYS=90
./quick-deploy.sh
```

### Staging Setup
```bash
export ENV=staging
export LEEK_APP_NAME="funly-staging-leek"
export DJANGO_APP_NAME="funly-manage-staging"
export SYNC_DAYS=30
./quick-deploy.sh
```

### Development Setup  
```bash
export ENV=test
export LEEK_APP_NAME="funly-dev-leek"
export DJANGO_APP_NAME="funly-manage-dev"
export SYNC_DAYS=7
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

### Sync Failures
```bash
# Check Django app has sync command
heroku run python manage.py help sync_tasks_to_leek --app your-django-app

# Check Leek is ready
curl -s https://your-leek-app.herokuapp.com/v1/events/process \
  -H "x-leek-org-name: palnea.com" \
  -H "x-leek-app-name: funly" \
  -H "x-leek-app-env: prod"
```

### Config Variables
```bash
# Check stored config
heroku config:get DEPLOYMENT_LEEK_APP --app your-leek-app
heroku config:get DEPLOYMENT_DJANGO_APP --app your-leek-app

# Update if needed
heroku config:set DEPLOYMENT_DJANGO_APP=your-django-app --app your-leek-app
```

## 🎯 Best Practices

1. **Use environment variables** for CI/CD pipelines
2. **Set SYNC_DAYS appropriately** for your data retention needs
3. **Monitor release logs** for automatic sync status
4. **Check release output** after each deployment
5. **Keep Django task retention** aligned with Leek sync period

## 📊 Verification

After deployment and sync:

1. **Check Leek Dashboard**: Visit your Leek URL
2. **Verify Historical Tasks**: Look for tasks from before deployment
3. **Test New Tasks**: Run a Celery task and verify it appears in both systems
4. **Check Retry Functionality**: Try retrying a failed task from Leek UI 