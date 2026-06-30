"""Holdings API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.storage.database import get_db
from src.storage.repository import HoldingRepository

router = APIRouter()


@router.get("/{fund_id}")
def get_holdings(fund_id: str, db: Session = Depends(get_db)):
    """Get holdings for a specific fund"""
    holdings = HoldingRepository.get_holdings_by_fund(db, fund_id)
    return {"fund_id": fund_id, "holdings": holdings}
