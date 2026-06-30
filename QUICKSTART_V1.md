# MF Holdings Tracker - V1 Quick Start Guide

## ✅ V1 Scope: CSV/XLSX Only (No Database)

This guide focuses on **V1: Fetch → Parse → Export** pipeline.

```
FETCH (Selenium scraping)
    ↓
backend/data/raw/{amc_id}_{YYYY-MM}.xlsx
    ↓
PARSE (Normalize to standard schema)
    ↓
backend/data/processed/{amc_id}_{YYYY-MM}_normalized.csv
    ↓
PUSH (Export to Google Sheets - optional for V1)
    ↓
Google Sheets Workbook (future)
```

**What's NOT in V1:**
- ✗ Database operations (skip Alembic, SQLAlchemy ORM, migrations)
- ✗ Repository pattern
- ✗ API endpoints
- ✗ Advanced analytics

**What's IN V1:**
- ✓ Fetch: Download XLSX from fund houses (Selenium web scraping)
- ✓ Parse: Normalize to CSVs
- ✓ Export: Prepare for Google Sheets (V2)

---

## 🚀 Getting Started (3 Steps)

### Step 1: Activate Environment
```bash
cd backend
source .venv/bin/activate
```

### Step 2: Configure Your Funds
Edit `config/funds.yaml`:
```yaml
amcs:
  - id: nippon
    name: Nippon India Mutual Fund
    file_pattern: multi_tab
    download_method: selenium
    base_url: "https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures"
    selectors:
      link_text_pattern: "Monthly portfolio for the month of"
      link_selector: "a[href*='portfolio']"
      wait_element: "body"

funds:
  - id: nippon_small_cap
    name: Nippon India Small Cap Fund
    cap_category: small_cap
    amfi_code: "INF123"
    amc_id: nippon
    sheet_name: "Small Cap Fund"
    is_active: true
  
  # Add 9 more small cap funds here
```

### Step 3: Run the Pipeline
```bash
# Full pipeline: fetch → parse
python scripts/run_monthly.py --step all --month 2026-06

# Or individual steps
python scripts/run_monthly.py --step fetch --month 2026-06
python scripts/run_monthly.py --step parse --month 2026-06

# Check output
ls -la data/raw/          # Downloaded XLSX files
ls -la data/processed/    # Normalized CSV files
```

---

## 📊 V1 Pipeline Details

### FETCH: Download from Fund Houses

```bash
python scripts/run_monthly.py --step fetch --month 2026-06
```

**What happens:**
1. Reads `config/funds.yaml` AMC configurations
2. For each AMC, checks if file already exists in `data/raw/`
3. If not, tries Selenium web scraping
4. If Selenium fails, looks for manually uploaded file
5. Logs all results

**Outputs:**
```
backend/data/raw/nippon_2026-06.xlsx
backend/data/raw/sbi_2026-06.xlsx
backend/data/raw/axis_2026-06.xlsx
...
```

### PARSE: Normalize to Standard CSV Schema

```bash
python scripts/run_monthly.py --step parse --month 2026-06
```

**What happens:**
1. Reads all XLSX files from `data/raw/` for the month
2. For each AMC, instantiates correct parser (Nippon, SBI, etc.)
3. Parser extracts fund-specific data
4. Normalizes to standard schema
5. Exports as CSV to `data/processed/`

**Standard CSV Schema:**
```
fund_id, date, isin, stock_name, sector, instrument_type, 
market_value_cr, pct_of_nav, rank_in_fund
```

**Outputs:**
```
backend/data/processed/nippon_2026-06_normalized.csv
backend/data/processed/sbi_2026-06_normalized.csv
backend/data/processed/axis_2026-06_normalized.csv
...
```

### PUSH: Export to Google Sheets (Future)

```bash
python scripts/run_monthly.py --step push --month 2026-06
```

**V1 Status:** Logged only (no actual export yet)

**V2 will create sheets:**
- Summary: Weighted avg holdings
- Detail: Fund × Stock matrix
- Trends: MoM changes
- Overlap: Multi-fund appearances

---

## 🔧 Implementing Parsers (Your Main Task for V1)

Each AMC parser must implement 2 methods:

### Example: Nippon Parser

File: `src/parsing/amc/nippon.py`

```python
from src.parsing.amc.base import BaseAMCParser
import pandas as pd

class NipponParser(BaseAMCParser):
    
    def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
        """
        Read the Nippon multi-tab Excel file and extract the correct sheet.
        
        Args:
            file_path: Path to Excel file
            fund_config: Configuration with sheet_name
            
        Returns:
            Raw DataFrame from the Excel sheet
        """
        sheet_name = fund_config.get('sheet_name')
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    
    def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
        """
        Map Nippon's column names to standard schema.
        
        Standard columns:
        - fund_id, date, isin, stock_name, sector, 
          instrument_type, market_value_cr, pct_of_nav, rank_in_fund
        """
        # Example mapping (adjust based on actual Nippon Excel structure)
        normalized = pd.DataFrame({
            'isin': df['ISIN Code'],
            'stock_name': df['Scrip Name'],
            'sector': df['Sector'],
            'instrument_type': 'equity',  # or read from df
            'market_value_cr': df['Market Value (Rs. Cr.)'],
            'pct_of_nav': df['% of NAV'],
            'rank_in_fund': df.index + 1,  # 1-indexed rank
        })
        
        return normalized
```

### Example: SBI Parser

File: `src/parsing/amc/sbi.py`

```python
from src.parsing.amc.base import BaseAMCParser
import pandas as pd

class SBIParser(BaseAMCParser):
    
    def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
        """Read the entire SBI Excel file"""
        df = pd.read_excel(file_path)
        return df
    
    def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
        """Map SBI columns to standard schema"""
        normalized = pd.DataFrame({
            'isin': df['ISIN'],
            'stock_name': df['Company Name'],
            'sector': df['Industry'],
            'instrument_type': df['Type'],
            'market_value_cr': df['Value (Cr)'],
            'pct_of_nav': df['% of Portfolio'],
            'rank_in_fund': df['Rank'],
        })
        
        return normalized
```

---

## 📋 To Do for V1 Completion

- [ ] Configure `config/funds.yaml` with 10 small cap funds
- [ ] Download sample XLSX files from each fund house
- [ ] Place in `backend/data/raw/` with naming: `{amc_id}_{YYYY-MM}.xlsx`
- [ ] Implement `src/parsing/amc/nippon.py` normalize() method
- [ ] Implement `src/parsing/amc/sbi.py` normalize() method
- [ ] Implement other AMC parsers (as needed)
- [ ] Test: `python scripts/run_monthly.py --step all --month 2026-06`
- [ ] Verify CSVs in `backend/data/processed/`

---

## 🧪 Quick Test

```bash
# Create sample data for testing
cd backend

# 1. Manually download a Nippon disclosure file and place it:
cp ~/Downloads/nippon_disclosure_may_2026.xlsx data/raw/nippon_2026-05.xlsx

# 2. Run fetch (should find it)
python scripts/run_monthly.py --step fetch --month 2026-05

# 3. Implement Nippon parser, then run parse
python scripts/run_monthly.py --step parse --month 2026-05

# 4. Check output
cat data/processed/nippon_2026-05_normalized.csv | head -20
```

---

## 📁 File Structure for V1

```
backend/
├── config/
│   └── funds.yaml                    # Configure your 10 funds here
├── data/
│   ├── raw/                          # Downloaded XLSX files
│   │   ├── nippon_2026-06.xlsx
│   │   ├── sbi_2026-06.xlsx
│   │   └── ...
│   └── processed/                    # Normalized CSV files
│       ├── nippon_2026-06_normalized.csv
│       ├── sbi_2026-06_normalized.csv
│       └── ...
├── src/
│   ├── ingestion/
│   │   ├── fetcher.py               # Already done ✓
│   │   ├── downloader.py            # Already done ✓
│   │   └── web_scraper.py           # Already done ✓
│   └── parsing/
│       ├── parser.py                 # Already done ✓
│       ├── normalizer.py             # Already done ✓
│       └── amc/
│           ├── base.py               # Base class ✓
│           ├── nippon.py             # TODO: Implement normalize()
│           └── sbi.py                # TODO: Implement normalize()
├── scripts/
│   ├── run_monthly.py                # Already done ✓
│   └── discover_downloads.py         # Already done ✓
└── .env.example                      # Copy to .env (no DB needed)
```

---

## 🎯 Next Actions (Priority Order)

1. **TODAY:** Set up `config/funds.yaml` with your 10 small cap funds
2. **TODAY:** Download sample disclosure files from Nippon and place in `data/raw/`
3. **TOMORROW:** Implement Nippon parser (map columns in normalize())
4. **TOMORROW:** Test: `python scripts/run_monthly.py --step parse`
5. **THIS WEEK:** Implement SBI and other parsers
6. **THIS WEEK:** Test full pipeline end-to-end

---

## ❓ FAQ

**Q: Do I need to set up the database?**  
A: No! V1 skips all database operations. Just CSV files.

**Q: Where's the Google Sheets integration?**  
A: V1 prepares data as CSVs. Google Sheets export is V2.

**Q: How do I get sample files to test?**  
A: Visit fund house websites, download disclosures manually, place in `data/raw/`.

**Q: What if a fund house website changes?**  
A: The Selenium discovery script can find new selectors. Or manually download as fallback.

**Q: Can I skip Selenium?**  
A: Yes! Just manually download and place files in `data/raw/` with naming convention.

---

## 📞 Commands Reference

```bash
# Activate environment
source backend/.venv/bin/activate

# Run full pipeline for a month
python scripts/run_monthly.py --step all --month 2026-06

# Or individual steps
python scripts/run_monthly.py --step fetch --month 2026-06
python scripts/run_monthly.py --step parse --month 2026-06
python scripts/run_monthly.py --step push --month 2026-06

# Discover links for a fund house
python scripts/discover_downloads.py --amc nippon

# Check what's in raw directory
ls -lh data/raw/

# Check processed CSVs
ls -lh data/processed/
head -5 data/processed/nippon_2026-06_normalized.csv
```

---

## ✨ Key Insight for V1

**Configuration Over Code**  
Everything is configured in `config/funds.yaml`:
- Which funds to track
- Which fund houses
- How to download files (Selenium selectors)
- When/where to look for files

**No code changes needed to add a new fund!**

---

Ready? Start with `config/funds.yaml` 👉 

V1 is all about getting data flowing from fund houses → normalized CSVs. You've got this! 🚀
