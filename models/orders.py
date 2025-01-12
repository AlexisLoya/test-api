from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Beer(BaseModel):
    name: str
    price: int
    quantity: int

class RoundItem(BaseModel):
    name: str
    quantity: int
    person: str

class OrderItem(BaseModel):
    name: str
    quantity: int
    total: int

class Friend(BaseModel):
    name: str
    balance: float

class Round(BaseModel):
    created: datetime
    items: List[RoundItem]

class Order(BaseModel):
    created: datetime
    paid: bool
    subtotal: float
    taxes: float
    discounts: float
    discounts_str: str
    total: float
    items: List[OrderItem]
    rounds: List[Round]

class StockItem(BaseModel):
    name: str
    quantity: int

class StockRequest(BaseModel):
    items: List[StockItem]

class Stock(BaseModel):
    last_updated: datetime
    beers: List[Beer]

class OrderRequest(BaseModel):
    name: str
    quantity: int
    user: str

class PayRequest(BaseModel):
    mode: str
    friend_name: Optional[str] = None
