"""
Database operations - all the boring SQL lives here so routes stay thin.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models


def normalize_warehouse_name(name: str) -> str:
    """
    Makes 'warehouse a', 'Warehouse A', 'A', 'WAREHOUSE A' all resolve consistently.
    Commands often extract just the letter after 'warehouse'.
    """
    cleaned = name.strip()
    if not cleaned:
        return "Warehouse"

    if cleaned.lower().startswith("warehouse "):
        suffix = cleaned[10:].strip()
        return f"Warehouse {suffix.title()}" if suffix else "Warehouse"

    # Shorthand from parser: "A" -> "Warehouse A"
    return f"Warehouse {cleaned.title()}"


def get_or_create_warehouse(db: Session, name: str) -> models.Warehouse:
    """Find warehouse by name or create it on the fly."""
    normalized = normalize_warehouse_name(name)
    warehouse = db.query(models.Warehouse).filter(
        func.lower(models.Warehouse.name) == normalized.lower()
    ).first()

    if not warehouse:
        warehouse = models.Warehouse(name=normalized)
        db.add(warehouse)
        db.flush()  # get id without full commit yet

    return warehouse


def get_warehouse_by_name(db: Session, name: str) -> Optional[models.Warehouse]:
    normalized = normalize_warehouse_name(name)
    return db.query(models.Warehouse).filter(
        func.lower(models.Warehouse.name) == normalized.lower()
    ).first()


def list_warehouses(db: Session) -> List[models.Warehouse]:
    return db.query(models.Warehouse).order_by(models.Warehouse.name).all()


def get_inventory_item(db: Session, item_name: str, warehouse_id: int) -> Optional[models.InventoryItem]:
    return db.query(models.InventoryItem).filter(
        func.lower(models.InventoryItem.item_name) == item_name.lower(),
        models.InventoryItem.warehouse_id == warehouse_id
    ).first()


def add_stock(db: Session, item_name: str, quantity: int, location: str) -> models.InventoryItem:
    """
    Adds units to a warehouse. If the item already exists there, we bump quantity.
    """
    warehouse = get_or_create_warehouse(db, location)
    existing = get_inventory_item(db, item_name, warehouse.id)

    if existing:
        existing.quantity += quantity
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    new_item = models.InventoryItem(
        item_name=item_name.strip(),
        quantity=quantity,
        warehouse_id=warehouse.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


def remove_stock(db: Session, item_name: str, quantity: int, location: str) -> models.InventoryItem:
    """
    Pulls stock from a warehouse. Raises ValueError if not enough on hand.
    """
    warehouse = get_warehouse_by_name(db, location)
    if not warehouse:
        raise ValueError(f"Warehouse '{normalize_warehouse_name(location)}' not found.")

    item = get_inventory_item(db, item_name, warehouse.id)
    if not item:
        raise ValueError(f"'{item_name}' not found in {warehouse.name}.")

    if item.quantity < quantity:
        raise ValueError(
            f"Not enough stock. Have {item.quantity}, tried to remove {quantity}."
        )

    item.quantity -= quantity
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


def transfer_stock(
    db: Session,
    item_name: str,
    quantity: int,
    from_location: str,
    to_location: str
) -> tuple:
    """Move units between two warehouses in one transaction."""
    remove_stock(db, item_name, quantity, from_location)
    added = add_stock(db, item_name, quantity, to_location)
    return added


def list_all_inventory(db: Session, location: Optional[str] = None) -> List[models.InventoryItem]:
    query = db.query(models.InventoryItem).join(models.Warehouse)

    if location:
        normalized = normalize_warehouse_name(location)
        query = query.filter(func.lower(models.Warehouse.name) == normalized.lower())

    return query.order_by(models.Warehouse.name, models.InventoryItem.item_name).all()


def delete_item(db: Session, item_id: int) -> bool:
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


def item_to_response(item: models.InventoryItem) -> dict:
    """Helper to shape DB row into API-friendly dict with location name."""
    return {
        "id": item.id,
        "item_name": item.item_name,
        "quantity": item.quantity,
        "warehouse_id": item.warehouse_id,
        "location": item.warehouse.name,
        "updated_at": item.updated_at,
    }
