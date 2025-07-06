#!/bin/bash

# Quick Leek Deployment Script for Heroku
# This script runs the setup and deployment in one go

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Quick Leek Deployment for Heroku with Searchbox${NC}"
echo "=================================================="

# Check if setup script exists
if [ ! -f "heroku-setup.sh" ]; then
    echo -e "${RED}❌ heroku-setup.sh not found. Please run from project root.${NC}"
    exit 1
fi

# Run setup
echo -e "${BLUE}📋 Running Heroku setup with Searchbox addon...${NC}"
bash heroku-setup.sh

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Setup completed successfully${NC}"
else
    echo -e "${RED}❌ Setup failed${NC}"
    exit 1
fi

# Get app name for deployment
read -p "Enter Heroku app name [funly-manage-test-leek]: " APP_NAME
APP_NAME=${APP_NAME:-funly-manage-test-leek}

# Deploy
echo -e "${BLUE}🐳 Deploying to Heroku with Docker...${NC}"

# Initialize git if needed
if [ ! -d ".git" ]; then
    git init
fi

# Add all files
git add .

# Always commit changes or create empty commit to ensure deployment
if git diff --staged --quiet; then
    echo -e "${YELLOW}ℹ️  No changes detected, creating empty commit to force redeploy...${NC}"
    git commit --allow-empty -m "Deploy Leek with Searchbox - $(date)"
else
    echo -e "${GREEN}📝 Changes detected, committing...${NC}"
    git commit -m "Deploy Leek with Searchbox - $(date)"
fi

# Get app name for deployment
read -p "Enter Heroku remote name [heroku-leek]: " HEROKU_REMOTE
HEROKU_REMOTE=${HEROKU_REMOTE:-heroku-leek}

# Check if remote exists
if ! git remote get-url $HEROKU_REMOTE &> /dev/null; then
    heroku git:remote -a $APP_NAME -r $HEROKU_REMOTE
fi

# Push to Heroku
echo -e "${YELLOW}⬆️  Pushing to Heroku (this may take several minutes)...${NC}"
git push $HEROKU_REMOTE main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    
    # Scale the app
    echo -e "${YELLOW}⚖️  Scaling web dyno...${NC}"
    heroku ps:scale web=1 --app $APP_NAME
    
    # Get the actual app URL from Heroku
    echo -e "${YELLOW}🔗 Getting app URL from Heroku...${NC}"
    HEROKU_APP_URL=$(heroku info --app $APP_NAME | grep "Web URL" | awk '{print $3}')
    
    # Get Searchbox URL
    SEARCHBOX_URL=$(heroku config:get SEARCHBOX_URL --app $APP_NAME)
    
    echo -e "${GREEN}🎉 Leek is now running with Searchbox!${NC}"
    echo ""
    echo -e "${YELLOW}🌐 Your Leek instance:${NC} $HEROKU_APP_URL"
    echo -e "${YELLOW}🔍 Searchbox URL:${NC} $SEARCHBOX_URL"
    echo ""
    
    echo -e "${BLUE}📊 Searchbox Dashboard Access:${NC}"
    echo "heroku addons:open searchbox --app $APP_NAME"
    echo ""
    
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Add $(echo $HEROKU_APP_URL | sed 's|https://||') to Firebase authorized domains"
    echo "2. Configure your Celery workers to send events"
    echo "3. Visit $HEROKU_APP_URL to access Leek"
    echo "4. Access Searchbox dashboard: heroku addons:open searchbox --app $APP_NAME"
    echo ""
    echo -e "${GREEN}🎯 Searchbox Benefits:${NC}"
    echo "• ✅ Persistent data storage (survives app restarts)"
    echo "• ✅ Managed Elasticsearch service"
    echo "• ✅ Better performance and reliability"
    echo "• ✅ Searchbox dashboard for monitoring"
    echo ""
    echo -e "${BLUE}📚 Check the logs:${NC} heroku logs --tail --app $APP_NAME"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    echo "Check the logs: heroku logs --tail --app $APP_NAME"
    exit 1
fi 