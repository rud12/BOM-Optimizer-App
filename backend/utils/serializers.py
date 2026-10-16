def vendor_to_dict(vendor):
    return {
        "id": vendor.id,
        "name": vendor.name,
        "display_name": vendor.display_name,
        "is_active": vendor.is_active,
        "created_at": vendor.created_at,
    }


def item_to_dict(item):
    return {
        "id": item.id,
        "alias_name": item.alias_name or item.component_name,
        "component_name": item.component_name,
        "quantity": item.quantity,
        "vendor_id": getattr(item, "vendor_id", None) or getattr(item, "selected_vendor_id", None),
        "vendor_name": item.vendor.name if item.vendor else None,
        "vendor_display_name": item.vendor.display_name if item.vendor else None,
        "manufacturer": item.manufacturer,
        "unit_price": float(item.unit_price),
        "total_price": float(item.total_price),
        "stock": item.stock,
        "product_url": item.product_url,
        "created_at": item.created_at,
    }


def bom_to_dict(bom, include_items=False):
    data = {
        "id": bom.id,
        "name": bom.name,
        "total_cost": float(bom.total_cost),
        "created_at": bom.created_at,
    }
    if include_items:
        data["items"] = [item_to_dict(item) for item in bom.items]
    return data
