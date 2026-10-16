from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from services.vendor_service import get_vendor_products, get_vendor_suggestions, list_active_vendors
from utils.serializers import vendor_to_dict


router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.get("")
def list_vendors(db: Session = Depends(get_db)):
    return [vendor_to_dict(vendor) for vendor in list_active_vendors(db)]


@router.get("/{vendor_name}/products")
def vendor_products(vendor_name: str, search: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    return get_vendor_products(db, vendor_name, search)


@router.get("/{vendor_name}/suggestions")
def vendor_autocomplete(vendor_name: str, q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    return get_vendor_suggestions(db, vendor_name, q)
