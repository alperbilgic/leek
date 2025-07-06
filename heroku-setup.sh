#!/bin/bash

# Heroku Leek Setup Script
# This script helps set up Leek on Heroku with proper environment variables

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
HEROKU_APP_NAME="funly-manage-test-leek"
ORIGINAL_APP="funly-manage-test"

echo -e "${GREEN}🌿 Leek Heroku Setup Script${NC}"
echo "=============================="

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${RED}❌ Heroku CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo -e "${YELLOW}⚠️  Please log in to Heroku first${NC}"
    heroku login
fi

echo -e "${GREEN}✅ Heroku CLI is ready${NC}"

# Get user inputs
read -p "Enter Heroku app name for Leek [funly-manage-test-leek]: " input_app_name
HEROKU_APP_NAME=${input_app_name:-$HEROKU_APP_NAME}

read -p "Enter your original app name [funly-manage-test]: " input_original_app
ORIGINAL_APP=${input_original_app:-$ORIGINAL_APP}

# Export environment variables for post-deployment scripts
export LEEK_APP_NAME="$HEROKU_APP_NAME"
export DJANGO_APP_NAME="$ORIGINAL_APP"

read -p "Enter your Firebase Project ID: " FIREBASE_PROJECT_ID
if [ -z "$FIREBASE_PROJECT_ID" ]; then
    echo -e "${RED}❌ Firebase Project ID is required${NC}"
    exit 1
fi

read -p "Enter your Firebase API Key: " FIREBASE_API_KEY
if [ -z "$FIREBASE_API_KEY" ]; then
    echo -e "${RED}❌ Firebase API Key is required${NC}"
    exit 1
fi

read -p "Enter your Firebase App ID: " FIREBASE_APP_ID
if [ -z "$FIREBASE_APP_ID" ]; then
    echo -e "${RED}❌ Firebase App ID is required${NC}"
    exit 1
fi

read -p "Enter your email domain (e.g., yourdomain.com): " EMAIL_DOMAIN
if [ -z "$EMAIL_DOMAIN" ]; then
    echo -e "${RED}❌ Email domain is required${NC}"
    exit 1
fi

read -p "Enter days of Django tasks to sync [30]: " input_sync_days
SYNC_DAYS=${input_sync_days:-30}

echo -e "${YELLOW}📋 Getting Redis URL from your original app...${NC}"
REDIS_URL=$(heroku config:get REDISCLOUD_URL --app $ORIGINAL_APP)
if [ -z "$REDIS_URL" ]; then
    echo -e "${RED}❌ Could not get Redis URL from $ORIGINAL_APP${NC}"
    echo "Please make sure Redis is configured in your original app"
    exit 1
fi
echo -e "${GREEN}✅ Redis URL obtained${NC}"

# Create Heroku app
echo -e "${YELLOW}🏗️  Creating Heroku app: $HEROKU_APP_NAME${NC}"
if heroku apps:info $HEROKU_APP_NAME &> /dev/null; then
    echo -e "${YELLOW}⚠️  App $HEROKU_APP_NAME already exists. Continuing with configuration...${NC}"
else
    heroku create $HEROKU_APP_NAME
    echo -e "${GREEN}✅ App created successfully${NC}"
fi

# Check addon configuration
echo -e "${YELLOW}🔌 Checking addon configuration...${NC}"

# Function to check if addon exists
check_addon_exists() {
    local app_name=$1
    local addon_type=$2
    heroku addons --app $app_name 2>/dev/null | grep -q "$addon_type"
}

# Note about local Elasticsearch
echo -e "${BLUE}ℹ️  Using local Elasticsearch inside Docker container (no external addon needed)${NC}"

if check_addon_exists $HEROKU_APP_NAME "redis"; then
    echo -e "${YELLOW}⚠️  WARNING: Redis addon found on Leek app. This is usually unnecessary.${NC}"
    echo -e "${YELLOW}   We'll use your existing Redis from $ORIGINAL_APP instead.${NC}"
    EXISTING_REDIS=$(heroku addons --app $HEROKU_APP_NAME | grep redis | awk '{print $1}')
    echo -e "${YELLOW}   Consider removing this addon: heroku addons:destroy $EXISTING_REDIS --app $HEROKU_APP_NAME${NC}"
fi

echo -e "${GREEN}✅ Using existing Redis from $ORIGINAL_APP (no new Redis needed)${NC}"
echo -e "${GREEN}✅ Local Elasticsearch will run inside Docker container${NC}"

# Generate API secret
AGENT_SECRET=$(openssl rand -hex 32)

# Set stack to container for Docker deployment
echo -e "${YELLOW}🐳 Setting stack to container for Docker deployment...${NC}"
heroku stack:set container --app $HEROKU_APP_NAME

# Get the actual app URL from Heroku
echo -e "${YELLOW}🔗 Getting app URL from Heroku...${NC}"
HEROKU_APP_URL=$(heroku info --app $HEROKU_APP_NAME | grep "Web URL" | awk '{print $3}')
if [ -z "$HEROKU_APP_URL" ]; then
    echo -e "${RED}❌ Could not get app URL from Heroku${NC}"
    exit 1
fi
echo -e "${GREEN}✅ App URL obtained: $HEROKU_APP_URL${NC}"

# Set environment variables
echo -e "${YELLOW}⚙️  Setting environment variables...${NC}"

heroku config:set \
  LEEK_API_LOG_LEVEL=INFO \
  LEEK_AGENT_LOG_LEVEL=INFO \
  LEEK_ENABLE_API=true \
  LEEK_ENABLE_AGENT=true \
  LEEK_ENABLE_WEB=true \
  LEEK_API_ENABLE_AUTH=true \
  LEEK_FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID \
  LEEK_FIREBASE_API_KEY=$FIREBASE_API_KEY \
  LEEK_FIREBASE_AUTH_DOMAIN=$FIREBASE_PROJECT_ID.firebaseapp.com \
  LEEK_FIREBASE_APP_ID=$FIREBASE_APP_ID \
  LEEK_API_OWNER_ORG=$EMAIL_DOMAIN \
  LEEK_API_WHITELISTED_ORGS=$EMAIL_DOMAIN \
  LEEK_API_URL=$HEROKU_APP_URL \
  LEEK_WEB_URL=$HEROKU_APP_URL \
  LEEK_ES_URL=http://localhost:9200 \
  LEEK_AGENT_API_SECRET=$AGENT_SECRET \
  LEEK_ES_IM_ENABLE=false \
  LEEK_ENABLE_EVENTS_CLEANUP=false \
  LEEK_ENABLE_STATS_CLEANUP=false \
  LEEK_CLEAN_BROKER_ON_STARTUP=false \
  LEEK_ES_INDEX_CLEANUP_ENABLED=false \
  LEEK_CLEAN_DATABASE_ON_STARTUP=false \
  LEEK_PERSIST_ON_WORKER_RESTART=true \
  DEPLOYMENT_LEEK_APP=$HEROKU_APP_NAME \
  DEPLOYMENT_DJANGO_APP=$ORIGINAL_APP \
  SYNC_DAYS=$SYNC_DAYS \
  --app $HEROKU_APP_NAME

# Set agent subscriptions
AGENT_SUBSCRIPTIONS="[
  {
    \"broker\": \"$REDIS_URL\",
    \"broker_management_url\": \"$REDIS_URL\",
    \"backend\": null,
    \"exchange\": \"celeryev\",
    \"queue\": \"leek.fanout\",
    \"routing_key\": \"#\",
    \"org_name\": \"$EMAIL_DOMAIN\",
    \"app_name\": \"funly\",
    \"app_env\": \"prod\",
    \"prefetch_count\": 1000,
    \"concurrency_pool_size\": 2,
    \"batch_max_size_in_mb\": 1,
    \"batch_max_number_of_messages\": 1000,
    \"batch_max_window_in_seconds\": 5
  }
]"

heroku config:set LEEK_AGENT_SUBSCRIPTIONS="$AGENT_SUBSCRIPTIONS" --app $HEROKU_APP_NAME

echo -e "${GREEN}✅ Environment variables configured${NC}"

# Set up git remote
echo -e "${YELLOW}🔗 Setting up git remote...${NC}"
if ! git remote get-url heroku-leek &> /dev/null; then
    heroku git:remote -a $HEROKU_APP_NAME -r heroku-leek
else
    echo -e "${YELLOW}⚠️  Git remote 'heroku-leek' already exists${NC}"
fi

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo -e "${YELLOW}✨ Configuration Summary:${NC}"
echo "• Using local Elasticsearch inside Docker container (no external addon needed)"
echo "• Using existing Redis from $ORIGINAL_APP"
echo "• Firebase authentication configured"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Deploy the app with Docker: git push heroku-leek master:main (from project root)"
echo "2. Scale the web dyno: heroku ps:scale web=1 --app $HEROKU_APP_NAME"
echo "3. Add $(echo $HEROKU_APP_URL | sed 's|https://||') to Firebase authorized domains"
echo "4. Configure your Celery workers to send events (see deployment guide)"
echo "5. Visit $HEROKU_APP_URL to access Leek UI"
echo ""
echo -e "${GREEN}📖 See heroku-deploy-guide.md for detailed instructions${NC}" 