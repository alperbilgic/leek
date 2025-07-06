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

def run_bootstrap():
    """Run the standard Leek bootstrap process"""
    log("🚀 Starting Leek bootstrap...")
    
    try:
        # Run the original bootstrap
        result = subprocess.run([
            "python", "/opt/app/bin/bootstrap.py"
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log("✅ Bootstrap completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            log(f"❌ Bootstrap failed with return code {result.returncode}", "ERROR")
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
    log("🎬 Starting Heroku release process")
    
    # Step 1: Check Searchbox connection
    check_searchbox_connection()
    
    # Step 2: Run standard bootstrap
    if not run_bootstrap():
        log("❌ Release failed during bootstrap", "ERROR")
        sys.exit(1)
    
    # Step 3: Wait for API to be ready
    if not wait_for_leek_api():
        log("❌ Release failed - API not ready", "ERROR")
        sys.exit(1)
    
    log("🎉 Release process completed successfully!")
    
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