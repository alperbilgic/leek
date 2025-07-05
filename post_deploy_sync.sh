#!/bin/bash

# Post-deployment script to sync Django tasks to Leek
# Run this after each Leek deployment to restore historical data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Post-deployment Django to Leek sync${NC}"
echo "=========================================="

# Configuration - Get from environment variables or auto-detect
LEEK_APP="${LEEK_APP_NAME:-${DEPLOYMENT_LEEK_APP}}"
DJANGO_APP="${DJANGO_APP_NAME:-${DEPLOYMENT_DJANGO_APP}}"
DAYS_TO_SYNC="${SYNC_DAYS:-30}"

# Auto-detect if not provided
if [ -z "$LEEK_APP" ] || [ -z "$DJANGO_APP" ]; then
    echo -e "${YELLOW}🔍 Auto-detecting app names from environment...${NC}"
    
    # Try common patterns for different environments
    if [ -z "$LEEK_APP" ]; then
        if [ "$ENVIRONMENT" = "production" ] || [ "$ENV" = "prod" ]; then
            LEEK_APP="funly-prod-leek"
        elif [ "$ENVIRONMENT" = "staging" ] || [ "$ENV" = "staging" ]; then
            LEEK_APP="funly-staging-leek"
        else
            LEEK_APP="funly-manage-test-leek"  # Default for test/dev
        fi
    fi
    
    if [ -z "$DJANGO_APP" ]; then
        if [ "$ENVIRONMENT" = "production" ] || [ "$ENV" = "prod" ]; then
            DJANGO_APP="funly-manage-prod"
        elif [ "$ENVIRONMENT" = "staging" ] || [ "$ENV" = "staging" ]; then
            DJANGO_APP="funly-manage-staging"
        else
            DJANGO_APP="funly-manage-test"  # Default for test/dev
        fi
    fi
fi

# Try to get config from Leek app if still not found
if [ -z "$DJANGO_APP" ] && [ -n "$LEEK_APP" ]; then
    echo -e "${YELLOW}🔍 Trying to get Django app name from Leek config...${NC}"
    DJANGO_APP=$(heroku config:get DEPLOYMENT_DJANGO_APP --app "$LEEK_APP" 2>/dev/null || echo "")
fi

echo -e "${BLUE}🔧 Environment Configuration:${NC}"
echo -e "${YELLOW}   Environment: ${ENVIRONMENT:-${ENV:-auto-detected}}${NC}"
echo -e "${YELLOW}   Leek App: $LEEK_APP${NC}"
echo -e "${YELLOW}   Django App: $DJANGO_APP${NC}"
echo -e "${YELLOW}   Sync Days: $DAYS_TO_SYNC${NC}"

# Validate configuration
if [ -z "$LEEK_APP" ]; then
    echo -e "${RED}❌ LEEK_APP not specified and could not be auto-detected${NC}"
    echo -e "${YELLOW}💡 Set LEEK_APP_NAME environment variable or run from heroku-setup.sh context${NC}"
    exit 1
fi

if [ -z "$DJANGO_APP" ]; then
    echo -e "${RED}❌ DJANGO_APP not specified and could not be auto-detected${NC}"
    echo -e "${YELLOW}💡 Set DJANGO_APP_NAME environment variable or run from heroku-setup.sh context${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Getting configuration...${NC}"

# Get Leek API secret
LEEK_API_SECRET=$(heroku config:get LEEK_AGENT_API_SECRET --app $LEEK_APP)
if [ -z "$LEEK_API_SECRET" ]; then
    echo -e "${RED}❌ Could not get Leek API secret${NC}"
    exit 1
fi

# Get Leek URL
LEEK_URL=$(heroku info --app $LEEK_APP | grep "Web URL" | awk '{print $3}' | sed 's/\/$//')
if [ -z "$LEEK_URL" ]; then
    echo -e "${RED}❌ Could not get Leek URL${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration obtained${NC}"
echo -e "${YELLOW}📡 Leek URL: ${LEEK_URL}${NC}"

# Wait for Leek to be ready
echo -e "${BLUE}⏳ Waiting for Leek to be ready...${NC}"
for i in {1..30}; do
    if curl -s "${LEEK_URL}/v1/events/process" \
        -H "x-leek-org-name: palnea.com" \
        -H "x-leek-app-name: funly" \
        -H "x-leek-app-env: prod" \
        -H "x-leek-app-key: ${LEEK_API_SECRET}" \
        > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Leek is ready!${NC}"
        break
    fi
    echo -e "${YELLOW}⏳ Attempt $i/30: Leek not ready yet, waiting...${NC}"
    sleep 10
done

if [ $i -eq 30 ]; then
    echo -e "${RED}❌ Leek failed to become ready after 5 minutes${NC}"
    exit 1
fi

# Create the sync command
echo -e "${BLUE}📝 Creating sync command...${NC}"

cat > /tmp/sync_command.py << EOF
"""
Run Django management command remotely via Heroku
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage.settings')
django.setup()

# Import and run the command
from django.core.management.base import BaseCommand
from django.core.management import call_command

try:
    call_command(
        'sync_tasks_to_leek',
        days=$DAYS_TO_SYNC,
        leek_url='$LEEK_URL',
        verbosity=2
    )
    print("✅ Sync completed successfully!")
except Exception as e:
    print(f"❌ Sync failed: {e}")
    sys.exit(1)
EOF

# Set environment variable for the Django app
echo -e "${BLUE}⚙️  Setting environment variables on Django app...${NC}"
heroku config:set LEEK_API_SECRET="$LEEK_API_SECRET" --app $DJANGO_APP

# Upload and run the sync command on Django app
echo -e "${BLUE}🚀 Running sync on Django app...${NC}"
heroku run python -c "
import os
import subprocess
import sys

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage.settings')

# Run the sync command
result = subprocess.run([
    'python', 'manage.py', 'sync_tasks_to_leek',
    '--days=$DAYS_TO_SYNC',
    '--leek-url=$LEEK_URL'
], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

sys.exit(result.returncode)
" --app $DJANGO_APP

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 Post-deployment sync completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}📊 Check your Leek dashboard:${NC} $LEEK_URL"
    echo -e "${YELLOW}📋 Historical tasks should now be visible${NC}"
else
    echo -e "${RED}❌ Post-deployment sync failed${NC}"
    echo "Check the logs above for details"
    exit 1
fi

# Clean up
rm -f /tmp/sync_command.py

echo -e "${GREEN}✨ All done!${NC}" 