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

    # Automatically create the default admin user if they don't exist
    from app.utils.auth import hash_password
    from datetime import datetime, timezone

    admin_email = "admin@foodie.com"
    existing_admin = await users_collection.find_one({"email": admin_email})
    
    if not existing_admin:
        admin_user = {
            "name": "Admin",
            "full_name": "System Administrator",
            "email": admin_email,
            "password": hash_password("admin123"),
            "role": "admin",
            "phone_number": "0000000000",
            "dob": "1990-01-01",
            "created_at": datetime.now(timezone.utc)
        }
        await users_collection.insert_one(admin_user)
        print(f"Default admin created automatically: {admin_email} / admin123")


async def close_db():
    """Close the MongoDB connection."""
    client.close()
    print("MongoDB connection closed.")
