# 🚀 Leek Deployment Guide: Searchbox Elasticsearch

This guide explains how to deploy Leek with Searchbox Elasticsearch addon for persistent, reliable task monitoring.

## 🎯 **Why Searchbox Elasticsearch?**

**Searchbox Advantages:**
- ✅ **Persistent data storage** (survives app restarts)
- ✅ **Managed Elasticsearch service** (no maintenance required)
- ✅ **Better performance** and reliability
- ✅ **Automatic backups** and maintenance
- ✅ **Searchbox dashboard** for monitoring
- ✅ **Reduced resource usage** in your app container
- ✅ **Professional monitoring** and alerting

## 🚀 **Quick Deployment (Recommended)**

### Option 1: Automated Deployment
```bash
# Set your environment
export ENV=production  # or staging, test

# Deploy everything automatically
./quick-deploy.sh
```

This will:
1. ✅ Create Heroku app with Searchbox addon
2. ✅ Configure all environment variables
3. ✅ Deploy Leek with persistent storage
4. ✅ Set up automatic Django sync
5. ✅ Scale and verify deployment

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Run Setup Script
```bash
# Interactive setup with Searchbox
./heroku-setup.sh
```

#### Step 2: Deploy to Heroku
```bash
# Commit and deploy
git add .
git commit -m "Deploy Leek with Searchbox"
git push heroku-leek main
```

#### Step 3: Scale and Verify
```bash
# Scale the web dyno
heroku ps:scale web=1 --app your-app-name

# Check deployment
heroku logs --tail --app your-app-name
```

## 📊 **Searchbox Dashboard Access**

### Via Heroku Dashboard
1. Go to your [Heroku Dashboard](https://dashboard.heroku.com/)
2. Select your Leek app
3. Click on "Searchbox" in the Add-ons section
4. This opens the Searchbox dashboard

### Via CLI
```bash
# Open Searchbox dashboard
heroku addons:open searchbox --app your-app-name

# Check addon status
heroku addons:info searchbox --app your-app-name
```

### Dashboard Features
- 🔍 **Search and query** your Elasticsearch data
- 📈 **Performance metrics** and monitoring
- 🔧 **Index management** and settings
- 📊 **Usage statistics** and analytics
- 🚨 **Alerts and notifications**
- 📋 **Query builder** and data explorer

## 🛠️ **Configuration Details**

### Environment Variables
```bash
# Searchbox URL (automatically set by addon)
LEEK_ES_URL=https://your-searchbox-url.searchbox.io

# Searchbox-optimized settings
LEEK_ES_IM_ENABLE=false                    # Disable index management
LEEK_ES_INDEX_CLEANUP_ENABLED=false       # Disable cleanup on Searchbox
LEEK_CLEAN_DATABASE_ON_STARTUP=false      # Preserve data on restart
```

### Searchbox Plans
| Plan | Price | Storage | RAM | Features |
|------|-------|---------|-----|----------|
| **Starter** | $9/month | 1 GB | 1 GB | Basic monitoring, SSL |
| **Professional** | $49/month | 10 GB | 4 GB | Advanced features, backups |
| **Business** | $149/month | 50 GB | 16 GB | High availability, SLA |

**Recommendation:** Start with **Starter** plan for development/testing

## 🔧 **Troubleshooting**

### Common Issues

#### 1. Searchbox Addon Not Provisioned
```bash
# Check if addon is provisioned
heroku addons --app your-app-name

# Check addon status
heroku addons:info searchbox --app your-app-name

# Wait for provisioning if needed
heroku addons:wait searchbox --app your-app-name
```

#### 2. Connection Issues
```bash
# Test Searchbox connectivity
curl -s -f "$(heroku config:get SEARCHBOX_URL --app your-app-name)"

# Check app logs for ES connection errors
heroku logs --tail --app your-app-name | grep -i elastic
```

#### 3. Performance Issues
```bash
# Check Searchbox dashboard for resource usage
heroku addons:open searchbox --app your-app-name

# Consider upgrading plan if needed
heroku addons:upgrade searchbox:professional --app your-app-name
```

#### 4. Data Not Appearing
```bash
# Verify correct environment variables
heroku config:get LEEK_ES_URL --app your-app-name

# Check bootstrap logs
heroku logs --app your-app-name | grep bootstrap

# Restart application
heroku restart --app your-app-name
```

### Debugging Commands
```bash
# Check all environment variables
heroku config --app your-app-name

# Check running processes
heroku ps --app your-app-name

# View real-time logs
heroku logs --tail --app your-app-name

# Check addon status
heroku addons --app your-app-name

# Test Searchbox directly
heroku run curl -s "$(heroku config:get SEARCHBOX_URL --app your-app-name)" --app your-app-name
```

## 🧪 **Testing the Deployment**

### 1. Verify Searchbox Connection
```bash
# Test connection from app
heroku run python -c "
import requests
import os
url = os.environ.get('SEARCHBOX_URL')
response = requests.get(url)
print(f'Status: {response.status_code}')
print(f'Response: {response.text[:200]}')
" --app your-app-name
```

### 2. Test Data Persistence
```bash
# Create some test data in Leek UI
# Then restart the application
heroku restart --app your-app-name

# Check if data persists (should remain after restart)
# Visit your Leek UI and verify data is still there
```

### 3. Monitor Performance
```bash
# Check resource usage
heroku ps --app your-app-name

# Check Searchbox metrics
heroku addons:open searchbox --app your-app-name
```

## 🔐 **Security and Access**

### Searchbox Security Features
- 🔒 **SSL/TLS encryption** for all connections
- 🛡️ **Authentication** built into the connection URL
- 🔐 **Network isolation** from other tenants
- 📊 **Access logs** and monitoring

### Best Practices
```bash
# Rotate credentials if needed
heroku addons:upgrade searchbox:starter --app your-app-name

# Monitor access logs
heroku addons:open searchbox --app your-app-name

# Set up alerts for unusual activity
# (Available in Searchbox dashboard)
```

## 💰 **Cost Optimization**

### Cost Breakdown
- **Heroku Dyno**: ~$7-25/month (reduced resource usage)
- **Searchbox Starter**: $9/month
- **Total**: ~$16-34/month

### Optimization Tips
1. **Monitor usage** via Searchbox dashboard
2. **Clean up old data** regularly
3. **Use appropriate plan** for your data volume
4. **Set up alerts** for usage thresholds

## 🔄 **Scaling**

### Horizontal Scaling
```bash
# Scale web dynos
heroku ps:scale web=2 --app your-app-name

# Scale worker dynos (if applicable)
heroku ps:scale worker=1 --app your-app-name
```

### Vertical Scaling
```bash
# Upgrade dyno type
heroku ps:resize web=standard-2x --app your-app-name

# Upgrade Searchbox plan
heroku addons:upgrade searchbox:professional --app your-app-name
```

## 📚 **Advanced Configuration**

### Custom Searchbox Settings
```bash
# Configure specific Elasticsearch settings
heroku config:set LEEK_ES_TIMEOUT=30 --app your-app-name
heroku config:set LEEK_ES_MAX_RETRIES=3 --app your-app-name
```

### Index Management
```bash
# Access Searchbox dashboard for index management
heroku addons:open searchbox --app your-app-name

# Use the dashboard to:
# - Create custom indices
# - Set up index templates
# - Configure mappings
# - Monitor performance
```

## 🤝 **Support**

### Getting Help
1. **Check logs**: `heroku logs --tail --app your-app-name`
2. **Searchbox dashboard**: `heroku addons:open searchbox --app your-app-name`
3. **Searchbox support**: Available through their dashboard
4. **Heroku support**: For addon provisioning issues

### Useful Resources
- [Searchbox Documentation](https://elements.heroku.com/addons/searchbox)
- [Elasticsearch Documentation](https://www.elastic.co/guide/)
- [Heroku Container Registry](https://devcenter.heroku.com/articles/container-registry-and-runtime)

---

**🎉 Congratulations!** You've successfully deployed Leek with persistent, reliable Elasticsearch storage using Searchbox addon. 