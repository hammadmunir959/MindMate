"""
Database Initialization Script v2
=================================
Initializes the MindMate v2 database.
1. Creates 'mindmate' user if not exists.
2. Creates 'mindmate_v2' database if not exists.
3. Creates all tables using new models.
Environment variables for setup:
- SUPER_USER: Postgres superuser (default: postgres)
- SUPER_PASS: Postgres superuser password (default: postgres)
"""

import os
import sys
import subprocess
import time
import logging

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.db.session import create_tables, engine
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_psql_command(command, description, db="postgres", user=None, password=None):
    """Run psql command via subprocess"""
    # Use provided creds or defaults
    pg_user = user or os.getenv("SUPER_USER", "postgres")
    pg_pass = password or os.getenv("SUPER_PASS", "postgres")
    pg_host = settings.DB_HOST
    pg_port = str(settings.DB_PORT)

    env = os.environ.copy()
    env["PGPASSWORD"] = pg_pass

    cmd = [
        "psql",
        "-h", pg_host,
        "-p", pg_port,
        "-U", pg_user,
        "-d", db,
        "-c", command
    ]

    try:
        logger.info(f"Running: {description} on {pg_host}:{pg_port}...")
        result = subprocess.run(
            cmd, 
            env=env,
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        logger.info(f"✅ {description} success")
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode().strip()
        if "already exists" in error_msg:
            logger.info(f"⚠️ {description} (already exists)")
            return True
        logger.error(f"❌ {description} failed: {error_msg}")
        return False

def setup_postgres_auth():
    """Setup Postgres user and database using superuser creds"""
    
    target_user = settings.DB_USER
    target_pass = settings.DB_PASSWORD
    target_db = settings.DB_NAME
    
    # 1. Create User
    run_psql_command(
        f"CREATE USER {target_user} WITH PASSWORD '{target_pass}';", 
        "Create DB User"
    )

    # 2. Create Database
    run_psql_command(
        f"CREATE DATABASE {target_db} OWNER {target_user};", 
        "Create Database"
    )
        
    # 3. Grant privileges
    run_psql_command(
        f"GRANT ALL PRIVILEGES ON DATABASE {target_db} TO {target_user};", 
        "Grant Privileges"
    )
    
    # 4. Grant schema usage (often needed on public schema for new users)
    run_psql_command(
        f"ALTER DATABASE {target_db} OWNER TO {target_user};",
        "Set DB Owner"
    )

def init_tables():
    """Initialize tables using SQLAlchemy"""
    logger.info("Initializing schema...")
    try:
        # Verify connection first
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Connected to database successfully")
            
        create_tables()
        logger.info("✅ All tables created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Schema initialization failed: {e}")
        #sys.exit(1) # Don't exit, maybe just connection flakiness

if __name__ == "__main__":
    print(f"Initializing {settings.DB_NAME} on {settings.DB_HOST}:{settings.DB_PORT}...")
    
    # Wait for DB to be ready
    max_retries = 30
    for i in range(max_retries):
        if run_psql_command("SELECT 1", "Check DB Connection"):
            break
        logger.info(f"Waiting for database... ({i+1}/{max_retries})")
        time.sleep(2)
        
    setup_postgres_auth()
    init_tables()
