"""
MongoDB connection module using Motor (async driver).
Provides a singleton database instance used across the application.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_URI, DATABASE_NAME

# Create the Motor client (connection pooling is handled automatically)
client = AsyncIOMotorClient(MONGODB_URI)

# Get the database instance
db = client[DATABASE_NAME]

# Collection references for convenience
users_collection = db["users"]
menu_collection = db["menu_items"]
orders_collection = db["orders"]
notices_collection = db["notices"]


async def init_db():
    """Initialize database indexes for performance and uniqueness constraints."""
    # Unique index on email for the users collection
    await users_collection.create_index("email", unique=True)
    # Index on category for fast menu filtering
    await menu_collection.create_index("category")
    # Index on user_id for fast order lookups
    await orders_collection.create_index("user_id")
    # Index on created_at for sorting notices
    await notices_collection.create_index("created_at")

    print("Database indexes initialized.")


async def close_db():
    """Close the MongoDB connection."""
    client.close()
    print("MongoDB connection closed.")
