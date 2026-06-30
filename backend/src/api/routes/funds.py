"""Funds API endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.storage.database import get_db
from src.storage.repository import FundRepository

router = APIRouter()


@router.get("/")
def list_funds(db: Session = Depends(get_db)):
    """Get all active funds"""
    funds = FundRepository.get_all_active_funds(db)
    return {"funds": funds}


@router.get("/{fund_id}")
def get_fund(fund_id: str, db: Session = Depends(get_db)):
    """Get a specific fund"""
    fund = FundRepository.get_fund_by_id(db, fund_id)
    return fund
