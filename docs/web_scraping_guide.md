# Web Scraping & File Download Guide

## The Challenge

Each mutual fund house has a different website structure for portfolio disclosures:
- **Nippon**: JavaScript-heavy, dynamic content loading
- **SBI**: Different layout and link structure
- **Others**: Completely custom implementations

Manual clicking is impractical for automation. This guide explains the solution.

---

## Solution: 3-Tier Fallback System

```
┌─────────────────────────────────────┐
│ Try 1: Direct HTTP Download         │  (fast, if static URL available)
│ (direct_url in config)              │
└────────────┬────────────────────────┘
             │ (fails)
             ▼
┌─────────────────────────────────────┐
│ Try 2: Selenium Web Scraping        │  (handles JavaScript & dynamic content)
│ (base_url + selectors in config)    │
└────────────┬────────────────────────┘
             │ (fails)
             ▼
┌─────────────────────────────────────┐
│ Try 3: Manual Upload                │  (user drops file in data/raw/)
│ (fallback for complex sites)        │
└─────────────────────────────────────┘
```

---

## Step 1: Install Browser Automation

The Selenium approach requires Chrome/Chromium browser:

```bash
# macOS
brew install chromium

# Linux
sudo apt-get install chromium-browser

# Or install Chrome from https://www.google.com/chrome/
```

---

## Step 2: Configure Fund House in funds.yaml

### Example: Nippon India

```yaml
amcs:
  - id: nippon
    name: Nippon India Mutual Fund
    file_pattern: multi_tab
    download_method: selenium         # ← Use Selenium for this fund house
    base_url: "https://mf.nipponindiaim.com/investor-service/downloads/factsheet-portfolio-and-other-disclosures"
    selectors:
      link_text_pattern: "Monthly portfolio for the month of"  # ← Text in the link
      link_selector: "a[href*='portfolio']"                   # ← CSS selector (optional)
      wait_element: ".downloads-section"                      # ← Element to wait for before scraping
```

### Configuration Fields Explained

| Field | Purpose | Example |
|-------|---------|---------|
| `download_method` | "direct" &#124; "selenium" &#124; "manual" | "selenium" |
| `base_url` | URL of the disclosures page | Portfolio downloads page URL |
| `link_text_pattern` | Partial text to match in download link | "Monthly portfolio" |
| `wait_element` | CSS selector to wait for before scraping | ".downloads" |
| `direct_url` | (Optional) Direct URL if available | Full URL to Excel file |

---

## Step 3: Discover Configuration Using Helper Script

If you're unsure about the correct selectors, use the discovery script:

```bash
cd backend
source .venv/bin/activate

# Discover all download links for Nippon
python scripts/discover_downloads.py --amc nippon

# Show CSS selectors for each link
python scripts/discover_downloads.py --amc nippon --show-selectors
```

**Output example:**
```
🔍 Discovering download links for nippon...
────────────────────────────────────────────────────────────────────────────────

✓ Found 12 download links:

1. Monthly portfolio for the month of May 2026
   Link: https://mf.nipponindiaim.com/...

2. Monthly portfolio for the month of April 2026
   Link: https://mf.nipponindiaim.com/...

...

📋 SUGGESTED CONFIG UPDATE for funds.yaml:

amcs:
  - id: nippon
    name: Nippon Mutual Fund
    file_pattern: multi_tab
    download_method: selenium
    base_url: "https://mf.nipponindiaim.com/investor-service/downloads/..."
    selectors:
      link_text_pattern: "Monthly portfolio for the month of"
      link_selector: "a"
      wait_element: "body"
```

---

## Step 4: Test Your Configuration

```bash
# Test the fetcher with your config
python -c "
from src.ingestion.fetcher import fetch_all
from datetime import date
downloads = fetch_all('config/funds.yaml', date(2026, 5, 1))
for amc_id, path in downloads.items():
    print(f'{amc_id}: {path}')
"
```

---

## Step 5: Fallback to Manual Upload (If Selenium Fails)

If a fund house's website is too complex or changes structure:

1. **Manually download the Excel file** from the fund house website
2. **Place it in** `backend/data/raw/` folder
3. **Name it** as: `{amc_id}_{YYYY-MM}.xlsx`

**Example filenames:**
```
backend/data/raw/nippon_2026-05.xlsx
backend/data/raw/sbi_2026-05.xlsx
backend/data/raw/axis_2026-05.xlsx
```

The fetcher will automatically detect these files and use them!

---

## Adding a New Fund House

### Quick Steps

1. **Visit the fund house's portfolio disclosure page**
2. **Note the URL** (e.g., `https://fund-house.com/disclosures`)
3. **Run the discovery script** with `base_url`
4. **Copy the suggested config** into `funds.yaml`
5. **Add fund entries** under the `funds:` section

### Example: Adding HDFC Mutual Fund

```yaml
amcs:
  - id: hdfc
    name: HDFC Mutual Fund
    file_pattern: single_file
    download_method: selenium
    base_url: "https://www.hdfcfund.com/en/investors/portfolio-disclosures"
    selectors:
      link_text_pattern: "Portfolio"
      link_selector: "a.download-link"
      wait_element: ".disclosure-list"

funds:
  - id: hdfc_small_cap
    name: HDFC Small Cap Fund
    cap_category: small_cap
    amfi_code: "INF175K01TT6"
    amc_id: hdfc
    sheet_name: null
    is_active: true
```

---

## Troubleshooting

### ❌ "Chrome/Chromium not found"
```bash
# Install Chrome
brew install chromium  # macOS
sudo apt-get install chromium-browser  # Linux

# Or specify Chrome path in environment
export CHROMEDRIVER_PATH=/usr/bin/chromium
```

### ❌ "Timeout waiting for element"
- Increase `wait_timeout` in fetcher call
- Check if the `wait_element` CSS selector is correct
- Run discovery script to verify link exists

### ❌ "No link found with pattern 'X'"
- Use discovery script to see actual link text
- Update `link_text_pattern` to match exactly
- Note: Pattern matching is case-insensitive

### ❌ "Download failed but file not saved"
- Check file permissions in `backend/data/raw/`
- Verify Chrome sandbox settings (`--no-sandbox` is set)
- Try manual upload as fallback

---

## Running the Full Pipeline

```bash
cd backend
source .venv/bin/activate

# For current month
python scripts/run_monthly.py --step all

# For specific month
python scripts/run_monthly.py --step all --month 2026-05

# Just fetch (test your configurations)
python scripts/run_monthly.py --step fetch --month 2026-05
```

---

## Advanced: Custom Selenium Scripts

For very complex fund houses, you can write custom Selenium code:

```python
# backend/src/ingestion/custom_scrapers.py
from src.ingestion.web_scraper import SeleniumDownloader

def download_custom_fund_house(destination):
    scraper = SeleniumDownloader(headless=False)  # Show browser during debug
    scraper.setup_driver()
    
    scraper.driver.get("https://fund-house.com/disclosures")
    
    # Custom logic for this fund house
    # Click buttons, fill forms, etc.
    
    scraper.driver.find_element("id", "some_button").click()
    # ... more custom interactions
    
    scraper.driver.quit()
```

---

## Key Points to Remember

✓ **Configuration-first**: Add/update fund in `funds.yaml`, no code changes
✓ **Discovery script**: Use it to find correct selectors before manual config
✓ **Fallback to manual**: If web scraping breaks, just drop file in `data/raw/`
✓ **Month format**: Files are named `{amc_id}_{YYYY-MM}.xlsx` (first of month)
✓ **Headless mode**: Selenium runs without showing browser (faster, no UI)

---

## Next Steps

1. Update `funds.yaml` with Nippon and SBI URLs
2. Run discovery script for each AMC
3. Test fetch for current month
4. If issues, use manual upload as fallback
