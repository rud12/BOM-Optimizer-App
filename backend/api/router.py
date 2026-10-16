from fastapi import APIRouter

from api.routes import boms, products, vendors

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(vendors.router)
api_router.include_router(products.router)
api_router.include_router(boms.router)
