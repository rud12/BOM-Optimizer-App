from fastapi import HTTPException
from sqlalchemy import func
from decimal import Decimal

from models import BOM, BOMItem
from services.file_service import read_component_file
from services.vendor_service import search_all_products, vendor_id_from_product, get_vendor


def create_bom(db, name):
    if not name.strip():
        raise HTTPException(status_code=400, detail="BOM name is required")
    bom = BOM(name=name.strip())
    db.add(bom)
    db.commit()
    db.refresh(bom)
    return bom


def list_boms(db):
    return db.query(BOM).order_by(BOM.created_at.desc()).all()


def get_bom(db, bom_id):
    bom = db.query(BOM).filter(BOM.id == bom_id).first()
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    return bom


def delete_bom(db, bom_id):
    bom = get_bom(db, bom_id)
    db.delete(bom)
    db.commit()


def recalculate_bom(db, bom):
    total = db.query(func.coalesce(func.sum(BOMItem.total_price), 0)).filter(BOMItem.bom_id == bom.id).scalar()
    bom.total_cost = total
    db.commit()
    db.refresh(bom)


def find_existing_item(db, bom_id, alias_name, component_name, vendor_id):
    query = db.query(BOMItem).filter(
        BOMItem.bom_id == bom_id,
        func.lower(BOMItem.alias_name) == alias_name.strip().lower(),
        func.lower(BOMItem.component_name) == component_name.strip().lower(),
    )
    if vendor_id:
        query = query.filter(BOMItem.vendor_id == vendor_id)
    else:
        query = query.filter(BOMItem.vendor_id.is_(None))
    return query.first()


def save_or_increment_item(db, bom, item_data):
    existing = find_existing_item(
        db,
        bom.id,
        item_data["alias_name"],
        item_data["component_name"],
        item_data.get("vendor_id"),
    )
    if existing:
        existing.quantity += item_data["quantity"]
        existing.total_price = existing.unit_price * existing.quantity
        db.commit()
        recalculate_bom(db, bom)
        db.refresh(existing)
        return existing

    item = BOMItem(bom_id=bom.id, **item_data)
    db.add(item)
    db.commit()
    recalculate_bom(db, bom)
    db.refresh(item)
    return item


def add_bom_item(db, bom_id, payload):
    bom = get_bom(db, bom_id)

    vendor_id = payload.vendor_id
    if not vendor_id and payload.vendor_name:
        vendor = get_vendor(db, payload.vendor_name)
        vendor_id = vendor.id if vendor else None

    unit_price = Decimal(str(payload.unit_price))
    quantity = max(payload.quantity, 1)
    component_name = payload.component_name.strip()
    alias_name = (payload.alias_name or component_name).strip() or component_name
    return save_or_increment_item(
        db,
        bom,
        {
            "component_name": component_name,
            "alias_name": alias_name,
            "quantity": quantity,
            "vendor_id": vendor_id,
            "manufacturer": payload.manufacturer,
            "unit_price": unit_price,
            "total_price": unit_price * quantity,
            "stock": payload.stock,
            "product_url": payload.product_url,
        },
    )


def list_bom_items(db, bom_id):
    bom = get_bom(db, bom_id)
    return bom.items


def delete_bom_item(db, bom_id, item_id):
    bom = get_bom(db, bom_id)
    item = db.query(BOMItem).filter(BOMItem.id == item_id, BOMItem.bom_id == bom_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    recalculate_bom(db, bom)


def item_data_from_search(db, component, quantity):
    results = search_all_products(component)
    best = results[0] if results else None
    min_price = float("inf")
    for r in results:
        price = float("inf")
        for p in r["moq"]:
            if p["BreakQuantity"] <= quantity:
                price = p["UnitPrice"]
            else:
                break
        if price < min_price:
            min_price = price
            best = r
    if not best or min_price == float("inf"):
        return None

    unit_price = min_price
    return {
        "component_name": best["component_name"],
        "alias_name": component,
        "quantity": quantity,
        "vendor_id": vendor_id_from_product(db, best),
        "manufacturer": best["manufacturer"],
        "unit_price": unit_price,
        "total_price": unit_price * quantity,
        "stock": best["stock"],
        "product_url": best["product_url"],
    }


def import_bom_items(db, bom_id, file_bytes, file_name):
    bom = get_bom(db, bom_id)
    rows = read_component_file(file_bytes, file_name)
    missing_items = []

    for row in rows:
        item_data = item_data_from_search(db, row["component"], row["quantity"])
        if not item_data:
            missing_items.append(row["component"])
            continue
        save_or_increment_item(db, bom, item_data)

    recalculate_bom(db, bom)
    db.refresh(bom)
    return bom, missing_items
