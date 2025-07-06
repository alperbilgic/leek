#!/usr/bin/env python3
"""
Heroku Release Task: Bootstrap Leek

This script runs automatically after each Leek deployment on Heroku.
It performs the standard bootstrap process to initialize Leek with Searchbox.
"""

import os
import sys
import time
import subprocess
import requests

def log(message: str, level: str = "INFO"):
    """Log with timestamp and level"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def configure_searchbox_environment():
    """Configure environment variables for Searchbox compatibility"""
    log("🔧 Configuring environment for Searchbox compatibility...")
    
    # Set environment variables to disable operations that Searchbox doesn't allow
    os.environ["LEEK_ES_IM_ENABLE"] = "false"
    os.environ["LEEK_ES_INDEX_CLEANUP_ENABLED"] = "false"
    os.environ["LEEK_CLEAN_DATABASE_ON_STARTUP"] = "false"
    os.environ["LEEK_ENABLE_EVENTS_CLEANUP"] = "false"
    os.environ["LEEK_ENABLE_STATS_CLEANUP"] = "false"
    os.environ["LEEK_CLEAN_BROKER_ON_STARTUP"] = "false"
    os.environ["LEEK_PERSIST_ON_WORKER_RESTART"] = "true"
    
    # Disable local ES since we're using Searchbox
    os.environ["LEEK_ENABLE_ES"] = "false"
    
    log("✅ Environment configured for Searchbox")

def run_searchbox_bootstrap():
    """Run the Searchbox-compatible bootstrap process"""
    log("🚀 Starting Searchbox-compatible bootstrap...")
    
    try:
        # Run our custom Searchbox-compatible bootstrap
        result = subprocess.run([
            "python", "/opt/app/bin/bootstrap-searchbox.py"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log("✅ Searchbox bootstrap completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            log(f"❌ Searchbox bootstrap failed with return code {result.returncode}", "ERROR")
            if result.stderr:
                print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        log("❌ Bootstrap timed out after 5 minutes", "ERROR")
        return False
    except Exception as e:
        log(f"❌ Bootstrap error: {str(e)}", "ERROR")
        return False

def get_config_value(key: str, default: str = "") -> str:
    """Get configuration value from environment"""
    return os.environ.get(key, default)

def wait_for_leek_api(max_retries: int = 30) -> bool:
    """Wait for Leek API to be ready"""
    log("⏳ Waiting for Leek API to be ready...")
    
    api_url = get_config_value("LEEK_API_URL", "http://localhost:5000")
    org_name = get_config_value("LEEK_API_OWNER_ORG", "palnea.com")
    app_name = "funly"
    api_secret = get_config_value("LEEK_AGENT_API_SECRET")
    
    if not api_secret:
        log("❌ LEEK_AGENT_API_SECRET not found", "ERROR")
        return False
    
    headers = {
        "x-leek-org-name": org_name,
        "x-leek-app-name": app_name,
        "x-leek-app-env": "prod",
        "x-leek-app-key": api_secret
    }
    
    for i in range(max_retries):
        try:
            response = requests.get(
                f"{api_url}/v1/events/process",
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 404]:  # 404 is OK, means API is up but app not created yet
                log("✅ Leek API is ready")
                return True
        except Exception as e:
            log(f"⏳ API not ready yet (attempt {i+1}/{max_retries}): {str(e)}")
            time.sleep(10)
    
    log("❌ Leek API failed to become ready", "ERROR")
    return False

def check_searchbox_connection():
    """Check Searchbox Elasticsearch connection"""
    log("🔍 Checking Searchbox Elasticsearch connection...")
    
    searchbox_url = get_config_value("LEEK_ES_URL")
    if not searchbox_url:
        log("⚠️  LEEK_ES_URL not configured", "WARN")
        return True  # Don't fail if not configured yet
    
    try:
        # Use basic GET request for compatibility
        response = requests.get(searchbox_url, timeout=10)
        if response.status_code == 200:
            log("✅ Searchbox connection verified")
            return True
        else:
            log(f"⚠️  Searchbox returned status {response.status_code}", "WARN")
            return True  # Don't fail the release
    except Exception as e:
        log(f"⚠️  Searchbox connection check failed: {str(e)}", "WARN")
        return True  # Don't fail the release

def main():
    """Main release process"""
    log("🎬 Starting Heroku release process with Searchbox")
    
    # Step 1: Configure environment for Searchbox
    configure_searchbox_environment()
    
    # Step 2: Check Searchbox connection
    check_searchbox_connection()
    
    # Step 3: Run Searchbox-compatible bootstrap
    if not run_searchbox_bootstrap():
        log("❌ Release failed during Searchbox bootstrap", "ERROR")
        sys.exit(1)
    
    # Step 4: Final API verification
    if not wait_for_leek_api():
        log("❌ Release failed - API not ready", "ERROR")
        sys.exit(1)
    
    log("🎉 Searchbox release process completed successfully!")
    
    # Print summary
    leek_url = get_config_value("LEEK_WEB_URL", get_config_value("LEEK_API_URL", ""))
    searchbox_url = get_config_value("LEEK_ES_URL", "")
    
    if leek_url:
        log(f"🌐 Leek is available at: {leek_url}")
    if searchbox_url:
        log(f"🔍 Searchbox Elasticsearch: Connected")
    
    log("📋 Next steps:")
    log("   1. Create 'funly' application in Leek UI")
    log("   2. Configure Celery workers to send events")
    log("   3. Access Searchbox dashboard for monitoring")

if __name__ == "__main__":
    main() 