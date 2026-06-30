# 📥 Manual Download Guide for V1

Since some fund houses use JavaScript-heavy websites, V1 supports **manual file upload** for testing and initial setup.

## Quick Start (2 minutes)

1. **Visit Nippon's disclosure page:**
   - Go to: https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures
   - Click "FACTSHEET PORTFOLIO AND OTHER DISCLOSURES"
   - A dropdown or modal should appear with month-specific links

2. **Download the Excel file for your desired month:**
   - Look for: "Monthly Portfolio for the month of June 2026" (or your target month)
   - Download the Excel file

3. **Place in correct folder:**
   ```bash
   # Move to data/raw/ with naming convention: {amc_id}_{YYYY-MM}.xlsx
   mv ~/Downloads/nippon_portfolio_june_2026.xlsx backend/data/raw/nippon_2026-06.xlsx
   ```

4. **Run the pipeline:**
   ```bash
   cd backend
   python scripts/run_monthly.py --step all --month 2026-06
   ```

---

## Detailed Steps

### Step 1: Visit Nippon's Disclosure Page

Open in browser:
```
https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures
```

### Step 2: Find Monthly Portfolio

On the page you'll see a section titled "FACTSHEET PORTFOLIO AND OTHER DISCLOSURES".

Click it to reveal monthly portfolio options. You should see something like:
- Monthly Portfolio for the month of June 2026
- Monthly Portfolio for the month of May 2026
- etc.

### Step 3: Download Excel File

Click on the month you want (e.g., June 2026) and save the file.

**Downloaded file should look like:**
```
nippon_monthly_portfolio_june_2026.xlsx
```

### Step 4: Move to data/raw/

Move the downloaded file to the correct location with the V1 naming convention:

```bash
# From your project root:
cd backend

# Move file with V1 naming convention: {amc_id}_{YYYY-MM}.xlsx
mv ~/Downloads/nippon_monthly_portfolio_june_2026.xlsx data/raw/nippon_2026-06.xlsx

# Verify it's there:
ls -la data/raw/
```

Expected output:
```
-rw-r--r--  nippon_2026-06.xlsx
```

### Step 5: Run Pipeline

```bash
# Still in backend folder
python scripts/run_monthly.py --step parse --month 2026-06
```

This will:
1. Read the Excel from `data/raw/nippon_2026-06.xlsx`
2. Parse it using the Nippon parser
3. Export normalized CSV to `data/processed/nippon_2026-06_normalized.csv`

### Step 6: Check Output

```bash
# View the output
head -10 data/processed/nippon_2026-06_normalized.csv

# Expected format:
# fund_id,date,isin,stock_name,sector,instrument_type,market_value_cr,pct_of_nav,rank_in_fund
# nippon_small_cap,2026-06-01,INF001,Company Name,Sector,equity,150.5,2.5,1
```

---

## Naming Convention

All files in `data/raw/` must follow this pattern:

```
{amc_id}_{YYYY-MM}.xlsx

Examples:
  nippon_2026-06.xlsx          ← Nippon for June 2026
  sbi_2026-06.xlsx             ← SBI for June 2026
  axis_2026-06.xlsx            ← Axis for June 2026
  hdfc_2026-05.xlsx            ← HDFC for May 2026
```

The `{amc_id}` must match the `id` field in `funds.yaml`:

```yaml
amcs:
  - id: nippon          ← Use this ID in filename
  - id: sbi             ← Use this ID in filename
```

---

## Troubleshooting

### Problem: "No raw file found for 2026-06"

**Solution:** Check that the file exists and has the correct name:
```bash
ls -la backend/data/raw/nippon_2026-06.xlsx

# If not found:
# 1. Check downloaded file name
# 2. Rename to match pattern
# 3. Move to backend/data/raw/
```

### Problem: Parser crashes when reading Excel

**Possible causes:**
- File is corrupted - redownload from Nippon's website
- File has wrong sheet name - check `sheet_name` in `funds.yaml`
- File format not supported - must be `.xlsx` (Excel), not `.xls` or `.csv`

**Solution:**
```bash
# Check sheet names in Excel
python -c "
import openpyxl
wb = openpyxl.load_workbook('backend/data/raw/nippon_2026-06.xlsx')
print('Sheet names:', wb.sheetnames)
"

# Update sheet_name in funds.yaml if needed
```

### Problem: CSV output is empty

**Check parser implementation:**
- Nippon parser's `normalize()` method must be implemented
- See: [QUICKSTART_V1.md](QUICKSTART_V1.md) for parser implementation guide

---

## V1 Workflow

```
Manual Download (You)
    ↓
browser: https://mf.nipponindiaim.com/...
    ↓ (Download Excel)
~/Downloads/nippon_portfolio_june_2026.xlsx
    ↓ (Move to data/raw/)
backend/data/raw/nippon_2026-06.xlsx
    ↓
python scripts/run_monthly.py --step all
    ↓ (Parse & Normalize)
backend/data/processed/nippon_2026-06_normalized.csv
    ↓ (V2: Upload to Sheets/DB)
Google Sheets
```

---

## Adding More Funds

To test with multiple funds:

1. **Download Excel from each AMC:**
   - Nippon: https://mf.nipponindiaim.com/...
   - SBI: https://www.sbimf.com/...
   - etc.

2. **Place in data/raw/ with correct names:**
   ```bash
   backend/data/raw/nippon_2026-06.xlsx
   backend/data/raw/sbi_2026-06.xlsx
   ```

3. **Update funds.yaml** with new funds (see [QUICKSTART_V1.md](QUICKSTART_V1.md))

4. **Implement parser** for new AMC (see [QUICKSTART_V1.md](QUICKSTART_V1.md))

5. **Run pipeline:**
   ```bash
   python scripts/run_monthly.py --step all --month 2026-06
   ```

---

## Downloading Without Browser (Advanced)

If you have a direct download link, you can use curl:

```bash
# If you know the direct URL
curl -o backend/data/raw/nippon_2026-06.xlsx "https://direct-url-to-file.xlsx"
```

But for now, **browser download is recommended** since the websites use JavaScript.

---

## Next Steps

1. ✅ Download Nippon Excel from their website
2. ✅ Place in `backend/data/raw/nippon_2026-06.xlsx`
3. → Implement Nippon parser's `normalize()` method
4. → Run `python scripts/run_monthly.py --step parse`
5. → Check output in `backend/data/processed/`

See [QUICKSTART_V1.md](QUICKSTART_V1.md) for parser implementation! 🚀
