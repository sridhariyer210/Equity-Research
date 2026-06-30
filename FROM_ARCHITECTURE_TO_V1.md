# 🎯 From Architecture to V1: What Changed

## The Request

> "For now deprioritize database based actions - for V1 I don't want database activities as I have not configured. Currently I will only work on raw csv's / xlsx and final gsheet"

## What We Did

We **refocused the entire project from multi-tier architecture to a lean V1 pipeline** focused exclusively on:

1. **Fetch**: Download XLSX files from fund houses (Selenium scraping)
2. **Parse**: Normalize to standard CSV schema
3. **Export**: Prepare for Google Sheets (V2)

**Database, API, analytics, migrations, and Docker all deprioritized but scaffolded for V2.**

---

## Changes Summary

### Original Architecture (mf_tracker_architecture.md)

```
Fetch → Parse → Store (Database) → Analyze → Export
(6 modules: ingestion, parsing, storage, analytics, api, exporters)
Full complexity with SQLAlchemy ORM, Alembic migrations, repository pattern
```

### V1 Pipeline (NEW)

```
Fetch → Parse → Export
(3 modules: ingestion, parsing, exporters)
CSV-based, no database, configuration-driven
```

### Files Modified for V1

| File | Change | Reason |
|------|--------|--------|
| `scripts/run_monthly.py` | Removed DB steps, added CSV export | Focus on CSV pipeline |
| `src/parsing/parser.py` | Now exports CSV instead of saving to DB | V1 only needs CSV |
| `src/exporters/sheets_writer.py` | Google Sheets is logged only (V2+) | Deprioritized |
| `src/storage/models.py` | Added warning "V2+" | Not used in V1 |
| `config/settings.py` | Removed DB-related env vars for V1 | Simplify |

### Files Deprioritized (but intact for V2)

- ✗ Database operations (SQLAlchemy ORM)
- ✗ Alembic migrations
- ✗ Repository pattern
- ✗ Analytics module
- ✗ API endpoints
- ✗ Docker setup
- ✗ GitHub Actions

### New Files Created for V1

- ✓ `QUICKSTART_V1.md` — V1 quick start guide
- ✓ `V1_ARCHITECTURE.md` — V1 design document
- ✓ `V1_READY.md` — Checklist and summary

---

## Pipeline Comparison

### Original (Complex)
```
Fund House Website
    ↓
Raw Excel (ingestion)
    ↓
Parse (parsing)
    ↓
Database (storage + repository pattern)
    ↓
Analyze (analytics)
    ↓
API (fastapi)
    ↓
Google Sheets (exporters)
```

### V1 (Lean)
```
Fund House Website
    ↓ (Selenium scraping)
Raw Excel → data/raw/
    ↓ (AMC-specific parsers)
Normalized CSV → data/processed/
    ↓ (ready for Sheets/DB in V2)
[Future: Sheets, Database, API]
```

---

## Code Changes

### Before (run_monthly.py)

```python
# Full pipeline with database operations
if args.step in ("parse", "all"):
    parse_all(downloads, funds_config)
    
if args.step in ("push", "all"):
    push_to_sheets(analytics_dict)
    
# Plus database migrations, etc.
```

### After (run_monthly.py)

```python
# V1: CSV-only pipeline
if args.step in ("fetch", "all"):
    _run_fetch(args.config, month)
    
if args.step in ("parse", "all"):
    _run_parse(args.config, month)  # → CSV export
    
if args.step in ("push", "all"):
    _run_push(args.config, month)  # → Logged for V2
```

---

## Data Flow Changes

### Original Data Flow
```
XLSX → DataFrame → Normalize → ORM Models → Database → Queries → Sheets
```

### V1 Data Flow
```
XLSX → DataFrame → Normalize → CSV → [V2: Database, API, Sheets]
```

**Benefit**: Simpler, faster, no DB overhead, easy to test independently.

---

## What's Actually Needed for V1

```
backend/
├── config/funds.yaml          ← Configure your funds (YOU)
├── src/
│   ├── ingestion/             ✓ Complete
│   └── parsing/
│       └── amc/
│           ├── nippon.py      ← Implement (YOU)
│           └── sbi.py         ← Implement (YOU)
├── data/
│   ├── raw/                   ← Download XLSX here
│   └── processed/             ← CSV exports here
└── scripts/run_monthly.py     ✓ Ready
```

---

## What Can Be Ignored for V1

```
backend/
├── src/
│   ├── storage/               ← Database (V2+)
│   ├── analytics/             ← Analytics (V2+)
│   └── api/                   ← API (V2+)
├── migrations/                ← Alembic (V2+)
├── docker-compose.yml         ← Docker (V2+)
└── .github/workflows/         ← CI/CD (V2+)
```

All scaffolded, nothing deleted, ready when you need it.

---

## Configuration for V1

### .env for V1 (Minimal)

```bash
# V1: Only if you want Selenium headless=false for debugging
# Leave empty for V2 database variables

# Optional: For Google Sheets (V2+)
# GOOGLE_SHEETS_CREDENTIALS_PATH=
# GOOGLE_SHEETS_SPREADSHEET_ID=
```

### .env for V2+ (Full)

```bash
APP_ENV=production
DATABASE_URL=postgresql://user:pass@host/db
GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=xxxxx
```

---

## How to Implement V1

### Step 1: Configure (TODAY)

```yaml
# backend/config/funds.yaml
amcs:
  - id: nippon
    download_method: selenium
    base_url: "https://..."

funds:
  - id: nippon_small_cap
    amc_id: nippon
    # ... 9 more funds
```

### Step 2: Implement Parsers (THIS WEEK)

```python
# backend/src/parsing/amc/nippon.py
class NipponParser(BaseAMCParser):
    def normalize(self, df, fund_config):
        return pd.DataFrame({
            'isin': df['ISIN Code'],
            'stock_name': df['Scrip Name'],
            # ... more columns
        })
```

### Step 3: Run Pipeline

```bash
python scripts/run_monthly.py --step all --month 2026-06
# Outputs: data/processed/{amc_id}_*_normalized.csv
```

---

## Transition Path to V2

When ready to add database, sheets, and API:

1. **Activate storage** in `run_monthly.py` (uncomment DB lines)
2. **Run migrations** (`alembic upgrade head`)
3. **Update parser.py** to save CSV + database simultaneously
4. **Implement analytics** (`src/analytics/`)
5. **Implement sheets exporter** (`src/exporters/sheets_writer.py`)
6. **Enable API** (`src/api/main.py`)

**No rework of V1 code needed!** Parsers work exactly the same.

---

## Why This Approach?

✅ **Focus** — Get data flowing without infrastructure overhead  
✅ **Speed** — Skip database setup, migrations, ORM complexity  
✅ **Testing** — CSV files are easy to inspect and debug  
✅ **Flexibility** — Easy to switch databases later (CSV → SQLite → Postgres)  
✅ **Simplicity** — Configuration-driven, not code-driven  
✅ **Scalability** — All V2 infrastructure ready when you need it  

---

## Documentation Roadmap

**For V1, Read:**
1. `QUICKSTART_V1.md` — Get started
2. `V1_ARCHITECTURE.md` — Understand design
3. `docs/web_scraping_guide.md` — Selenium setup

**For Future V2, Read:**
4. `docs/architecture.md` — Full system design
5. `docs/adding_a_new_fund.md` — Scaling pattern
6. `docs/data_dictionary.md` — Database schema
7. `BUILD_SUMMARY.md` — Original vision

---

## Key Takeaway

**V1 is a focused, lean pipeline that gets data flowing from fund houses → normalized CSVs.**

All infrastructure for V2 (database, analytics, API) is scaffolded and ready. When you're ready, just activate it—no rework needed.

---

## Quick Command Reference for V1

```bash
# Full pipeline
python scripts/run_monthly.py --step all --month 2026-06

# Just fetch
python scripts/run_monthly.py --step fetch --month 2026-06

# Just parse
python scripts/run_monthly.py --step parse --month 2026-06

# Discover Selenium selectors
python scripts/discover_downloads.py --amc nippon

# Check outputs
ls -la data/processed/
cat data/processed/nippon_2026-06_normalized.csv | head -20
```

---

**Next: Read [QUICKSTART_V1.md](QUICKSTART_V1.md) to get started!** 🚀
