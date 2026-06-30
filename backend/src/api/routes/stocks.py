"""Stocks API endpoints"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_stocks():
    """Get list of all stocks across funds"""
    # TODO: Implement
    return {"stocks": []}


@router.get("/{isin}")
def get_stock(isin: str):
    """Get stock details by ISIN"""
    # TODO: Implement
    return {"isin": isin}
