#!/usr/bin/env python3
"""
Heroku Release Task: Bootstrap Leek and Auto-Sync Django Data

This script runs automatically after each Leek deployment on Heroku.
It performs the standard bootstrap and then syncs historical data from Django.
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

def trigger_django_sync() -> bool:
    """Trigger Django sync by calling the Django app"""
    log("🔄 Starting Django to Leek sync...")
    
    # Get configuration
    leek_app = get_config_value("DEPLOYMENT_LEEK_APP")
    django_app = get_config_value("DEPLOYMENT_DJANGO_APP")
    sync_days = get_config_value("SYNC_DAYS", "30")
    leek_url = get_config_value("LEEK_API_URL", "http://localhost:5000")
    api_secret = get_config_value("LEEK_AGENT_API_SECRET")
    
    if not django_app:
        log("⚠️  No Django app configured, skipping sync", "WARN")
        return True
    
    if not api_secret:
        log("❌ LEEK_AGENT_API_SECRET not found", "ERROR")
        return False
    
    log(f"🔧 Configuration:")
    log(f"   Leek App: {leek_app}")
    log(f"   Django App: {django_app}")
    log(f"   Sync Days: {sync_days}")
    log(f"   Leek URL: {leek_url}")
    
    # Prepare the Django management command
    sync_command = [
        "python", "manage.py", "sync_django_to_leek",
        f"--days={sync_days}",
        f"--leek-url={leek_url}",
        "--org-name=palnea.com",
        "--app-name=funly",
        "--app-env=prod"
    ]
    
    # Set environment variables for the Django command
    env = os.environ.copy()
    env["LEEK_API_SECRET"] = api_secret
    env["LEEK_URL"] = leek_url
    
    try:
        log("📡 Executing sync command on Django app...")
        
        # Construct the proper heroku run command with environment variables
        heroku_run_command = [
            "heroku", "run",
            "--app", django_app,
            "--exit-code",
            "-e", f"LEEK_API_SECRET={api_secret}",
            "-e", f"LEEK_URL={leek_url}",
            "--"
        ] + sync_command
        
        log(f"🚀 Running: {' '.join(heroku_run_command)}")
        
        result = subprocess.run(
            heroku_run_command,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
            env=env
        )
        
        if result.returncode == 0:
            log("✅ Django sync completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            log(f"❌ Django sync failed with return code {result.returncode}", "ERROR")
            if result.stderr:
                print(result.stderr)
            # Don't fail the release if sync fails - Leek is still functional
            log("⚠️  Continuing despite sync failure - Leek is operational", "WARN")
            return True
            
    except subprocess.TimeoutExpired:
        log("❌ Django sync timed out after 10 minutes", "ERROR")
        return True  # Don't fail the release
    except Exception as e:
        log(f"❌ Django sync error: {str(e)}", "ERROR")
        return True  # Don't fail the release

def main():
    """Main release process"""
    log("🎬 Starting Heroku release process with auto-sync")
    
    # Step 1: Run standard bootstrap
    if not run_bootstrap():
        log("❌ Release failed during bootstrap", "ERROR")
        sys.exit(1)
    
    # Step 2: Wait for API to be ready
    if not wait_for_leek_api():
        log("❌ Release failed - API not ready", "ERROR")
        sys.exit(1)
    
    # Step 3: Trigger Django sync
    if not trigger_django_sync():
        log("⚠️  Sync failed but continuing with release", "WARN")
    
    log("🎉 Release process completed successfully!")
    
    # Print summary
    leek_url = get_config_value("LEEK_WEB_URL", get_config_value("LEEK_API_URL", ""))
    if leek_url:
        log(f"🌐 Leek is available at: {leek_url}")
    
    log("📋 Next steps:")
    log("   1. Create 'funly' application in Leek UI")
    log("   2. Configure Celery workers to send events")
    log("   3. Check that historical tasks are visible")

if __name__ == "__main__":
    main() 