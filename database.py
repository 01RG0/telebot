"""
Database module for MongoDB operations
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import logging
from config import MONGODB_URI, DATABASE_NAME, USERS_COLLECTION

logger = logging.getLogger("telegram_app.database")


class Database:
    """MongoDB database handler"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = None
        self.db = None
        self.users_collection = None
        self.connect()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            self.users_collection = self.db[USERS_COLLECTION]
            logger.info("Successfully connected to MongoDB")
            self._create_indexes()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary indexes for better performance"""
        try:
            # Create index on chat_id for faster lookups
            self.users_collection.create_index("chat_id", unique=True)
            # Create index on name for search functionality
            self.users_collection.create_index("name")
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def add_or_update_user(self, chat_id: int, name: str, activity_type: str = "message"):
        """
        Add a new user or update existing user's name and activity

        Args:
            chat_id: Telegram chat ID
            name: User's name
            activity_type: Type of activity (message, start, etc.)
        """
        try:
            now = datetime.utcnow()
            update_doc = {
                "$set": {
                    "name": name,
                    "updated_at": now,
                    "last_activity_at": now,
                    "last_activity_type": activity_type,
                    "status": "active"
                },
                "$setOnInsert": {
                    "joined_at": now,
                    "message_count": 0
                }
            }

            # Increment message count if it's a message activity
            if activity_type == "message":
                update_doc["$inc"] = {"message_count": 1}

            self.users_collection.update_one(
                {"chat_id": chat_id},
                update_doc,
                upsert=True
            )
            logger.info(f"User {chat_id} ({name}) added/updated with activity: {activity_type}")
        except Exception as e:
            logger.error(f"Failed to add/update user {chat_id}: {e}")
            raise
    
    def get_users(self, search=None, status_filter=None, page=1, per_page=50):
        """
        Get users with optional filtering, search, and pagination

        Args:
            search: Search term for name or chat_id
            status_filter: Filter by status (active, inactive)
            page: Page number (1-based)
            per_page: Users per page

        Returns:
            Tuple of (users_list, total_count, total_pages)
        """
        try:
            query = {}

            # Add search filter
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"chat_id": {"$regex": search}}
                ]

            # Add status filter
            if status_filter:
                query["status"] = status_filter

            # Get total count
            total_count = self.users_collection.count_documents(query)
            total_pages = (total_count + per_page - 1) // per_page

            # Get paginated results
            skip = (page - 1) * per_page
            users = self.users_collection.find(query, {
                "chat_id": 1, "name": 1, "joined_at": 1,
                "last_activity_at": 1, "message_count": 1, "status": 1,
                "_id": 0
            }).sort("last_activity_at", -1).skip(skip).limit(per_page)

            users_list = []
            for user in users:
                users_list.append((
                    user["chat_id"],
                    user.get("name", ""),
                    user.get("joined_at"),
                    user.get("last_activity_at"),
                    user.get("message_count", 0),
                    user.get("status", "unknown")
                ))

            return users_list, total_count, total_pages
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return [], 0, 0

    def get_users_simple(self):
        """
        Get all users sorted by name (legacy method for compatibility)

        Returns:
            List of tuples (chat_id, name)
        """
        users, _, _ = self.get_users()
        return [(chat_id, name) for chat_id, name, _, _, _, _ in users]
    
    def get_user_by_chat(self, chat_id: int):
        """
        Get user by chat ID
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Tuple (chat_id, name) or None if not found
        """
        try:
            user = self.users_collection.find_one({"chat_id": chat_id}, {"chat_id": 1, "name": 1, "_id": 0})
            if user:
                return (user["chat_id"], user.get("name", ""))
            return None
        except Exception as e:
            logger.error(f"Failed to get user {chat_id}: {e}")
            return None
    
    def find_users_by_name(self, name: str):
        """
        Find users by name (case-insensitive partial match)
        
        Args:
            name: Name to search for
            
        Returns:
            List of tuples (chat_id, name)
        """
        try:
            # Use regex for case-insensitive partial matching
            pattern = {"$regex": name, "$options": "i"}
            users = self.users_collection.find({"name": pattern}, {"chat_id": 1, "name": 1, "_id": 0})
            return [(user["chat_id"], user.get("name", "")) for user in users]
        except Exception as e:
            logger.error(f"Failed to find users by name '{name}': {e}")
            return []
    
    def delete_user(self, chat_id: int):
        """
        Delete a user from the database
        
        Args:
            chat_id: Telegram chat ID
        """
        try:
            result = self.users_collection.delete_one({"chat_id": chat_id})
            if result.deleted_count > 0:
                logger.info(f"User {chat_id} deleted successfully")
            else:
                logger.warning(f"User {chat_id} not found for deletion")
        except Exception as e:
            logger.error(f"Failed to delete user {chat_id}: {e}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
db = Database()
