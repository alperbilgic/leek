# 🚀 Leek Deployment - Quick Start

This is the **automatic deployment** system for Leek with **Searchbox Elasticsearch**.

## ⚡ **Quick Deploy**

```bash
# Set your environment
export ENV=production  # or staging, test

# Deploy everything (Leek + Searchbox)
./quick-deploy.sh
```

That's it! 🎉

## 🔧 **What Happens Automatically**

1. **Setup**: Configures Heroku app with Searchbox addon
2. **Deploy**: Builds and deploys Leek to Heroku  
3. **Bootstrap**: Initializes Searchbox and Leek services
4. **Ready**: Leek is running with persistent data storage

## 📊 **Check Status**

```bash
# View your Leek instance
heroku open --app funly-prod-leek

# Check release logs
heroku releases:output --app funly-prod-leek

# Monitor real-time
heroku logs --tail --app funly-prod-leek

# Access Searchbox dashboard
heroku addons:open searchbox --app funly-prod-leek
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
- Django app name (for Redis connection)

All configuration is stored in Heroku and persists across deployments.

## 🔍 **Searchbox Elasticsearch**

Your deployment includes:
- ✅ **Persistent data storage** (survives app restarts)
- ✅ **Managed Elasticsearch service** (no maintenance required)
- ✅ **Better performance** and reliability
- ✅ **Automatic backups** and monitoring
- ✅ **Searchbox dashboard** for analytics

## 📁 **Key Files**

- `quick-deploy.sh` - Main deployment script
- `heroku-setup.sh` - Configuration setup with Searchbox
- `release.py` - Automatic bootstrap (runs on Heroku)
- `heroku.yml` - Heroku deployment config

## 🆘 **Troubleshooting**

**Deployment Issues:**
```bash
heroku logs --app funly-prod-leek
```

**Searchbox Issues:**
```bash
heroku addons:open searchbox --app funly-prod-leek
heroku addons:info searchbox --app funly-prod-leek
```

**Bootstrap Issues:**  
```bash
heroku releases:output --app funly-prod-leek
```

## 📚 **More Information**

- **Full Documentation**: `ENVIRONMENT_SETUP.md`
- **Searchbox Guide**: `SEARCHBOX_DEPLOYMENT_GUIDE.md`

---

**Ready to deploy?** Just run: `ENV=production ./quick-deploy.sh` 🚀 