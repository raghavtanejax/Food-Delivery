"""
Seed script — Populates the database with dummy menu data and a default admin user.
Run: python -m app.seed
"""

import asyncio
from datetime import datetime, timezone
from app.database import db, init_db, close_db, menu_collection, users_collection
from app.utils.auth import hash_password


DUMMY_MENU = [
    # --- Starters ---
    {
        "name": "Paneer Tikka",
        "description": "Smoky, chargrilled cottage cheese cubes marinated in spiced yoghurt",
        "price": 249.0,
        "category": "starters",
        "image_url": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Chicken Seekh Kebab",
        "description": "Succulent minced chicken skewers with aromatic herbs & spices",
        "price": 299.0,
        "category": "starters",
        "image_url": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Crispy Spring Rolls",
        "description": "Golden-fried rolls stuffed with fresh veggies and glass noodles",
        "price": 179.0,
        "category": "starters",
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Masala Fries",
        "description": "Crispy French fries tossed in a tangy chaat masala blend",
        "price": 149.0,
        "category": "starters",
        "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    # --- Mains ---
    {
        "name": "Butter Chicken",
        "description": "Tender chicken in a rich, creamy tomato-butter gravy. Served with naan",
        "price": 349.0,
        "category": "mains",
        "image_url": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Dal Makhani",
        "description": "Slow-cooked black lentils simmered in butter and cream overnight",
        "price": 269.0,
        "category": "mains",
        "image_url": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Chicken Biryani",
        "description": "Fragrant basmati rice layered with spiced chicken, saffron & fried onions",
        "price": 329.0,
        "category": "mains",
        "image_url": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Paneer Butter Masala",
        "description": "Soft cottage cheese cubes in a velvety onion-tomato makhani sauce",
        "price": 289.0,
        "category": "mains",
        "image_url": "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Veg Thali",
        "description": "Complete meal — dal, sabzi, raita, rice, roti, pickle & dessert",
        "price": 229.0,
        "category": "mains",
        "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    # --- Drinks ---
    {
        "name": "Mango Lassi",
        "description": "Creamy yoghurt smoothie blended with Alphonso mango pulp",
        "price": 129.0,
        "category": "drinks",
        "image_url": "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Masala Chai",
        "description": "Classic Indian spiced tea with ginger, cardamom & cinnamon",
        "price": 69.0,
        "category": "drinks",
        "image_url": "https://images.unsplash.com/photo-1571934811356-5cc061b6821f?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Fresh Lime Soda",
        "description": "Zesty lime juice with soda, a pinch of salt & a dash of sugar",
        "price": 89.0,
        "category": "drinks",
        "image_url": "https://images.unsplash.com/photo-1513558161293-cdaf765ed514?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Cold Coffee",
        "description": "Chilled coffee blended with vanilla ice cream & chocolate drizzle",
        "price": 159.0,
        "category": "drinks",
        "image_url": "https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    # --- Desserts ---
    {
        "name": "Gulab Jamun",
        "description": "Warm, melt-in-mouth milk dumplings soaked in rose-cardamom syrup",
        "price": 129.0,
        "category": "desserts",
        "image_url": "https://images.unsplash.com/photo-1666190050726-f622cf37ee56?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
    {
        "name": "Rasmalai",
        "description": "Soft chenna discs floating in saffron-infused sweetened milk",
        "price": 149.0,
        "category": "desserts",
        "image_url": "https://images.unsplash.com/photo-1645177628172-a94c1f96e6db?w=400",
        "available": True,
        "created_at": datetime.now(timezone.utc),
    },
]

DEFAULT_ADMIN = {
    "name": "Restaurant Admin",
    "email": "admin@foodie.com",
    "password": hash_password("admin123"),
    "role": "admin",
    "created_at": datetime.now(timezone.utc),
}


async def seed():
    """Seed the database with dummy data."""
    await init_db()

    # Seed admin user
    existing_admin = await users_collection.find_one({"email": DEFAULT_ADMIN["email"]})
    if not existing_admin:
        await users_collection.insert_one(DEFAULT_ADMIN)
        print("Default admin created: admin@foodie.com / admin123")
    else:
        print("Admin already exists, skipping.")

    # Seed menu items
    count = await menu_collection.count_documents({})
    if count == 0:
        await menu_collection.insert_many(DUMMY_MENU)
        print(f"Seeded {len(DUMMY_MENU)} menu items.")
    else:
        print(f"Menu already has {count} items, skipping.")

    await close_db()
    print("\nSeed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
