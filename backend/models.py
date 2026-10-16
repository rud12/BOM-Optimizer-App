from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from core.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())


class BOM(Base):
    __tablename__ = "boms"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    total_cost = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    items = relationship("BOMItem", cascade="all, delete", back_populates="bom")


class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True)
    bom_id = Column(Integer, ForeignKey("boms.id", ondelete="CASCADE"))
    alias_name = Column(String(255))
    component_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    manufacturer = Column(String(255))
    unit_price = Column(Numeric(12, 2), default=0)
    total_price = Column(Numeric(12, 2), default=0)
    stock = Column(String(100))
    product_url = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())

    bom = relationship("BOM", back_populates="items")
    vendor = relationship("Vendor")
