from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List
import random

from models.orders import (
    Beer,
    OrderRequest,
    OrderItem,
    Round,
    RoundItem,
    PayRequest,
    PaidModeEnum,
    Friend,
    Order, 
    Stock,
    StockRequest,
)

router = APIRouter()
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
    paid_mode="unknown",
    items=[],
    rounds=[],
)

# Helper Functions
def fill_stock(stock_request: StockRequest):
    for item in stock_request.items:
        existing_beer = next((beer for beer in stock.beers if beer.name == item.name), None)
        if existing_beer:
            existing_beer.quantity += item.quantity
        else:
            stock.beers.append(Beer(name=item.name, price=item.price, quantity=item.quantity))
    stock.last_updated = datetime.now()

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


def update_stock_and_order(order_requests: List[OrderRequest]):
    new_round = Round(
        created=datetime.now(),
        items=[
            RoundItem(name=req.name, quantity=req.quantity, person=req.user.strip())
            for req in order_requests
        ],
    )

    for req in order_requests:
        beer = next((b for b in stock.beers if b.name == req.name), None)
        if not beer:
            raise HTTPException(status_code=404, detail=f"Beer {req.name} not found")

        if beer.quantity < req.quantity:
            raise HTTPException(
                status_code=400, detail=f"Not enough stock for {req.name}"
            )

        total = beer.price * req.quantity
        beer.quantity -= req.quantity

        current_order.items.append(
            OrderItem(name=req.name, quantity=req.quantity, total=total)
        )

        if req.user.strip() not in friends:
            friends[req.user.strip()] = Friend(name=req.user.strip(), balance=0)

    current_order.rounds.append(new_round)

    calculate_order_totals()


# endpoints
@router.post("/fill-stock")
def fill_stock_endpoint(stock_request: StockRequest):
    """Fill the stock with new items."""
    fill_stock(stock_request)
    return {"message": "Stock filled successfully", "stock": stock}

@router.get("/stock", response_model=Stock)
def list_beers():
    """List available beers in stock."""
    return stock

@router.post("/order")
def place_order(order_request: List[OrderRequest]):
    """Place an order for beers."""
    update_stock_and_order(order_request)
    return {"message": "Order placed", "order": current_order}

@router.get("/bill", response_model=Order)
def get_bill():
    """Retrieve the current bill."""
    return current_order

@router.put("/pay")
def pay_bill(pay_request: PayRequest):
    """Pay the bill either equally or individually."""
    if current_order.paid:
        raise HTTPException(status_code=400, detail="The bill has already been paid.")

    if pay_request.mode == PaidModeEnum.equal:
        current_order.paid_mode = PaidModeEnum.equal

        share = round(current_order.total / len(friends), 2)

        total_paid = sum(friend.balance for friend in friends.values())
        if total_paid + (share * len(friends)) > current_order.total:
            raise HTTPException(
                status_code=400, detail="The payment exceeds the total bill."
            )

        for friend in friends.values():
            friend.balance += share

    elif pay_request.mode == PaidModeEnum.individual:
        current_order.paid_mode = PaidModeEnum.individual

        friend = friends.get(pay_request.friend)
        if not friend:
            raise HTTPException(status_code=404, detail=f"Friend {pay_request.friend} not found.")

        individual_total = 0
        for round_item in current_order.rounds:
            for item in round_item.items:
                if item.person == pay_request.friend:
                    beer_price = next((b.price for b in stock.beers if b.name == item.name), 0)
                    item_total = item.quantity * beer_price
                    item_taxes = item_total * TAX_RATE
                    item_discount = item_total * (current_order.discounts / current_order.subtotal) if current_order.subtotal > 0 else 0
                    individual_total += item_total + item_taxes - item_discount

        friend_paid = friend.balance
        remaining_amount = individual_total - friend_paid
        if remaining_amount <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"{pay_request.friend} has already paid their total amount.",
            )

        payment = min(remaining_amount, current_order.total - sum(f.balance for f in friends.values()))
        friend.balance += payment
    else:
        raise HTTPException(status_code=400, detail="Invalid payment mode")

    total_paid = sum(friend.balance for friend in friends.values())
    if total_paid >= current_order.total:
        current_order.paid = True
    print(total_paid, current_order.total)
    return {
        "message": "Payment processed successfully.",
        "remaining_balances": {f.name: f.balance for f in friends.values()},
        "bill_status": "Paid" if current_order.paid else "Pending",
        "order": current_order,
    }

