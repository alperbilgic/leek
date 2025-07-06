# 🚀 Leek Deployment - Quick Start

This is the **automatic deployment** system for Leek with Django task synchronization.

## ⚡ **Quick Deploy**

```bash
# Set your environment
export ENV=production  # or staging, test

# Deploy everything (Leek + automatic Django sync)
./quick-deploy.sh
```

That's it! 🎉

## 🔧 **What Happens Automatically**

1. **Setup**: Configures Heroku app with all environment variables
2. **Deploy**: Builds and deploys Leek to Heroku  
3. **Bootstrap**: Initializes Elasticsearch and Leek services
4. **Sync**: Automatically syncs historical tasks from Django database
5. **Ready**: Leek is running with all your historical data

## 📊 **Check Status**

```bash
# View your Leek instance
heroku open --app funly-prod-leek

# Check release logs (including sync status)
heroku releases:output --app funly-prod-leek

# Monitor real-time
heroku logs --tail --app funly-prod-leek
```

## 🌍 **Multi-Environment Support**

```bash
# Production
ENV=production ./quick-deploy.sh

# Staging  
ENV=staging ./quick-deploy.sh

# Test/Development
ENV=test ./quick-deploy.sh
```

## 🔧 **Configuration**

The setup script will ask you for:
- Firebase credentials
- Email domain
- Django app name
- Days of history to sync (default: 30)

All configuration is stored in Heroku and persists across deployments.

## 📁 **Key Files**

- `quick-deploy.sh` - Main deployment script
- `heroku-setup.sh` - Configuration setup
- `release_with_sync.py` - Automatic sync (runs on Heroku)
- `heroku.yml` - Heroku deployment config

## 🆘 **Troubleshooting**

**Deployment Issues:**
```bash
heroku logs --app funly-prod-leek
```

**Sync Issues:**  
```bash
heroku releases:output --app funly-prod-leek
```

**Manual Sync (if needed):**
```bash
heroku run --app funly-manage-test -- python manage.py sync_django_to_leek --days=30
```

## 📚 **More Information**

- **Full Documentation**: `ENVIRONMENT_SETUP.md`
- **Architecture Details**: `AUTOMATIC_DEPLOYMENT.md`

---

**Ready to deploy?** Just run: `ENV=production ./quick-deploy.sh` 🚀 