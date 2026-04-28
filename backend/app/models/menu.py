"""Pydantic models for Menu Item operations."""

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class MenuCategory(str, Enum):
    STARTERS = "starters"
    MAINS = "mains"
    DRINKS = "drinks"
    DESSERTS = "desserts"


class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    category: MenuCategory
    image_url: Optional[str] = ""
    available: bool = True


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[MenuCategory] = None
    image_url: Optional[str] = None
    available: Optional[bool] = None


class MenuItemResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: str
    available: bool
