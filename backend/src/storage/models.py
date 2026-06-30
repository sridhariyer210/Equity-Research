"""
Database models using SQLAlchemy ORM.
⚠️ V2+: These models are scaffolded but NOT used in V1.
V1 focuses on CSV-based pipeline only.

When you're ready for V2 (database integration):
1. Uncomment database setup in run_monthly.py
2. Run: alembic init migrations
3. Run: alembic revision --autogenerate -m "initial schema"
4. Run: alembic upgrade head
5. Update parser.py to save to database instead of CSV
"""
from sqlalchemy import Column, String, Float, Date, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class AMC(Base):
    """Asset Management Company registry"""
    __tablename__ = "amcs"

    amc_id = Column(String, primary_key=True)
    amc_name = Column(String, nullable=False)
    file_pattern = Column(String, nullable=False)   # "single_file" | "multi_tab"
    url_template = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Fund(Base):
    """Mutual fund registry"""
    __tablename__ = "funds"

    fund_id = Column(String, primary_key=True)
    fund_name = Column(String, nullable=False)
    cap_category = Column(String, nullable=False)   # small_cap | mid_cap | large_cap | flexi_cap
    amc_id = Column(String, ForeignKey("amcs.amc_id"), nullable=False)
    amfi_code = Column(String)
    sheet_name = Column(String)                     # For multi_tab AMCs only
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Holding(Base):
    """Core fact table - one row per fund × stock × month"""
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)             # Always YYYY-MM-01 (first of month)
    fund_id = Column(String, ForeignKey("funds.fund_id"), nullable=False)
    isin = Column(String)
    stock_name = Column(String, nullable=False)
    sector = Column(String)
    instrument_type = Column(String)                # equity | debt | etf | reit | etc
    market_value_cr = Column(Float)
    pct_of_nav = Column(Float)
    rank_in_fund = Column(Integer)                  # 1 = largest holding
    created_at = Column(DateTime, default=datetime.utcnow)


class PortfolioAllocation(Base):
    """Future: user portfolio overlay. Scaffold now, implement later."""
    __tablename__ = "portfolio_allocations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    fund_id = Column(String, ForeignKey("funds.fund_id"), nullable=False)
    allocation_pct = Column(Float)
    sip_amount = Column(Float)
    as_of_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

