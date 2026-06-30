# MF Holdings Tracker — Architecture & Setup Guide

> Feed this file to VS Code (or any AI assistant) to scaffold the full project structure, install dependencies, and understand design decisions before writing any code.

---

## Project Overview

A scalable Python pipeline that:
1. Fetches monthly mutual fund portfolio disclosures from AMFI
2. Normalizes and stores holdings data in a structured database
3. Aggregates cross-fund analytics (weighted averages, overlap, trends)
4. Exports to Google Sheets
5. Is designed to support a future frontend/API layer

**Phase 1 scope**: 10 small cap mutual funds. Architecture is built to scale to all cap categories and a user portfolio overlay.

---

## Project Structure

Create the following folder and file structure exactly as shown:

```
mf-tracker/
│
├── backend/
│   ├── src/
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── fetcher.py
│   │   │   └── downloader.py
│   │   │
│   │   ├── parsing/
│   │   │   ├── __init__.py
│   │   │   ├── parser.py
│   │   │   ├── normalizer.py
│   │   │   └── amc/
│   │   │       ├── __init__.py
│   │   │       ├── base.py
│   │   │       ├── nippon.py
│   │   │       └── sbi.py
│   │   │
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── repository.py
│   │   │
│   │   ├── analytics/
│   │   │   ├── __init__.py
│   │   │   ├── aggregator.py
│   │   │   ├── trends.py
│   │   │   └── portfolio.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── holdings.py
│   │   │       ├── funds.py
│   │   │       └── stocks.py
│   │   │
│   │   └── exporters/
│   │       ├── __init__.py
│   │       ├── sheets_writer.py
│   │       └── csv_writer.py
│   │
│   ├── config/
│   │   ├── funds.yaml
│   │   ├── settings.py
│   │   └── logging.yaml
│   │
│   ├── data/
│   │   ├── raw/
│   │   └── processed/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_parser.py
│   │   │   ├── test_normalizer.py
│   │   │   └── test_aggregator.py
│   │   ├── integration/
│   │   │   ├── test_fetcher.py
│   │   │   └── test_sheets_writer.py
│   │   └── fixtures/
│   │       └── sample_holdings.xlsx
│   │
│   ├── migrations/
│   │   └── versions/
│   │
│   ├── scripts/
│   │   └── run_monthly.py
│   │
│   ├── .env.example
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Makefile
│
├── frontend/
│   └── .gitkeep
│
├── docs/
│   ├── architecture.md
│   ├── adding_a_new_fund.md
│   └── data_dictionary.md
│
├── .github/
│   └── workflows/
│       └── monthly_refresh.yml
│
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

## File Contents to Scaffold

### `.gitignore`

```
# Environment
.env
*.env

# Data files (never commit raw or processed data)
backend/data/raw/
backend/data/processed/

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
venv/

# DB files
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/settings.json
.idea/

# Logs
*.log
```

---

### `backend/requirements.txt`

```
pandas>=2.0.0
openpyxl>=3.1.0
requests>=2.31.0
sqlalchemy>=2.0.0
alembic>=1.12.0
pyyaml>=6.0
gspread>=5.12.0
google-auth>=2.23.0
fastapi>=0.104.0
uvicorn>=0.24.0
python-dotenv>=1.0.0
httpx>=0.25.0
```

---

### `backend/requirements-dev.txt`

```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.1.0
isort>=5.12.0
mypy>=1.6.0
```

---

### `backend/.env.example`

```
# Environment: dev | staging | prod
APP_ENV=dev

# Database
# Dev: SQLite (no setup needed)
DATABASE_URL=sqlite:///./data/mf_tracker.db

# Prod: Uncomment and fill in
# DATABASE_URL=postgresql://user:password@host:5432/mf_tracker

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_PATH=config/google_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here

# AMFI / Data fetch
REQUEST_TIMEOUT_SECONDS=30
REQUEST_RETRY_COUNT=3
RAW_DATA_DIR=data/raw
PROCESSED_DATA_DIR=data/processed
```

---

### `backend/Makefile`

```makefile
.PHONY: fetch parse push refresh test lint format

fetch:
	python scripts/run_monthly.py --step fetch

parse:
	python scripts/run_monthly.py --step parse

push:
	python scripts/run_monthly.py --step push

refresh:
	python scripts/run_monthly.py --step all

test:
	pytest tests/ -v --cov=src

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/
```

---

### `backend/config/funds.yaml`

This is the single source of truth for all funds. Adding a new fund = one new entry here, no code changes.

```yaml
amcs:
  - id: nippon
    name: Nippon India Mutual Fund
    file_pattern: multi_tab        # One Excel file contains all Nippon funds across tabs
    url: ""                        # To be filled with AMFI/AMC URL

  - id: sbi
    name: SBI Mutual Fund
    file_pattern: single_file      # One Excel file per fund
    url_template: ""               # To be filled with AMFI/AMC URL template

funds:
  - id: nippon_small_cap
    name: Nippon India Small Cap Fund
    cap_category: small_cap
    amfi_code: ""
    amc_id: nippon
    sheet_name: "Small Cap Fund"   # Tab name inside Nippon's multi-tab Excel
    is_active: true

  - id: sbi_small_cap
    name: SBI Small Cap Fund
    cap_category: small_cap
    amfi_code: ""
    amc_id: sbi
    sheet_name: null
    is_active: true

  # Add remaining 8 small cap funds here following the same structure
  # Future: add large_cap, mid_cap, flexi_cap entries below
```

---

### `backend/config/settings.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "dev")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/mf_tracker.db")
GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 30))
REQUEST_RETRY_COUNT = int(os.getenv("REQUEST_RETRY_COUNT", 3))
RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "data/processed")
```

---

### `backend/src/storage/models.py`

SQLAlchemy ORM models. These define the database schema.

```python
from sqlalchemy import Column, String, Float, Date, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class AMC(Base):
    __tablename__ = "amcs"

    amc_id = Column(String, primary_key=True)
    amc_name = Column(String, nullable=False)
    file_pattern = Column(String, nullable=False)   # "single_file" | "multi_tab"
    url_template = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Fund(Base):
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
```

---

### `backend/src/parsing/amc/base.py`

Abstract base class. Every AMC parser must inherit this and implement both methods.

```python
from abc import ABC, abstractmethod
import pandas as pd


class BaseAMCParser(ABC):

    @abstractmethod
    def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
        """
        Read the raw file and return a DataFrame for the specific fund.
        For multi_tab AMCs: read the correct sheet.
        For single_file AMCs: read the whole file.
        """
        pass

    @abstractmethod
    def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
        """
        Map AMC-specific column names to the standard schema:
        [date, fund_id, isin, stock_name, sector, instrument_type,
         market_value_cr, pct_of_nav, rank_in_fund]
        """
        pass
```

---

### `backend/src/ingestion/fetcher.py`

```python
"""
Fetcher: Primary = auto-fetch from AMFI/AMC URLs.
Fallback = read from local data/raw/ folder.
"""
import os
import logging
from pathlib import Path
from datetime import date
from config.settings import RAW_DATA_DIR
from src.ingestion.downloader import download_file

logger = logging.getLogger(__name__)


def fetch_all(funds: list, amcs: dict, month: date) -> dict:
    """
    Fetch raw files for all AMCs for a given month.
    Groups funds by AMC to avoid duplicate downloads for multi_tab AMCs.
    Returns: dict of {amc_id: local_file_path}
    """
    downloaded = {}

    for amc_id, amc_config in amcs.items():
        file_path = _get_file_path(amc_id, month)

        if file_path.exists():
            logger.info(f"[{amc_id}] File already exists locally, skipping download.")
            downloaded[amc_id] = file_path
            continue

        try:
            url = _build_url(amc_config, month)
            download_file(url, file_path)
            logger.info(f"[{amc_id}] Downloaded successfully: {file_path}")
            downloaded[amc_id] = file_path
        except Exception as e:
            logger.warning(f"[{amc_id}] Auto-fetch failed: {e}. Falling back to manual file.")
            manual_path = _find_manual_file(amc_id, month)
            if manual_path:
                downloaded[amc_id] = manual_path
            else:
                logger.error(f"[{amc_id}] No manual file found either. Skipping.")

    return downloaded


def _get_file_path(amc_id: str, month: date) -> Path:
    return Path(RAW_DATA_DIR) / f"{amc_id}_{month.strftime('%Y-%m')}.xlsx"


def _find_manual_file(amc_id: str, month: date) -> Path | None:
    """Look for a manually downloaded file in data/raw/ matching naming convention."""
    path = _get_file_path(amc_id, month)
    return path if path.exists() else None


def _build_url(amc_config: dict, month: date) -> str:
    # URL construction logic per AMC — to be implemented per AMC's URL pattern
    raise NotImplementedError(f"URL builder not implemented for AMC: {amc_config['id']}")
```

---

### `backend/scripts/run_monthly.py`

Single entry point for all pipeline steps.

```python
"""
Usage:
    python scripts/run_monthly.py --step fetch
    python scripts/run_monthly.py --step parse
    python scripts/run_monthly.py --step push
    python scripts/run_monthly.py --step all
    python scripts/run_monthly.py --step all --month 2024-01
"""
import argparse
from datetime import date, datetime


def main():
    parser = argparse.ArgumentParser(description="MF Holdings Tracker — Monthly Refresh")
    parser.add_argument("--step", choices=["fetch", "parse", "push", "all"], required=True)
    parser.add_argument("--month", type=str, default=None,
                        help="Month to process in YYYY-MM format. Defaults to current month.")
    args = parser.parse_args()

    if args.month:
        month = datetime.strptime(args.month, "%Y-%m").date().replace(day=1)
    else:
        today = date.today()
        month = today.replace(day=1)

    print(f"Running step='{args.step}' for month={month}")

    if args.step in ("fetch", "all"):
        print("→ Fetching raw files...")
        # from src.ingestion.fetcher import fetch_all
        # fetch_all(...)

    if args.step in ("parse", "all"):
        print("→ Parsing and loading to DB...")
        # from src.parsing.parser import parse_all
        # parse_all(...)

    if args.step in ("push", "all"):
        print("→ Exporting to Google Sheets...")
        # from src.exporters.sheets_writer import push_to_sheets
        # push_to_sheets(...)

    print("Done.")


if __name__ == "__main__":
    main()
```

---

### `.github/workflows/monthly_refresh.yml`

Auto-runs the full pipeline on the 10th of every month (AMFI disclosures typically drop by then).

```yaml
name: Monthly Holdings Refresh

on:
  schedule:
    - cron: '0 6 10 * *'   # 6am UTC on the 10th of every month
  workflow_dispatch:         # Also allows manual trigger from GitHub UI

jobs:
  refresh:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run monthly refresh
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          GOOGLE_SHEETS_CREDENTIALS_PATH: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS_PATH }}
          GOOGLE_SHEETS_SPREADSHEET_ID: ${{ secrets.GOOGLE_SHEETS_SPREADSHEET_ID }}
        run: |
          cd backend
          python scripts/run_monthly.py --step all
```

---

### `docker-compose.yml`

For local development with Postgres (optional — SQLite works fine for dev).

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: mftracker
      POSTGRES_PASSWORD: mftracker
      POSTGRES_DB: mf_tracker
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://mftracker:mftracker@db:5432/mf_tracker
    depends_on:
      - db
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
```

---

## Database Schema

```sql
-- AMC registry (static)
CREATE TABLE amcs (
    amc_id       TEXT PRIMARY KEY,
    amc_name     TEXT NOT NULL,
    file_pattern TEXT NOT NULL,   -- 'single_file' or 'multi_tab'
    url_template TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fund registry (mostly static)
CREATE TABLE funds (
    fund_id      TEXT PRIMARY KEY,
    fund_name    TEXT NOT NULL,
    cap_category TEXT NOT NULL,   -- 'small_cap' | 'mid_cap' | 'large_cap' | 'flexi_cap'
    amc_id       TEXT REFERENCES amcs(amc_id),
    amfi_code    TEXT,
    sheet_name   TEXT,            -- For multi_tab AMCs only
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core fact table — one row per fund × stock × month
CREATE TABLE holdings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             DATE NOT NULL,        -- Always YYYY-MM-01
    fund_id          TEXT REFERENCES funds(fund_id),
    isin             TEXT,
    stock_name       TEXT NOT NULL,
    sector           TEXT,
    instrument_type  TEXT,                 -- 'equity' | 'debt' | 'etf' | 'reit'
    market_value_cr  REAL,
    pct_of_nav       REAL,
    rank_in_fund     INTEGER,              -- 1 = largest holding
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Composite index for fast time-series queries
CREATE INDEX idx_holdings_date_fund ON holdings(date, fund_id);
CREATE INDEX idx_holdings_isin      ON holdings(isin);

-- Future: user portfolio overlay (scaffold only)
CREATE TABLE portfolio_allocations (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        TEXT NOT NULL,
    fund_id        TEXT REFERENCES funds(fund_id),
    allocation_pct REAL,
    sip_amount     REAL,
    as_of_date     DATE NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Google Sheets Output Structure

The final Sheets workbook should have these tabs:

| Tab | Description |
|---|---|
| `Summary — [Month]` | Weighted avg % per stock across all active funds, sorted by avg weight |
| `Detail — [Month]` | Full fund × stock matrix — rows are stocks, columns are funds |
| `Stock Trends` | Month-over-month entry/exit and position size changes per stock |
| `Fund Overlap` | Which stocks appear in N or more funds (overlap heatmap) |
| `Raw Data` | Full holdings dump for the selected month (optional) |

---

## Key Design Principles

### One row = one fund × one stock × one month
Everything else is derived. Append monthly snapshots and all time-series comparisons (MoM, QoQ, YoY) become simple SQL filters.

### AMC-first ingestion
The fetcher iterates AMCs (not individual funds) to avoid duplicate downloads. One download per AMC per month, even if you track 5 funds from that AMC.

### Parser inheritance
Every AMC parser inherits `BaseAMCParser` and must implement `get_raw_dataframe()` and `normalize()`. Adding a new AMC = create one new file in `src/parsing/amc/`, no changes elsewhere.

### Repository pattern
All database reads and writes go through `src/storage/repository.py`. No raw SQL anywhere else. Switching from SQLite to Postgres = change one connection string.

### Stateless analytics
All functions in `src/analytics/` take a DataFrame in, return a DataFrame out. No side effects. These become API response generators directly when the API layer is wired up.

---

## Scalability Roadmap

| Future Need | How the Architecture Handles It |
|---|---|
| Add large/mid cap funds | New entries in `funds.yaml` with `cap_category: large_cap` |
| New AMC | Create `src/parsing/amc/new_amc.py`, add entry to `funds.yaml` |
| User portfolio overlay | Implement `src/analytics/portfolio.py` + `portfolio_allocations` table |
| QoQ / YoY comparisons | Filter `holdings` table by date range — schema already supports it |
| Frontend | `frontend/` folder is already separated; wire to `src/api/` routes |
| Multi-user app | Add `user_id` to `portfolio_allocations`; auth layer in `src/api/` |
| Prod database | Change `DATABASE_URL` in `.env` from SQLite to Postgres — no code changes |

---

## Next Steps (What to Build First)

1. Scaffold the full folder structure above
2. Fill in `funds.yaml` with the 10 small cap funds and their AMFI codes
3. Implement `src/storage/database.py` and run `alembic init` for migrations
4. Build `src/ingestion/downloader.py` with retry logic
5. Build the first two AMC parsers (`nippon.py` and `sbi.py`)
6. Wire up `run_monthly.py` end to end for a single month
7. Verify the `holdings` table looks correct
8. Build `src/exporters/sheets_writer.py`
