"""Orders router — placing orders, viewing history, and updating status."""

from fastapi import APIRouter, HTTPException, status, Depends
from app.database import orders_collection, menu_collection
from app.models.order import OrderCreate, OrderStatusUpdate, OrderResponse
from app.utils.deps import get_current_user, require_admin
from app.config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from bson import ObjectId
from datetime import datetime, timezone
from pydantic import BaseModel
import razorpay

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

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
        "payment_status": order.get("payment_status", "Pending"),
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

    payment_status = "Pending"
    if order.payment_method != "Cash on Delivery":
        if not order.razorpay_payment_id or not order.razorpay_order_id or not order.razorpay_signature:
            raise HTTPException(status_code=400, detail="Missing Razorpay payment details")
        
        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order.razorpay_order_id,
                'razorpay_payment_id': order.razorpay_payment_id,
                'razorpay_signature': order.razorpay_signature
            })
            payment_status = "Completed"
        except razorpay.errors.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid payment signature")

    order_doc = {
        "user_id": str(user["_id"]),
        "user_name": user["name"],
        "items": [item.model_dump() for item in order.items],
        "total": round(total, 2),
        "status": "pending",
        "address": order.address,
        "payment_method": order.payment_method,
        "payment_status": payment_status,
        "razorpay_payment_id": order.razorpay_payment_id,
        "razorpay_order_id": order.razorpay_order_id,
        "created_at": datetime.now(timezone.utc),
    }

    result = await orders_collection.insert_one(order_doc)
    order_doc["_id"] = result.inserted_id
    return serialize_order(order_doc)


class RazorpayOrderRequest(BaseModel):
    amount: float

@router.post("/create-razorpay-order")
async def create_razorpay_order(req: RazorpayOrderRequest, user=Depends(get_current_user)):
    """Create an order ID for Razorpay frontend popup."""
    try:
        # amount is in INR, Razorpay expects paise (multiply by 100)
        amount_in_paise = int(req.amount * 100)
        order_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"receipt_{user['_id']}_{int(datetime.now().timestamp())}",
            "payment_capture": 1
        }
        razorpay_order = razorpay_client.order.create(data=order_data)
        return {"order_id": razorpay_order["id"], "key_id": RAZORPAY_KEY_ID}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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
