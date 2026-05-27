"""Menu router — CRUD operations for menu items."""

from fastapi import APIRouter, HTTPException, status, Depends
from app.database import menu_collection, orders_collection
from app.models.menu import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from app.utils.deps import require_admin
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/api/menu", tags=["Menu"])


def serialize_item(item: dict) -> dict:
    """Convert MongoDB document to response-friendly dict."""
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "description": item["description"],
        "price": item["price"],
        "category": item["category"],
        "image_url": item.get("image_url", ""),
        "available": item.get("available", True),
        "is_recommended": item.get("is_recommended", False),
    }


@router.get("/", response_model=list[MenuItemResponse])
async def get_menu():
    """Get all menu items (public)."""
    items = await menu_collection.find().to_list(length=100)
    return [serialize_item(item) for item in items]


@router.get("/recommended", response_model=list[MenuItemResponse])
async def get_recommended_menu():
    """Get top recommended menu items based on admin curation and order frequency."""
    
    # 1. Fetch admin-curated recommendations
    admin_curated = await menu_collection.find({"is_recommended": True}).to_list(length=100)
    recommended_items = [serialize_item(item) for item in admin_curated]
    
    # Track IDs we've already added to avoid duplicates
    added_ids = {item["id"] for item in recommended_items}
    
    # 2. Fill the rest with popular items from orders
    if len(recommended_items) < 4:
        limit = 4 - len(recommended_items)
        pipeline = [
            {"$unwind": "$items"},
            {"$group": {"_id": "$items.item_id", "total_ordered": {"$sum": "$items.quantity"}}},
            {"$sort": {"total_ordered": -1}},
            {"$limit": 10} # Fetch a bit more to filter out already added ones
        ]
        
        popular_item_docs = await orders_collection.aggregate(pipeline).to_list(length=10)
        
        for doc in popular_item_docs:
            if len(recommended_items) >= 4:
                break
                
            if ObjectId.is_valid(doc["_id"]) and str(doc["_id"]) not in added_ids:
                item = await menu_collection.find_one({"_id": ObjectId(doc["_id"])})
                if item:
                    recommended_items.append(serialize_item(item))
                    added_ids.add(str(doc["_id"]))
                    
    return recommended_items


@router.get("/category/{category}", response_model=list[MenuItemResponse])
async def get_menu_by_category(category: str):
    """Get menu items filtered by category (public)."""
    items = await menu_collection.find({"category": category}).to_list(length=100)
    return [serialize_item(item) for item in items]


@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(item: MenuItemCreate, admin=Depends(require_admin)):
    """Add a new menu item (Admin only)."""
    item_doc = {
        **item.model_dump(),
        "category": item.category.value,
        "created_at": datetime.now(timezone.utc),
    }
    result = await menu_collection.insert_one(item_doc)
    item_doc["_id"] = result.inserted_id
    return serialize_item(item_doc)


@router.put("/{item_id}", response_model=MenuItemResponse)
async def update_menu_item(item_id: str, item: MenuItemUpdate, admin=Depends(require_admin)):
    """Update an existing menu item (Admin only)."""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    update_data = {k: v for k, v in item.model_dump().items() if v is not None}
    if "category" in update_data and hasattr(update_data["category"], "value"):
        update_data["category"] = update_data["category"].value

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await menu_collection.find_one_and_update(
        {"_id": ObjectId(item_id)},
        {"$set": update_data},
        return_document=True,
    )

    if not result:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return serialize_item(result)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(item_id: str, admin=Depends(require_admin)):
    """Delete a menu item (Admin only)."""
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid item ID")

    result = await menu_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
