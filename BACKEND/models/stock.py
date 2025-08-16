# BACKEND/app/models/stock.py
from pydantic import BaseModel

class PricePoint(BaseModel):
    Date: str
    Close: float