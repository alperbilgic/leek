#!/usr/bin/env python3
"""
Heroku Release Task: Bootstrap Leek

This script runs automatically after each Leek deployment on Heroku.
It performs the standard bootstrap process to initialize Leek with Bonsai Elasticsearch.
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

def configure_bonsai_environment():
    """Configure environment variables for Bonsai Elasticsearch"""
    log("🔧 Configuring environment for Bonsai Elasticsearch...")
    
    # Enable all ES features since Bonsai supports full functionality
    os.environ["LEEK_ES_IM_ENABLE"] = "true"
    os.environ["LEEK_ES_INDEX_CLEANUP_ENABLED"] = "true"
    os.environ["LEEK_CLEAN_DATABASE_ON_STARTUP"] = "true"
    os.environ["LEEK_ENABLE_EVENTS_CLEANUP"] = "true"
    os.environ["LEEK_ENABLE_STATS_CLEANUP"] = "true"
    os.environ["LEEK_CLEAN_BROKER_ON_STARTUP"] = "true"
    os.environ["LEEK_PERSIST_ON_WORKER_RESTART"] = "true"
    
    # Disable local ES since we're using Bonsai
    os.environ["LEEK_ENABLE_ES"] = "false"
    
    # Enable auto app creation - Bonsai supports all ES operations
    os.environ["LEEK_CREATE_APP_IF_NOT_EXIST"] = "true"
    
    log("✅ Environment configured for Bonsai")

def run_bootstrap():
    """Run the standard Leek bootstrap process"""
    log("🚀 Starting Leek bootstrap...")
    
    try:
        # Run the standard bootstrap
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
    
    for i in range(max_retries):
        try:
            # Simple health check without triggering app creation
            response = requests.get(f"{api_url}/v1/applications/", timeout=10)
            if response.status_code in [200, 401, 403]:  # API is up (auth required is OK)
                log("✅ Leek API is ready")
                return True
        except Exception as e:
            log(f"⏳ API not ready yet (attempt {i+1}/{max_retries}): {str(e)}")
            time.sleep(10)
    
    log("❌ Leek API failed to become ready", "ERROR")
    return False

def check_bonsai_connection():
    """Check Bonsai Elasticsearch connection"""
    log("🔍 Checking Bonsai Elasticsearch connection...")
    
    bonsai_url = get_config_value("LEEK_ES_URL")
    if not bonsai_url:
        log("⚠️  LEEK_ES_URL not configured", "WARN")
        return True  # Don't fail if not configured yet
    
    try:
        response = requests.get(bonsai_url, timeout=10)
        if response.status_code == 200:
            log("✅ Bonsai connection verified")
            return True
        else:
            log(f"⚠️  Bonsai returned status {response.status_code}", "WARN")
            return True  # Don't fail the release
    except Exception as e:
        log(f"⚠️  Bonsai connection check failed: {str(e)}", "WARN")
        return True  # Don't fail the release

def main():
    """Main release process"""
    log("🎬 Starting Heroku release process with Bonsai Elasticsearch")
    
    # Step 1: Configure environment for Bonsai
    configure_bonsai_environment()
    
    # Step 2: Check Bonsai connection
    check_bonsai_connection()
    
    # Step 3: Run standard bootstrap
    if not run_bootstrap():
        log("❌ Release failed during bootstrap", "ERROR")
        sys.exit(1)
    
    # Step 4: Final API verification
    if not wait_for_leek_api():
        log("❌ Release failed - API not ready", "ERROR")
        sys.exit(1)
    
    log("🎉 Bonsai release process completed successfully!")
    
    # Print summary
    leek_url = get_config_value("LEEK_WEB_URL", get_config_value("LEEK_API_URL", ""))
    bonsai_url = get_config_value("LEEK_ES_URL", "")
    
    if leek_url:
        log(f"🌐 Leek is available at: {leek_url}")
    if bonsai_url:
        log(f"🔍 Bonsai Elasticsearch: Connected")
    
    log("📋 Next steps:")
    log("   1. Create 'funly' application via Leek UI or auto-creation")
    log("   2. Configure Celery workers to send events")
    log("   3. Access Bonsai dashboard for monitoring")

if __name__ == "__main__":
    main() 