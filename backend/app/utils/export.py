"""
Utility to automatically dump MongoDB user data to local files.
"""

import json
import csv
import os
from datetime import datetime
from bson import ObjectId
from app.database import users_collection

class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def auto_export_users_to_file():
    """
    Fetches all users from the database and saves them to a JSON and CSV file.
    This runs automatically in the background whenever a user is created or updated.
    """
    try:
        cursor = users_collection.find({})
        users = await cursor.to_list(length=None)
        
        # Hide passwords
        for user in users:
            if "password" in user:
                user["password"] = "******** (hidden for security)"
                
        # Define paths at the root of the backend folder
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(backend_dir, "users_database_dump.json")
        csv_path = os.path.join(backend_dir, "users_database_dump.csv")
        
        # 1. Export JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(users, f, cls=MongoJSONEncoder, indent=4)
            
        # 2. Export CSV
        if users:
            keys = ["_id", "name", "full_name", "email", "role", "phone_number", "dob", "created_at"]
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
                writer.writeheader()
                for user in users:
                    row = {k: str(v) if isinstance(v, (ObjectId, datetime)) else v for k, v in user.items()}
                    writer.writerow(row)
                    
        print(f"Auto-exported {len(users)} users to local files.")
    except Exception as e:
        print(f"Error auto-exporting users: {e}")
