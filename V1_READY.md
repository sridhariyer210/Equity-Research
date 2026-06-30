# ✅ V1 Ready: CSV-Based Pipeline (No Database)

## What Changed for V1

Based on your request to **deprioritize database operations**, the project has been refocused for **V1: Raw CSV/XLSX only**.

### Summary of Changes

| Component | V0 | V1 | Status |
|-----------|----|----|--------|
| Fetch | ✓ | ✓ | Ready (Selenium scraping) |
| Parse | ✓ | ✓ | Ready (CSV export instead of DB) |
| Database | ✓ | ✗ | Removed from V1 (ready for V2) |
| Analytics | ✓ | ✗ | Removed from V1 (ready for V2) |
| API | ✓ | ✗ | Removed from V1 (ready for V2) |
| Google Sheets | ✓ | ○ | Logged in V1, ready for V2 |

Legend: ✓ Active | ✗ Skipped | ○ Prepared

---

## V1 Pipeline: 3 Steps

```
Step 1: FETCH (Selenium)       → data/raw/{amc_id}_{YYYY-MM}.xlsx
Step 2: PARSE (CSV Export)     → data/processed/{amc_id}_{YYYY-MM}_normalized.csv
Step 3: PUSH (Logged for V2)   → [To Google Sheets when ready]
```

**Command:**
```bash
python scripts/run_monthly.py --step all --month 2026-06
```

---

## What's Ready for V1

| Item | File | Status | Notes |
|------|------|--------|-------|
| Fetch orchestrator | `src/ingestion/fetcher.py` | ✅ Complete | Multi-method: Selenium, HTTP, manual |
| Web scraper | `src/ingestion/web_scraper.py` | ✅ Complete | Selenium automation |
| Downloader | `src/ingestion/downloader.py` | ✅ Complete | HTTP with retry + 3-tier fallback |
| Parser orchestrator | `src/parsing/parser.py` | ✅ Complete | CSV export (NEW for V1) |
| Base parser class | `src/parsing/amc/base.py` | ✅ Complete | Base for AMC-specific parsers |
| Nippon parser | `src/parsing/amc/nippon.py` | 🟡 Scaffold | Need to implement `normalize()` |
| SBI parser | `src/parsing/amc/sbi.py` | 🟡 Scaffold | Need to implement `normalize()` |
| Discovery script | `scripts/discover_downloads.py` | ✅ Complete | Auto-find Selenium selectors |
| Main script | `scripts/run_monthly.py` | ✅ Complete | V1 pipeline (no DB steps) |
| Configuration | `config/funds.yaml` | 🟡 Template | Need to fill with 10 funds |

---

## What's Deprioritized for V2+

These are **scaffolded but not used in V1**:

| Component | Files | Status |
|-----------|-------|--------|
| **Database** | `src/storage/models.py`, `database.py`, `repository.py` | ⏸️ Ready for V2 |
| **Analytics** | `src/analytics/` | ⏸️ Ready for V2 |
| **API** | `src/api/` | ⏸️ Ready for V2 |
| **Migrations** | `migrations/` | ⏸️ Ready for V2 |
| **CI/CD** | `.github/workflows/` | ⏸️ Ready for V2 |

When you're ready for V2, just uncomment/activate these modules. No rework needed!

---

## Your V1 Action Items

### Priority 1: Configure (Today)

**File:** `backend/config/funds.yaml`

```yaml
amcs:
  - id: nippon
    download_method: selenium
    base_url: "https://mf.nipponindiaim.com/investor-service/downloads/..."
    
  - id: sbi
    download_method: manual  # For now, download manually

funds:
  # Add your 10 small cap funds here with proper AMFI codes
  - id: nippon_small_cap
    amc_id: nippon
    # ...
```

### Priority 2: Implement Parsers (This Week)

**Files to implement:**
- `backend/src/parsing/amc/nippon.py` → Add column mapping in `normalize()`
- `backend/src/parsing/amc/sbi.py` → Add column mapping in `normalize()`
- Other fund houses as needed

**Template:**
```python
def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
    return pd.DataFrame({
        'isin': df['ISIN column name'],
        'stock_name': df['Stock column name'],
        # ... map all standard columns
    })
```

### Priority 3: Test Pipeline (This Week)

```bash
cd backend
source .venv/bin/activate

# Place sample Excel file
cp ~/Downloads/nippon_disclosure.xlsx data/raw/nippon_2026-06.xlsx

# Run full pipeline
python scripts/run_monthly.py --step all --month 2026-06

# Check output
ls -la data/processed/
cat data/processed/nippon_2026-06_normalized.csv | head -10
```

---

## V1 File Locations

```
Inputs:
  backend/config/funds.yaml              ← Configure your funds
  backend/data/raw/*.xlsx                ← Downloaded Excel files

Processing:
  backend/src/ingestion/fetcher.py       ← Fetch orchestrator ✓
  backend/src/parsing/parser.py          ← Parse orchestrator ✓
  backend/src/parsing/amc/nippon.py      ← Implement normalize() 🟡

Outputs:
  backend/data/processed/*.csv           ← Normalized CSV files

Commands:
  backend/scripts/run_monthly.py         ← Main pipeline ✓
  backend/scripts/discover_downloads.py  ← Helper script ✓
```

---

## V1 CSV Output Format

Each parsed fund becomes a CSV with this schema:

```
fund_id,date,isin,stock_name,sector,instrument_type,market_value_cr,pct_of_nav,rank_in_fund
nippon_small_cap,2026-06-01,INF001,Infosys,Technology,equity,150.5,2.5,1
nippon_small_cap,2026-06-01,INF002,TCS,Technology,equity,140.2,2.3,2
nippon_small_cap,2026-06-01,INF003,HDFC Bank,Financial,equity,130.1,2.1,3
...
```

---

## Key V1 Features

✅ **Selenium Web Scraping**  
Automates clicking through fund house websites to download disclosures.

✅ **Manual Fallback**  
If Selenium fails, just place file in `data/raw/` with naming convention.

✅ **Configuration-Driven**  
Everything in `funds.yaml` — no code changes to add funds.

✅ **Normalized CSV Output**  
Standard schema ready for databases, APIs, or Sheets (V2).

✅ **Discovery Helper**  
Script to auto-find Selenium selectors for new fund houses.

---

## Commands for V1

```bash
# Activate environment
cd backend
source .venv/bin/activate

# Fetch only (download Excel files)
python scripts/run_monthly.py --step fetch --month 2026-06

# Parse only (convert Excel to CSV)
python scripts/run_monthly.py --step parse --month 2026-06

# Full pipeline (fetch + parse)
python scripts/run_monthly.py --step all --month 2026-06

# Discover Selenium selectors
python scripts/discover_downloads.py --amc nippon

# Check what files exist
ls -lh data/raw/        # Downloaded Excel files
ls -lh data/processed/  # Normalized CSV files

# View a CSV
head -20 data/processed/nippon_2026-06_normalized.csv
```

---

## V1 Timeline

**Today:**
- [ ] Read `QUICKSTART_V1.md` (5 min)
- [ ] Read `V1_ARCHITECTURE.md` (10 min)
- [ ] Configure `funds.yaml` (15 min)

**Tomorrow:**
- [ ] Download sample disclosure files
- [ ] Place in `data/raw/`
- [ ] Implement one parser (Nippon)
- [ ] Test: `python scripts/run_monthly.py --step parse`

**This Week:**
- [ ] Implement remaining parsers (SBI, others)
- [ ] Test full pipeline end-to-end
- [ ] Handle edge cases

**Next Week:**
- [ ] Ready for more fund houses
- [ ] Ready to move to V2 (database, sheets, API)

---

## Transition to V2

When you're ready to add **database + analytics + sheets**:

1. **Uncomment database setup** in `.env`
2. **Run migrations:** `alembic upgrade head`
3. **Activate storage module** in `run_monthly.py`
4. **Update parser.py** to save to database instead of CSV
5. **Implement analytics** in `src/analytics/`
6. **Implement sheets exporter** in `src/exporters/sheets_writer.py`
7. **Activate API** in `src/api/`

No rework needed—everything is scaffolded and ready!

---

## Documentation Structure for V1

| Document | Purpose | Read When |
|----------|---------|-----------|
| **QUICKSTART_V1.md** | Get started in 5 min | Now! |
| **V1_ARCHITECTURE.md** | Understand V1 design | Before implementing |
| **docs/web_scraping_guide.md** | File download automation | Setting up Selenium |
| **BUILD_SUMMARY.md** | Full project overview | Reference |
| **mf_tracker_architecture.md** | Original vision | Understanding V2+ |

---

## FAQ for V1

**Q: Do I really need to skip the database?**  
A: For V1, yes—focuses on getting data flowing. Database is ready for V2.

**Q: Can I manually download files instead of Selenium?**  
A: Yes! Just place in `data/raw/{amc_id}_{YYYY-MM}.xlsx` and run parse.

**Q: How do I handle a new fund house?**  
A: 1. Add to `funds.yaml`, 2. Implement parser class, 3. Configure Selenium selectors (or use manual).

**Q: When should I move to V2?**  
A: After V1 is stable and you want persistence + analytics + web access.

**Q: Is my V1 work wasted when moving to V2?**  
A: No! V1 parsers work exactly the same in V2. Just add database saving.

---

## Key Files to Edit

```
PRIORITY 1 (Critical):
  backend/config/funds.yaml                    ← Add your 10 funds

PRIORITY 2 (Implementation):
  backend/src/parsing/amc/nippon.py          ← Implement normalize()
  backend/src/parsing/amc/sbi.py             ← Implement normalize()

PRIORITY 3 (Testing):
  None - just run: python scripts/run_monthly.py --step all
```

---

## Ready? 🚀

1. Open [QUICKSTART_V1.md](QUICKSTART_V1.md)
2. Configure `funds.yaml`
3. Download sample Excel files
4. Implement parsers
5. Run: `python scripts/run_monthly.py --step all --month 2026-06`
6. Check `data/processed/` for CSVs

**That's V1!** Simple, focused, working. 🎉
