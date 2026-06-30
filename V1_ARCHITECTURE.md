# V1 Architecture - CSV-Based Pipeline (No Database)

## Overview

**V1 Scope:** Fetch fund disclosures → Normalize to CSV → Export data

```
Fund House Website
       ↓ (Selenium scraping)
Raw Excel Files (data/raw/)
       ↓ (AMC-specific parsers)
Normalized CSVs (data/processed/)
       ↓ (V2: Google Sheets, Database, API)
[Future: Analytics, Sheets, API]
```

---

## V1 vs V2+

### ✅ V1 (Current)
- Fetch: Selenium web scraping → XLSX
- Parse: Normalize to standard CSV schema
- Export: CSVs ready for Sheets/Database
- No database operations
- No API layer
- No advanced analytics

### 🔮 V2+ (Future)
- Database: Store CSVs in SQLAlchemy ORM
- Analytics: Compute weighted averages, overlaps, trends
- API: FastAPI endpoints for data queries
- Sheets: Auto-push aggregated data
- UI: Frontend dashboard

---

## Project Structure for V1

```
backend/
├── config/
│   ├── funds.yaml              ← Configure funds & download methods
│   └── settings.py             ← Environment variables
│
├── data/
│   ├── raw/                    ← Downloaded XLSX files (from fund houses)
│   └── processed/              ← Normalized CSV files
│
├── src/
│   ├── ingestion/
│   │   ├── fetcher.py         ✓ Multi-method downloader (Selenium, HTTP, manual)
│   │   ├── downloader.py      ✓ HTTP client with retry logic
│   │   └── web_scraper.py     ✓ Selenium browser automation
│   │
│   ├── parsing/
│   │   ├── parser.py          ✓ Orchestrates parsing, exports CSV
│   │   ├── normalizer.py      ✓ Standard schema definition & validation
│   │   └── amc/
│   │       ├── base.py        ✓ Base parser class
│   │       ├── nippon.py      → TODO: Implement normalize() for Nippon
│   │       └── sbi.py         → TODO: Implement normalize() for SBI
│   │
│   ├── storage/
│   │   ├── models.py          ⏸️ V2: Database models (not used in V1)
│   │   ├── database.py        ⏸️ V2: Database connection
│   │   └── repository.py      ⏸️ V2: Database access layer
│   │
│   ├── exporters/
│   │   ├── sheets_writer.py   → V2: Google Sheets export (logged in V1)
│   │   └── csv_writer.py      ✓ CSV export (used by parser.py)
│   │
│   ├── analytics/
│   │   ├── aggregator.py      ⏸️ V2: Cross-fund analytics
│   │   ├── trends.py          ⏸️ V2: Time-series analysis
│   │   └── portfolio.py       ⏸️ V2: User portfolio overlay
│   │
│   └── api/
│       ├── main.py            ⏸️ V2: FastAPI app
│       └── routes/            ⏸️ V2: API endpoints
│
├── scripts/
│   ├── run_monthly.py         ✓ V1: Fetch → Parse pipeline
│   └── discover_downloads.py  ✓ V1: Selenium link discovery helper
│
└── .env.example               ← Copy to .env (DB fields not needed for V1)
```

Legend:
- ✓ = Ready, used in V1
- → = Needs implementation (V1)
- ⏸️ = Scaffolded, not used in V1
- (empty) = Scaffolded but low priority

---

## V1 Data Flow

### Step 1: FETCH

```
config/funds.yaml (AMC configurations)
    ↓
fetcher.py (orchestrator)
    ├─→ Selenium web scraping (try first)
    ├─→ HTTP download (fallback)
    └─→ Manual upload (last resort)
    ↓
data/raw/nippon_2026-06.xlsx
data/raw/sbi_2026-06.xlsx
...
```

**Entry Point:**
```bash
python scripts/run_monthly.py --step fetch --month 2026-06
```

**Output:**
```
backend/data/raw/{amc_id}_{YYYY-MM}.xlsx
```

---

### Step 2: PARSE

```
data/raw/{amc_id}_{YYYY-MM}.xlsx
    ↓
parser.py (orchestrator)
    ├─→ Identify AMC from filename
    ├─→ Load funds.yaml config for that AMC
    └─→ Instantiate correct parser (NipponParser, SBIParser, etc.)
    ↓
parser.get_raw_dataframe()  ← Read Excel, get correct sheet
    ↓
parser.normalize()          ← Map columns to standard schema
    ↓
DataFrame with standard columns:
  fund_id, date, isin, stock_name, sector, 
  instrument_type, market_value_cr, pct_of_nav, rank_in_fund
    ↓
export to CSV
    ↓
data/processed/{amc_id}_{YYYY-MM}_normalized.csv
```

**Entry Point:**
```bash
python scripts/run_monthly.py --step parse --month 2026-06
```

**Output:**
```
backend/data/processed/nippon_2026-06_normalized.csv
backend/data/processed/sbi_2026-06_normalized.csv
...
```

**CSV Format:**
```
fund_id,date,isin,stock_name,sector,instrument_type,market_value_cr,pct_of_nav,rank_in_fund
nippon_small_cap,2026-06-01,INF001,Infosys,Technology,equity,150.5,2.5,1
nippon_small_cap,2026-06-01,INF002,TCS,Technology,equity,140.2,2.3,2
...
```

---

### Step 3: PUSH (V2, logged in V1)

```
data/processed/{amc_id}_{YYYY-MM}_normalized.csv
    ↓
sheets_writer.py (V2 orchestrator)
    ├─→ Load CSVs from data/processed/
    ├─→ Aggregate by stock (weighted average)
    ├─→ Create Sheets tabs:
    │   ├─ Summary: Weighted avg per stock
    │   ├─ Detail: Fund × Stock matrix
    │   ├─ Trends: MoM changes
    │   └─ Overlap: Multi-fund appearances
    ↓
Google Sheets Workbook
```

**Entry Point (V2):**
```bash
python scripts/run_monthly.py --step push --month 2026-06
```

**V1 Status:**  
Logged only. No actual Google Sheets export yet.

---

## Standard CSV Schema

All normalized CSVs must have these columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| fund_id | string | Fund identifier | nippon_small_cap |
| date | date | First of month | 2026-06-01 |
| isin | string | Security ISIN | INF001 |
| stock_name | string | Company name | Infosys |
| sector | string | Sector | Technology |
| instrument_type | string | Instrument type | equity |
| market_value_cr | float | Value in crores | 150.5 |
| pct_of_nav | float | % of portfolio | 2.5 |
| rank_in_fund | int | Rank (1=largest) | 1 |

---

## Implementing V1 Parsers

Each AMC needs two methods:

### 1. `get_raw_dataframe(file_path, fund_config) → DataFrame`

Read the raw Excel file and return DataFrame with fund's holdings.

**Nippon Example:**
```python
def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
    # Nippon is multi-tab, so get the specific sheet
    sheet_name = fund_config['sheet_name']  # e.g., "Small Cap Fund"
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df
```

**SBI Example:**
```python
def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
    # SBI is single file (one fund per file)
    df = pd.read_excel(file_path)
    return df
```

### 2. `normalize(df, fund_config) → DataFrame`

Map fund-house specific columns to standard schema.

**Nippon Example:**
```python
def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
    return pd.DataFrame({
        'isin': df['ISIN Code'],
        'stock_name': df['Scrip Name'],
        'sector': df['Sector'],
        'instrument_type': 'equity',  # or read from df
        'market_value_cr': df['Market Value (Rs. Cr.)'],
        'pct_of_nav': df['% of NAV'],
        'rank_in_fund': range(1, len(df) + 1),
    })
```

**SBI Example:**
```python
def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
    return pd.DataFrame({
        'isin': df['ISIN'],
        'stock_name': df['Company Name'],
        'sector': df['Industry'],
        'instrument_type': df['Type'],
        'market_value_cr': df['Value (Cr)'],
        'pct_of_nav': df['% of Portfolio'],
        'rank_in_fund': df['Rank'],
    })
```

---

## V1 Command Reference

```bash
# Full pipeline: fetch + parse
python scripts/run_monthly.py --step all --month 2026-06

# Just fetch
python scripts/run_monthly.py --step fetch --month 2026-06

# Just parse
python scripts/run_monthly.py --step parse --month 2026-06

# Discover Selenium selectors for a fund house
python scripts/discover_downloads.py --amc nippon

# Check what files exist
ls -lh data/raw/        # Downloaded Excel files
ls -lh data/processed/  # Processed CSV files

# View a CSV
cat data/processed/nippon_2026-06_normalized.csv | head -10
```

---

## Files Not Needed for V1

You can **safely ignore** these for V1 (they're for V2+):

- ⏸️ `src/storage/database.py` — Database connection
- ⏸️ `src/storage/repository.py` — Database queries
- ⏸️ `src/analytics/` — Analytics functions
- ⏸️ `src/api/` — FastAPI endpoints
- ⏸️ `migrations/` — Database migrations
- ⏸️ `.github/workflows/` — GitHub Actions
- ⏸️ `docker-compose.yml` — Docker setup

These are scaffolded and ready when you move to V2.

---

## Configuration for V1

Edit `config/funds.yaml`:

```yaml
amcs:
  - id: nippon
    name: Nippon India Mutual Fund
    file_pattern: multi_tab
    download_method: selenium
    base_url: "https://mf.nipponindiaim.com/investor-service/downloads/..."
    selectors:
      link_text_pattern: "Monthly portfolio for the month of"
      link_selector: "a[href*='portfolio']"
      wait_element: "body"

  - id: sbi
    name: SBI Mutual Fund
    file_pattern: single_file
    download_method: manual  # Set to 'manual' for V1 if scrapin fails
    base_url: ""

funds:
  - id: nippon_small_cap
    name: Nippon India Small Cap Fund
    cap_category: small_cap
    amfi_code: "INF123"
    amc_id: nippon
    sheet_name: "Small Cap Fund"
    is_active: true
    
  - id: sbi_small_cap
    name: SBI Small Cap Fund
    cap_category: small_cap
    amfi_code: "INF456"
    amc_id: sbi
    sheet_name: null
    is_active: true
    
  # Add 8 more funds here
```

---

## V1 Roadmap

**This Week:**
- [ ] Configure `funds.yaml` with 10 funds
- [ ] Implement Nippon parser
- [ ] Implement SBI parser
- [ ] Test: `python scripts/run_monthly.py --step all`
- [ ] Verify CSVs in `data/processed/`

**Next Week (V1.1):**
- Implement remaining parsers
- Add more fund houses
- Handle edge cases in parsing

**V2 (Next Phase):**
- Database: Store CSVs in SQLAlchemy
- API: FastAPI endpoints
- Analytics: Aggregations & trends
- Sheets: Auto-export with Google Sheets API

---

## Key V1 Principles

✓ **CSV-First**: Everything is CSV between steps
✓ **Config-Driven**: `funds.yaml` is source of truth
✓ **Parser Inheritance**: Each AMC = base class + 2 methods
✓ **No Database**: Skip all ORM operations
✓ **Simple Data Flow**: Raw Excel → Normalized CSV → (V2: Sheets/DB)

---

**Ready? Start here:** [QUICKSTART_V1.md](../QUICKSTART_V1.md)
