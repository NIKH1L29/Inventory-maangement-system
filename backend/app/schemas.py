"""
Pydantic models for request/response validation.

These sit between the HTTP layer and the database - keeps bad data out.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --- Warehouse schemas ---

class WarehouseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Warehouse A"])


class WarehouseResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Inventory item schemas ---

class ItemCreate(BaseModel):
    item_name: str = Field(..., min_length=1, max_length=200)
    quantity: int = Field(..., ge=0)
    location: str = Field(..., min_length=1, max_length=100)


class ItemUpdate(BaseModel):
    quantity: int = Field(..., ge=0)


class ItemResponse(BaseModel):
    id: int
    item_name: str
    quantity: int
    warehouse_id: int
    location: str
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Natural language command ---

class CommandRequest(BaseModel):
    command: str = Field(
        ...,
        min_length=3,
        examples=['Add 50 units of "Dell Laptop" to warehouse A.']
    )


class CommandResponse(BaseModel):
    action: str
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    location: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    status: str
    message: Optional[str] = None


class InventorySummary(BaseModel):
    total_items: int
    total_quantity: int
    warehouses: int
    items: List[ItemResponse]
