"""Pydantic models for Order operations."""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"


class OrderItem(BaseModel):
    item_id: str
    name: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    items: List[OrderItem]
    address: str
    payment_method: str = "Cash on Delivery"


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    items: List[dict]
    total: float
    status: str
    address: str
    payment_method: str
    created_at: str
