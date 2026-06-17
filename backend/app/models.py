"""
SQLAlchemy table definitions.

Two tables is enough for v1:
  - warehouses: physical locations (Warehouse A, B, etc.)
  - inventory_items: what stock lives where
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One warehouse can hold many item rows
    items = relationship("InventoryItem", back_populates="warehouse", cascade="all, delete-orphan")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(200), nullable=False, index=True)
    quantity = Column(Integer, default=0, nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    warehouse = relationship("Warehouse", back_populates="items")

    # Same item name shouldn't appear twice in one warehouse - merge quantities instead
    __table_args__ = (
        UniqueConstraint("item_name", "warehouse_id", name="uq_item_warehouse"),
    )
