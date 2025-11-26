"""
Migration script to transfer data from SQLite (old bot.py) to MongoDB
Run this script if you have an existing users.db file and want to migrate to MongoDB
"""
import sqlite3
import logging
from database import db
from config import MONGODB_URI, DATABASE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")


def migrate_sqlite_to_mongodb(sqlite_path="users.db"):
    """
    Migrate users from SQLite database to MongoDB
    
    Args:
        sqlite_path: Path to the SQLite database file
    """
    try:
        # Connect to SQLite
        logger.info(f"Connecting to SQLite database: {sqlite_path}")
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Get all users from SQLite
        cursor.execute("SELECT chat_id, name FROM users")
        users = cursor.fetchall()
        conn.close()
        
        logger.info(f"Found {len(users)} users in SQLite database")
        
        if len(users) == 0:
            logger.warning("No users found in SQLite database")
            return
        
        # Migrate to MongoDB
        migrated = 0
        failed = 0
        
        for chat_id, name in users:
            try:
                db.add_or_update_user(chat_id, name or "")
                migrated += 1
                logger.info(f"Migrated user: {chat_id} - {name}")
            except Exception as e:
                failed += 1
                logger.error(f"Failed to migrate user {chat_id}: {e}")
        
        logger.info("=" * 50)
        logger.info("Migration Summary:")
        logger.info(f"  Total users in SQLite: {len(users)}")
        logger.info(f"  Successfully migrated: {migrated}")
        logger.info(f"  Failed: {failed}")
        logger.info("=" * 50)
        
        if migrated > 0:
            logger.info(f"✓ Migration completed successfully!")
            logger.info(f"✓ {migrated} users are now in MongoDB")
            logger.info(f"✓ Database: {DATABASE_NAME}")
            logger.info(f"✓ Connection: {MONGODB_URI}")
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        logger.error("Make sure users.db exists in the current directory")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("SQLite to MongoDB Migration Tool")
    print("=" * 60)
    print()
    print("This script will migrate users from users.db to MongoDB")
    print(f"Target MongoDB: {MONGODB_URI}")
    print(f"Target Database: {DATABASE_NAME}")
    print()
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        migrate_sqlite_to_mongodb()
    else:
        print("Migration cancelled")
