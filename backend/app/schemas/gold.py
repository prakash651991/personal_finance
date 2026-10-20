from pydantic import BaseModel
from typing import Optional
from datetime import date


class GoldHoldingCreate(BaseModel):
    purchase_date: date
    grams: float
    purity: Optional[str] = None
    price_per_gram: Optional[float] = None
    making_charges: float = 0
    gst: float = 0
    total_cost: float
    seller: Optional[str] = None
    notes: Optional[str] = None


class GoldHoldingOut(BaseModel):
    id: str
    purchase_date: date
    grams: float
    purity: Optional[str] = None
    price_per_gram: Optional[float] = None
    making_charges: float = 0
    gst: float = 0
    total_cost: float
    seller: Optional[str] = None
    notes: Optional[str] = None
