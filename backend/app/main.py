"""
FastAPI application - Inventory Management System API.

Run locally:
    cd backend
    uvicorn app.main:app --reload --port 8000

Interactive docs at http://localhost:8000/docs
"""

import os
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, get_db, Base
from . import crud, models, schemas
from .command_parser import parse_command

# Create tables on startup - fine for SQLite demo; use Alembic in bigger projects
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory Management API",
    description="Track stock across warehouses. Supports REST endpoints and plain-English commands.",
    version="1.0.0",
)

# CORS - frontend URL comes from env when deployed (Netlify, GitHub Pages, etc.)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
origins_list = [o.strip() for o in allowed_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list if origins_list != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Quick sanity check - hit this before debugging the frontend."""
    return {
        "service": "Inventory Management API",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health_check():
    """Render/Railway health probes usually ping something like this."""
    return {"status": "healthy"}


# --- Warehouses ---

@app.get("/api/warehouses", response_model=List[schemas.WarehouseResponse])
def get_warehouses(db: Session = Depends(get_db)):
    return crud.list_warehouses(db)


@app.post("/api/warehouses", response_model=schemas.WarehouseResponse, status_code=201)
def create_warehouse(payload: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    existing = crud.get_warehouse_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=400, detail=f"Warehouse '{existing.name}' already exists.")
    warehouse = crud.get_or_create_warehouse(db, payload.name)
    db.commit()
    db.refresh(warehouse)
    return warehouse


# --- Inventory items (REST) ---

@app.get("/api/inventory", response_model=schemas.InventorySummary)
def get_inventory(location: Optional[str] = None, db: Session = Depends(get_db)):
    rows = crud.list_all_inventory(db, location=location)
    items = [schemas.ItemResponse(**crud.item_to_response(r)) for r in rows]
    total_qty = sum(i.quantity for i in items)
    warehouses = len(set(i.location for i in items))
    return schemas.InventorySummary(
        total_items=len(items),
        total_quantity=total_qty,
        warehouses=warehouses,
        items=items,
    )


@app.post("/api/items", response_model=schemas.ItemResponse, status_code=201)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")
    item = crud.add_stock(db, payload.item_name, payload.quantity, payload.location)
    return schemas.ItemResponse(**crud.item_to_response(item))


@app.put("/api/items/{item_id}", response_model=schemas.ItemResponse)
def update_item_quantity(item_id: int, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")
    item.quantity = payload.quantity
    db.commit()
    db.refresh(item)
    return schemas.ItemResponse(**crud.item_to_response(item))


@app.delete("/api/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    if not crud.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found.")
    return {"status": "success", "message": f"Item {item_id} deleted."}


# --- Natural language command endpoint (assignment example) ---

@app.post("/api/command", response_model=schemas.CommandResponse)
def execute_command(payload: schemas.CommandRequest, db: Session = Depends(get_db)):
    """
    Parses commands like:
        Add 50 units of "Dell Laptop" to warehouse A.

    Returns structured JSON with action, item_name, quantity, location, status.
    """
    try:
        parsed = parse_command(payload.command)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if parsed.action == "add_item":
            crud.add_stock(db, parsed.item_name, parsed.quantity, parsed.location)
            return schemas.CommandResponse(
                action="add_item",
                item_name=parsed.item_name,
                quantity=parsed.quantity,
                location=crud.normalize_warehouse_name(parsed.location),
                status="success",
                message=f"Added {parsed.quantity} units of {parsed.item_name}.",
            )

        if parsed.action == "remove_item":
            item = crud.remove_stock(db, parsed.item_name, parsed.quantity, parsed.location)
            return schemas.CommandResponse(
                action="remove_item",
                item_name=parsed.item_name,
                quantity=parsed.quantity,
                location=item.warehouse.name,
                status="success",
                message=f"Removed {parsed.quantity} units. Remaining: {item.quantity}.",
            )

        if parsed.action == "transfer_item":
            crud.transfer_stock(
                db,
                parsed.item_name,
                parsed.quantity,
                parsed.from_location,
                parsed.to_location,
            )
            return schemas.CommandResponse(
                action="transfer_item",
                item_name=parsed.item_name,
                quantity=parsed.quantity,
                from_location=crud.normalize_warehouse_name(parsed.from_location),
                to_location=crud.normalize_warehouse_name(parsed.to_location),
                status="success",
                message=f"Transferred {parsed.quantity} units of {parsed.item_name}.",
            )

        if parsed.action == "list_inventory":
            rows = crud.list_all_inventory(db, location=parsed.location)
            loc_label = crud.normalize_warehouse_name(parsed.location) if parsed.location else "all warehouses"
            return schemas.CommandResponse(
                action="list_inventory",
                location=loc_label,
                status="success",
                message=f"Found {len(rows)} item(s) in {loc_label}.",
            )

        if parsed.action == "list_warehouses":
            whs = crud.list_warehouses(db)
            return schemas.CommandResponse(
                action="list_warehouses",
                status="success",
                message=f"Registered warehouses: {', '.join(w.name for w in whs) or 'none yet'}.",
            )

        raise HTTPException(status_code=400, detail=f"Unknown action: {parsed.action}")

    except ValueError as e:
        return schemas.CommandResponse(
            action=parsed.action,
            item_name=parsed.item_name,
            quantity=parsed.quantity,
            location=parsed.location,
            status="failed",
            message=str(e),
        )
