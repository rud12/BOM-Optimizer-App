from pydantic import BaseModel


class BOMCreate(BaseModel):
    name: str


class BOMItemCreate(BaseModel):
    component_name: str
    alias_name: str | None = None
    quantity: int = 1
    vendor_id: int | None = None
    vendor_name: str | None = None
    manufacturer: str | None = None
    unit_price: float = 0
    stock: str | None = None
    product_url: str | None = None
