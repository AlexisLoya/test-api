from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
import random

from .models import (
    Beer,
    OrderRequest,
    OrderItem,
    Round,
    RoundItem,
    PayRequest,
    Friend,
    Order, 
    Stock,
)
app = FastAPI(title="Beer Order and Payment API", version="1.0")

# Constants

TAX_RATE = 0.19
MAX_DISCOUNT_RATE = [0.05, 0.10, 0.15]


# Data

stock = Stock(
    last_updated=datetime.now(),
    beers=[
        Beer(name="Corona", price=115, quantity=5),
        Beer(name="Quilmes", price=120, quantity=10),
        Beer(name="Club Colombia", price=110, quantity=8),
    ],
)

friends = {}

current_order = Order(
    created=datetime.now(),
    paid=False,
    subtotal=0,
    taxes=0,
    discounts=0,
    discounts_str="",
    total=0,
    items=[],
    rounds=[],
)

# Helper Functions

def calculate_order_totals():
    grouped_items = {}
    for item in current_order.items:
        if item.name in grouped_items:
            grouped_items[item.name]["quantity"] += item.quantity
            grouped_items[item.name]["total"] += item.total
        else:
            grouped_items[item.name] = {"quantity": item.quantity, "total": item.total}
    # Group items
    current_order.items = [
        OrderItem(name=name, quantity=data["quantity"], total=data["total"])
        for name, data in grouped_items.items()
    ]
    
    # Calculate totals
    subtotal = sum(item.total for item in current_order.items)
    taxes = round(subtotal * TAX_RATE, 2)
    discount_rate = random.choice(MAX_DISCOUNT_RATE)
    discounts = round(subtotal * discount_rate, 2)
    total = round(subtotal + taxes - discounts, 2)

    current_order.subtotal = subtotal
    current_order.taxes = taxes
    current_order.discounts = discounts
    current_order.discounts_str = f"{int(discount_rate * 100)}% off"
    current_order.total = total


def update_stock_and_order(order_request: OrderRequest):
    beer = next((b for b in stock.beers if b.name == order_request.name), None)
    if not beer:
        raise HTTPException(status_code=404, detail=f"Beer {order_request.name} not found")

    if beer.quantity < order_request.quantity:
        raise HTTPException(status_code=400, detail=f"Not enough stock for {order_request.name}")

    total = beer.price * order_request.quantity
    beer.quantity -= order_request.quantity

    current_order.items.append(OrderItem(name=order_request.name, quantity=order_request.quantity, total=total))

    # Combine rounds
    if current_order.rounds and (current_order.rounds[-1].created.date() == datetime.now().date()):
        current_order.rounds[-1].items.append(RoundItem(name=order_request.name, quantity=order_request.quantity, person=order_request.user.strip()))
    else:
        current_order.rounds.append(Round(
            created=datetime.now(),
            items=[RoundItem(name=order_request.name, quantity=order_request.quantity, person=order_request.user.strip())],
        ))

    # Register dynamic friends
    if order_request.user.strip() not in friends:
        friends[order_request.user.strip()] = Friend(name=order_request.user.strip(), balance=0)

    calculate_order_totals()

# endpoints
@app.get("/stock", response_model=Stock)
def list_beers():
    """List available beers in stock."""
    return stock

@app.post("/order")
def place_order(order_request: List[OrderRequest]):
    """Place an order for beers."""
    for req in order_request:
        update_stock_and_order(req)
    return {"message": "Order placed", "order": current_order}

@app.get("/bill", response_model=Order)
def get_bill():
    """Retrieve the current bill."""
    return current_order

@app.put("/pay")
def pay_bill(pay_request: PayRequest):
    """Pay the bill either equally or individually."""
    if current_order.paid:
        raise HTTPException(status_code=400, detail="Bill already paid")

    if pay_request.mode == "equal":
        share = round(current_order.total / len(friends), 2)
        for friend in friends.values():
            friend.balance -= share
    elif pay_request.mode == "individual":
        for round_item in current_order.rounds:
            for item in round_item.items:
                friend = friends.get(item.person)
                if not friend:
                    raise HTTPException(status_code=404, detail=f"Friend {item.person} not found")
                friend.balance -= item.quantity * next((b.price for b in stock.beers if b.name == item.name), 0)
    else:
        raise HTTPException(status_code=400, detail="Invalid payment mode")

    current_order.paid = True
    return {"message": "Bill paid", "remaining_balances": list(friends.values())}
