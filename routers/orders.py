from fastapi import APIRouter, HTTPException
from typing import List
from services.orders_service import (
    fill_stock,
    update_stock_and_order,
    pay_bill,
    stock,
    current_order,
)
from models.orders import StockRequest, OrderRequest, PayRequest

router = APIRouter()


@router.post("/fill-stock")
def fill_stock_endpoint(stock_request: StockRequest):
    """
    Endpoint to fill the stock with new items.
    """
    fill_stock(stock_request)
    return {"message": "Stock filled successfully", "stock": stock}


@router.get("/stock")
def list_beers():
    """
    Endpoint to list all available beers in stock.
    """
    return stock


@router.post("/order")
def place_order(order_request: List[OrderRequest]):
    """
    Endpoint to place an order for beers.
    """
    try:
        update_stock_and_order(order_request)
        return {"message": "Order placed", "order": current_order}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bill")
def get_bill():
    """
    Endpoint to retrieve the current bill.
    """
    return current_order


@router.put("/pay")
def pay_order(pay_request: PayRequest):
    """
    Endpoint to process a payment for the order.
    """
    try:
        return pay_bill(pay_request)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
