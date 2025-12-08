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
            
            # Build the update document
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
                    "phone_number": None  # Initialize phone number as None for new users
                }
            }

            # Handle message_count to avoid conflicts between $setOnInsert and $inc
            if activity_type == "message":
                # Use $inc which will auto-initialize to 0 then increment to 1 for new users
                update_doc["$inc"] = {"message_count": 1}
            else:
                # For non-message activities, just initialize to 0 for new users
                update_doc["$setOnInsert"]["message_count"] = 0

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
                "phone_number": 1,
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
                    user.get("status", "unknown"),
                    user.get("phone_number", "")
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
        return [(user[0], user[1]) for user in users]
    
    def get_users_with_phones(self):
        """
        Get all users with their phone numbers for export
        
        Returns:
            List of tuples (chat_id, name, phone_number, phone_verified_at)
        """
        try:
            users = self.users_collection.find(
                {},
                {
                    "chat_id": 1,
                    "name": 1,
                    "phone_number": 1,
                    "phone_verified_at": 1,
                    "joined_at": 1,
                    "_id": 0
                }
            ).sort("name", 1)
            
            users_list = []
            for user in users:
                users_list.append((
                    user.get("chat_id"),
                    user.get("name", ""),
                    user.get("phone_number", ""),
                    user.get("phone_verified_at"),
                    user.get("joined_at")
                ))
            
            return users_list
        except Exception as e:
            logger.error(f"Failed to get users with phones: {e}")
            return []

    def get_users_without_phone(self):
        """
        Get all users who don't have a phone number
        
        Returns:
            List of chat_ids
        """
        try:
            # Find users where phone_number is null or empty string or doesn't exist
            query = {
                "$or": [
                    {"phone_number": None},
                    {"phone_number": ""},
                    {"phone_number": {"$exists": False}}
                ]
            }
            users = self.users_collection.find(query, {"chat_id": 1, "_id": 0})
            return [user["chat_id"] for user in users]
        except Exception as e:
            logger.error(f"Failed to get users without phone: {e}")
            return []
    
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

    def find_users_by_phone(self, phone: str):
        """
        Find users by phone number
        
        Args:
            phone: Phone number to search for (exact or partial match)
            
        Returns:
            List of tuples (chat_id, name)
        """
        try:
            # Clean phone number - remove spaces, dashes, etc
            cleaned_phone = str(phone).strip()
            
            # Try exact match first
            user = self.users_collection.find_one(
                {"phone_number": cleaned_phone},
                {"chat_id": 1, "name": 1, "_id": 0}
            )
            
            if user:
                return [(user["chat_id"], user.get("name", ""))]
            
            # If no exact match, try partial match
            pattern = {"$regex": cleaned_phone, "$options": "i"}
            users = self.users_collection.find(
                {"phone_number": pattern},
                {"chat_id": 1, "name": 1, "_id": 0}
            )
            return [(user["chat_id"], user.get("name", "")) for user in users]
        except Exception as e:
            logger.error(f"Failed to find users by phone '{phone}': {e}")
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
    
    def has_phone_number(self, chat_id: int) -> bool:
        """
        Check if user has a phone number saved
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            True if phone number exists and is not None, False otherwise
        """
        try:
            user = self.users_collection.find_one(
                {"chat_id": chat_id},
                {"phone_number": 1, "_id": 0}
            )
            if user and user.get("phone_number"):
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to check phone number for user {chat_id}: {e}")
            return False
    
    def save_phone_number(self, chat_id: int, phone_number: str):
        """
        Save user's phone number
        
        Args:
            chat_id: Telegram chat ID
            phone_number: User's phone number
        """
        try:
            result = self.users_collection.update_one(
                {"chat_id": chat_id},
                {
                    "$set": {
                        "phone_number": phone_number,
                        "phone_verified_at": datetime.utcnow()
                    }
                }
            )
            if result.modified_count > 0 or result.matched_count > 0:
                logger.info(f"Phone number saved for user {chat_id}: {phone_number}")
            else:
                logger.warning(f"User {chat_id} not found when saving phone number")
        except Exception as e:
            logger.error(f"Failed to save phone number for user {chat_id}: {e}")
            raise
    
    def get_user_phone(self, chat_id: int) -> str:
        """
        Get user's phone number
        
        Args:
            chat_id: Telegram chat ID
            
        Returns:
            Phone number string or None if not found
        """
        try:
            user = self.users_collection.find_one(
                {"chat_id": chat_id},
                {"phone_number": 1, "_id": 0}
            )
            return user.get("phone_number") if user else None
        except Exception as e:
            logger.error(f"Failed to get phone number for user {chat_id}: {e}")
            return None
    
    
    def update_system_stats(self, sent=0, failed=0):
        """
        Update global system statistics
        
        Args:
            sent: Number of successful messages to add
            failed: Number of failed messages to add
        """
        try:
            self.db.system_stats.update_one(
                {"_id": "global_stats"},
                {
                    "$inc": {
                        "total_sent": sent,
                        "total_failed": failed,
                        "total_messages": sent + failed
                    },
                    "$set": {"last_updated": datetime.utcnow()}
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to update system stats: {e}")

    def get_system_stats(self):
        """
        Get global system statistics
        
        Returns:
            Dict with total_sent, total_failed, total_messages
        """
        try:
            stats = self.db.system_stats.find_one({"_id": "global_stats"})
            if not stats:
                return {
                    "total_sent": 0,
                    "total_failed": 0,
                    "total_messages": 0
                }
            return {
                "total_sent": stats.get("total_sent", 0),
                "total_failed": stats.get("total_failed", 0),
                "total_messages": stats.get("total_messages", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {
                "total_sent": 0,
                "total_failed": 0,
                "total_messages": 0
            }

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
db = Database()
