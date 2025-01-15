from datetime import datetime
from typing import List
import random
from functools import wraps

from models.orders import (
    Beer,
    OrderRequest,
    OrderItem,
    Round,
    RoundItem,
    Friend,
    Order,
    Stock,
    StockRequest,
    PaidModeEnum,
)
from fastapi import HTTPException

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
    paid_mode=PaidModeEnum.unknown,
    items=[],
    rounds=[],
)


# Stock Management
def fill_stock(stock_request: StockRequest):
    """
    Updates stock with the items in the request.
    """
    for item in stock_request.items:
        existing_beer = next((beer for beer in stock.beers if beer.name == item.name), None)
        if existing_beer:
            existing_beer.quantity += item.quantity
        else:
            stock.beers.append(Beer(name=item.name, price=item.price, quantity=item.quantity))
    stock.last_updated = datetime.now()


# Order Management
def calculate_order_totals():
    """
    Calculates and updates the totals for the current order.
    """
    grouped_items = {}
    for item in current_order.items:
        if item.name in grouped_items:
            grouped_items[item.name]["quantity"] += item.quantity
            grouped_items[item.name]["total"] += item.total
        else:
            grouped_items[item.name] = {"quantity": item.quantity, "total": item.total}

    current_order.items = [
        OrderItem(name=name, quantity=data["quantity"], total=data["total"])
        for name, data in grouped_items.items()
    ]

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


def validate_payment_mode(mode):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_order.paid_mode != PaidModeEnum.unknown and current_order.paid_mode != mode:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot process {mode.value} payment when {current_order.paid_mode.value} payment is already in progress."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def update_stock_and_order(order_requests: List[OrderRequest]):
    """
    Updates stock and processes the items in the current order.
    """
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
            raise HTTPException(status_code=400, detail=f"Not enough stock for {req.name}")

        total = beer.price * req.quantity
        beer.quantity -= req.quantity

        current_order.items.append(
            OrderItem(name=req.name, quantity=req.quantity, total=total)
        )

        if req.user.strip() not in friends:
            friends[req.user.strip()] = Friend(name=req.user.strip(), balance=0)

    current_order.rounds.append(new_round)
    calculate_order_totals()


# Payment Management
def pay_bill(pay_request):
    """
    Processes the payment for the current order, either equally or individually.
    """
    if current_order.paid:
        raise HTTPException(status_code=400, detail="The bill has already been paid.")

    if  pay_request.mode == PaidModeEnum.equal:
        return process_equal_payment()

    if pay_request.mode == PaidModeEnum.individual:
        return process_individual_payment(pay_request.friend)

    raise HTTPException(status_code=400, detail="Invalid payment mode")

@validate_payment_mode(PaidModeEnum.equal)
def process_equal_payment():
    """
    Splits the bill equally among all friends and processes the payment.
    """
    if not friends:
        raise HTTPException(status_code=400, detail="No friends found to split the bill.")

    share = round(current_order.total / len(friends), 2)
    total_paid = sum(friend.balance for friend in friends.values())
    if total_paid + (share * len(friends)) > current_order.total:
        raise HTTPException(status_code=400, detail="The payment exceeds the total bill.")

    for friend in friends.values():
        friend.balance += share
    
    current_order.paid_mode = PaidModeEnum.equal
    return finalize_payment()

@validate_payment_mode(PaidModeEnum.individual)
def process_individual_payment(friend_name: str):
    """
    Processes a payment for a specific friend.
    """
    friend = friends.get(friend_name)
    if not friend:
        raise HTTPException(status_code=404, detail=f"Friend {friend_name} not found.")

    total_due = calculate_individual_due(friend_name)

    if total_due <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"{friend_name} has already paid their total amount."
        )

    payment = min(total_due, current_order.total - sum(f.balance for f in friends.values()))
    friend.balance += payment
    current_order.paid_mode = PaidModeEnum.individual
    return finalize_payment()


def calculate_individual_due(friend_name: str) -> float:
    """
    Calculates the total amount a specific friend owes.
    """
    total_due = 0

    for round_item in current_order.rounds:
        for item in round_item.items:
            if item.person == friend_name:
                beer_price = next((b.price for b in stock.beers if b.name == item.name), 0)
                item_total = item.quantity * beer_price
                item_taxes = item_total * TAX_RATE
                item_discount = (
                    item_total * (current_order.discounts / current_order.subtotal)
                    if current_order.subtotal > 0 else 0
                )
                total_due += item_total + item_taxes - item_discount

    return total_due - friends[friend_name].balance


def finalize_payment():
    """
    Finalizes the payment, checks if the order is fully paid, and updates the status.
    """
    total_paid = sum(friend.balance for friend in friends.values())
    if total_paid >= current_order.total:
        current_order.paid = True

    return {
        "message": "Payment processed successfully.",
        "remaining_balances": {f.name: f.balance for f in friends.values()},
        "bill_status": "Paid" if current_order.paid else "Pending",
        "order": current_order,
    }
