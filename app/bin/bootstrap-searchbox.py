import json
import logging
import os
import subprocess
import requests
import time
from printy import printy
from elasticsearch import Elasticsearch

"""
Searchbox-Compatible Bootstrap Script for Leek
This version skips operations that are not allowed on managed Elasticsearch services.
"""

def get_bool(env_name, default="false"):
    return os.environ.get(env_name, default).lower() == "true"

def get_status(b):
    return "[n>]ENABLED@" if b else "[r>]DISABLED@"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)

# Environment variables
LEEK_VERSION = os.environ.get("LEEK_VERSION", "-.-.-")
LEEK_RELEASE_DATE = os.environ.get("LEEK_RELEASE_DATE", "0000/00/00 00:00:00")
LEEK_ENV = os.environ.get("LEEK_ENV", "PROD")
ENABLE_API = get_bool("LEEK_ENABLE_API")
ENABLE_AGENT = get_bool("LEEK_ENABLE_AGENT")
ENABLE_WEB = get_bool("LEEK_ENABLE_WEB")
LEEK_ES_URL = os.environ.get("LEEK_ES_URL", "http://0.0.0.0:9200")
LEEK_API_URL = os.environ.get("LEEK_API_URL", "http://0.0.0.0:5000")
LEEK_WEB_URL = os.environ.get("LEEK_WEB_URL", "http://0.0.0.0:8000")
LEEK_API_ENABLE_AUTH = get_bool("LEEK_API_ENABLE_AUTH", default="true")

LOGO = """
8 8888         8 8888888888   8 8888888888   8 8888     ,88'
8 8888         8 8888         8 8888         8 8888    ,88' 
8 8888         8 8888         8 8888         8 8888   ,88'  
8 8888         8 8888         8 8888         8 8888  ,88'   
8 8888         8 888888888888 8 888888888888 8 8888 ,88'    
8 8888         8 8888         8 8888         8 8888 88'     
8 8888         8 8888         8 8888         8 888888<      
8 8888         8 8888         8 8888         8 8888 `Y8.    
8 8888         8 8888         8 8888         8 8888   `Y8.  
8 888888888888 8 888888888888 8 888888888888 8 8888     `Y8.                        
"""

USAGE = f"""
[b>]|#|@     [y>]Leek Celery Monitoring Tool (Searchbox Edition)@       [b>]|#|@
[b>]|#|@     [n>]Versions:@ {LEEK_VERSION}                              [b>]|#|@
[b>]|#|@     [n>]Release date:@ {LEEK_RELEASE_DATE}                     [b>]|#|@
[b>]|#|@     [n>]Codename:@ Fennec                                      [b>]|#|@
[b>]|#|@     [n>]Repository:@ https://github.com/kodless/leek           [b>]|#|@
[b>]|#|@     [n>]Homepage:@ https://tryleek.com                         [b>]|#|@

[r>]Author:@ Hamza Adami <me@adamihamza.com>
[r>]Searchbox Compatible Version@ - Skips restricted operations
"""

SERVICES = f"""
[y>]SERVICE     STATUS      URL
=======     ------      ---@
- API       {get_status(ENABLE_API)}    {LEEK_API_URL}
- WEB       {get_status(ENABLE_WEB)}    {LEEK_WEB_URL}
- AGENT     {get_status(ENABLE_AGENT)}    -
"""

printy(LOGO, "n>B")
printy(USAGE)
printy(SERVICES)

def ensure_connection(target):
    """Ensure connection to a target URL"""
    for i in range(10):
        try:
            requests.options(url=target).raise_for_status()
            return
        except Exception as e:
            time.sleep(5)
            continue
    logger.error(f"Could not connect to target {target}")
    raise Exception(f"Connection failed to {target}")

def ensure_es_connection() -> Elasticsearch:
    """Ensure Elasticsearch connection with Searchbox compatibility"""
    logging.getLogger("elasticsearch").setLevel(logging.ERROR)
    conn = Elasticsearch(LEEK_ES_URL)
    for i in range(10):
        try:
            if conn.ping():
                logging.getLogger("elasticsearch").setLevel(logging.INFO)
                logger.info("✅ Connected to Searchbox Elasticsearch")
                return conn
        except Exception as e:
            logger.info(f"⏳ Waiting for Searchbox connection (attempt {i+1}/10)...")
            time.sleep(5)
    else:
        logger.error(f"Could not connect to Searchbox at {LEEK_ES_URL}")
        raise Exception(f"Searchbox connection failed")

def configure_web():
    """Configure web application"""
    if not ENABLE_WEB:
        return
        
    logger.info("🌐 Configuring web application...")
    
    if LEEK_API_ENABLE_AUTH:
        if LEEK_ENV == "PROD":
            LEEK_FIREBASE_PROJECT_ID = os.environ.get("LEEK_FIREBASE_PROJECT_ID")
            LEEK_FIREBASE_APP_ID = os.environ.get("LEEK_FIREBASE_APP_ID")
            LEEK_FIREBASE_API_KEY = os.environ.get("LEEK_FIREBASE_API_KEY")
            LEEK_FIREBASE_AUTH_DOMAIN = os.environ.get("LEEK_FIREBASE_AUTH_DOMAIN")
            
            none_fb_params = [LEEK_FIREBASE_PROJECT_ID, LEEK_FIREBASE_APP_ID, 
                             LEEK_FIREBASE_API_KEY, LEEK_FIREBASE_AUTH_DOMAIN].count(None)
            
            if 1 <= none_fb_params <= 3:
                raise Exception("Incomplete Firebase configuration")
            
            if none_fb_params == 4:
                logger.warning("Using default Firebase project for authentication!")
            
            web_conf = f"""
            window.leek_config = {{
                "LEEK_API_URL": "{LEEK_API_URL}",
                "LEEK_API_ENABLE_AUTH": "true",
                "LEEK_FIREBASE_PROJECT_ID": "{LEEK_FIREBASE_PROJECT_ID or 'kodhive-leek'}",
                "LEEK_FIREBASE_APP_ID": "{LEEK_FIREBASE_APP_ID or '1:894368938723:web:e14677d1835ce9bd09e3d6'}",
                "LEEK_FIREBASE_API_KEY": "{LEEK_FIREBASE_API_KEY or 'AIzaSyBiv9xF6VjDsv62ufzUb9aFJUreHQaFoDk'}",
                "LEEK_FIREBASE_AUTH_DOMAIN": "{LEEK_FIREBASE_AUTH_DOMAIN or 'kodhive-leek.firebaseapp.com'}",
                "LEEK_VERSION": "{LEEK_VERSION}",
            }};
            """
        else:
            logger.warning("Using default Firebase project for authentication!")
            web_conf = f"""
            window.leek_config = {{
                "LEEK_API_URL": "{LEEK_API_URL}",
                "LEEK_API_ENABLE_AUTH": "true",
                "LEEK_FIREBASE_PROJECT_ID": "kodhive-leek",
                "LEEK_FIREBASE_APP_ID": "1:894368938723:web:e14677d1835ce9bd09e3d6",
                "LEEK_FIREBASE_API_KEY": "AIzaSyBiv9xF6VjDsv62ufzUb9aFJUreHQaFoDk",
                "LEEK_FIREBASE_AUTH_DOMAIN": "kodhive-leek.firebaseapp.com",
                "LEEK_VERSION": "{LEEK_VERSION}",
            }};
            """
    else:
        web_conf = f"""
        window.leek_config = {{
            "LEEK_API_URL": "{LEEK_API_URL}",
            "LEEK_API_ENABLE_AUTH": "false",
            "LEEK_VERSION": "{LEEK_VERSION}",
        }};
        """
    
    web_conf_file = "/opt/app/public/leek-config.js"
    with open(web_conf_file, 'w') as f:
        f.write(web_conf)
    
    logger.info("✅ Web configuration complete")

def configure_agent():
    """Configure agent subscriptions"""
    if not ENABLE_AGENT:
        return
    
    logger.info("🤖 Configuring agent subscriptions...")
    
    subscriptions_file = "/opt/app/conf/subscriptions.json"
    subscriptions = os.environ.get("LEEK_AGENT_SUBSCRIPTIONS")
    
    if subscriptions:
        try:
            subscriptions = json.loads(subscriptions)
        except json.decoder.JSONDecodeError:
            raise Exception("Invalid LEEK_AGENT_SUBSCRIPTIONS JSON")
        
        # Add API URL and key if running in same container
        if ENABLE_API:
            for subscription in subscriptions:
                subscription["app_key"] = os.environ.get("LEEK_AGENT_API_SECRET")
                subscription["api_url"] = "http://0.0.0.0:5000"
        
        with open(subscriptions_file, 'w') as f:
            json.dump(subscriptions, f, indent=4, sort_keys=False)
    else:
        # Try to load from file
        try:
            with open(subscriptions_file) as s:
                subscriptions = json.load(s)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            subscriptions = []
        
        if not subscriptions:
            logger.warning("No agent subscriptions configured")
        
        with open(subscriptions_file, 'w') as f:
            json.dump(subscriptions, f, indent=4, sort_keys=False)
    
    logger.info("✅ Agent configuration complete")

def main():
    """Main bootstrap process for Searchbox"""
    try:
        logger.info("🚀 Starting Searchbox-compatible bootstrap...")
        
        # Configure web application
        configure_web()
        
        # Configure agent
        configure_agent()
        
        if ENABLE_API:
            # Test Searchbox connection (basic ping)
            logger.info("🔍 Testing Searchbox connection...")
            connection = ensure_es_connection()
            connection.close()
            
            # Start API process
            logger.info("🚀 Starting API service...")
            subprocess.run(["supervisorctl", "start", "api"])
            
            # Wait for API to be ready
            logger.info("⏳ Waiting for API to be ready...")
            ensure_connection("http://0.0.0.0:5000/v1/events/process")
            logger.info("✅ API service ready")
        
        if ENABLE_AGENT:
            logger.info("🚀 Starting Agent service...")
            subprocess.run(["supervisorctl", "start", "agent"])
            logger.info("✅ Agent service started")
        
        if ENABLE_WEB:
            logger.info("🚀 Starting Web service...")
            subprocess.run(["supervisorctl", "start", "web"])
            logger.info("✅ Web service started")
        
        logger.info("🎉 Searchbox-compatible bootstrap completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Bootstrap failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 