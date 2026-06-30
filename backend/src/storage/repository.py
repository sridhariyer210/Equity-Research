"""
Repository pattern - all database reads/writes go through here.
No raw SQL elsewhere in the codebase.
"""
import logging
from datetime import date
from sqlalchemy.orm import Session
from src.storage.models import AMC, Fund, Holding, PortfolioAllocation

logger = logging.getLogger(__name__)


class HoldingRepository:
    """Repository for holdings CRUD operations"""

    @staticmethod
    def create_holdings(db: Session, holdings_list: list) -> None:
        """Bulk insert holdings"""
        db.bulk_insert_mappings(Holding, holdings_list)
        db.commit()
        logger.info(f"Inserted {len(holdings_list)} holdings")

    @staticmethod
    def get_holdings_by_date(db: Session, as_of_date: date) -> list:
        """Get all holdings for a specific date"""
        return db.query(Holding).filter(Holding.date == as_of_date).all()

    @staticmethod
    def get_holdings_by_fund(db: Session, fund_id: str, as_of_date: date = None) -> list:
        """Get holdings for a specific fund, optionally filtered by date"""
        query = db.query(Holding).filter(Holding.fund_id == fund_id)
        if as_of_date:
            query = query.filter(Holding.date == as_of_date)
        return query.all()


class FundRepository:
    """Repository for fund CRUD operations"""

    @staticmethod
    def get_all_active_funds(db: Session) -> list:
        """Get all active funds"""
        return db.query(Fund).filter(Fund.is_active == True).all()

    @staticmethod
    def get_fund_by_id(db: Session, fund_id: str) -> Fund:
        """Get fund by ID"""
        return db.query(Fund).filter(Fund.fund_id == fund_id).first()

    @staticmethod
    def create_fund(db: Session, fund: Fund) -> Fund:
        """Create a new fund"""
        db.add(fund)
        db.commit()
        db.refresh(fund)
        return fund
