"""Orders router — placing orders, viewing history, and updating status."""

from fastapi import APIRouter, HTTPException, status, Depends
from app.database import orders_collection, menu_collection
from app.models.order import OrderCreate, OrderStatusUpdate, OrderResponse
from app.utils.deps import get_current_user, require_admin
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def serialize_order(order: dict) -> dict:
    """Convert MongoDB document to response-friendly dict."""
    return {
        "id": str(order["_id"]),
        "user_id": order["user_id"],
        "user_name": order.get("user_name", "Unknown"),
        "items": order["items"],
        "total": order["total"],
        "status": order["status"],
        "address": order.get("address", ""),
        "payment_method": order.get("payment_method", "Cash on Delivery"),
        "created_at": order["created_at"].isoformat() if isinstance(order["created_at"], datetime) else str(order["created_at"]),
    }


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(order: OrderCreate, user=Depends(get_current_user)):
    """Place a new order (Customer)."""
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")

    # Check database for item availability
    for item in order.items:
        if not ObjectId.is_valid(item.item_id):
            raise HTTPException(status_code=400, detail=f"Invalid item ID: {item.item_id}")
            
        db_item = await menu_collection.find_one({"_id": ObjectId(item.item_id)})
        if not db_item:
            raise HTTPException(status_code=404, detail=f"Item not found: {item.name}")
            
        if not db_item.get("available", True):
            raise HTTPException(status_code=400, detail=f"Item is currently out of stock: {db_item['name']}")

    total = sum(item.price * item.quantity for item in order.items)

    order_doc = {
        "user_id": str(user["_id"]),
        "user_name": user["name"],
        "items": [item.model_dump() for item in order.items],
        "total": round(total, 2),
        "status": "pending",
        "address": order.address,
        "payment_method": order.payment_method,
        "created_at": datetime.now(timezone.utc),
    }

    result = await orders_collection.insert_one(order_doc)
    order_doc["_id"] = result.inserted_id
    return serialize_order(order_doc)


@router.get("/my", response_model=list[OrderResponse])
async def get_my_orders(user=Depends(get_current_user)):
    """Get order history for the current user (Customer)."""
    orders = await orders_collection.find(
        {"user_id": str(user["_id"])}
    ).sort("created_at", -1).to_list(length=50)
    return [serialize_order(order) for order in orders]


@router.get("/all", response_model=list[OrderResponse])
async def get_all_orders(admin=Depends(require_admin)):
    """Get all orders (Admin only)."""
    orders = await orders_collection.find().sort("created_at", -1).to_list(length=200)
    return [serialize_order(order) for order in orders]


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: str, status_update: OrderStatusUpdate, admin=Depends(require_admin)):
    """Update the status of an order (Admin only)."""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")

    result = await orders_collection.find_one_and_update(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status_update.status.value}},
        return_document=True,
    )

    if not result:
        raise HTTPException(status_code=404, detail="Order not found")

    return serialize_order(result)
