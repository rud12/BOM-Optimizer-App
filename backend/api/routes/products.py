from fastapi import APIRouter, Query

from services.vendor_service import search_all_products

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/search")
def product_search(q: str = Query(..., min_length=2)):
    return search_all_products(q)
