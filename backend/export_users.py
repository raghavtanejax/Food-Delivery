"""
Utility script to automatically export all user data from MongoDB to a local JSON and CSV file.
You can run this script anytime to see all the users in your database.

Run: python export_users.py
"""

import asyncio
import json
import csv
import os
from datetime import datetime
from bson import ObjectId
from app.database import users_collection, init_db, close_db

# Custom JSON encoder to handle MongoDB ObjectIds and Datetimes
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def export_users():
    print("Connecting to database...")
    await init_db()
    
    # Fetch all users
    cursor = users_collection.find({})
    users = await cursor.to_list(length=None)
    
    # Remove password hashes for security so the file is safe to read
    for user in users:
        if "password" in user:
            user["password"] = "******** (hidden)"
            
    # 1. Export to JSON
    json_filename = "users_database_dump.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(users, f, cls=MongoJSONEncoder, indent=4)
        
    print(f"User data automatically saved to: {os.path.abspath(json_filename)}")
        
    # 2. Export to CSV (Excel compatible)
    if users:
        csv_filename = "users_database_dump.csv"
        
        # Extract all unique keys across all user documents for headers
        keys = ["_id", "name", "full_name", "email", "role", "phone_number", "dob", "created_at"]
        
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            for user in users:
                # Convert ObjectIds and Datetimes to strings for CSV
                row = {k: str(v) if isinstance(v, (ObjectId, datetime)) else v for k, v in user.items()}
                writer.writerow(row)
                
        print(f"User data automatically saved to: {os.path.abspath(csv_filename)}")
    else:
        print("No users found in the database.")
        
    await close_db()

if __name__ == "__main__":
    asyncio.run(export_users())
