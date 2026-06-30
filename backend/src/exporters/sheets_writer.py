"""
Google Sheets writer - V1: Exports processed CSVs to Sheets (no database)

Process:
1. Load all CSV files from data/processed/ for the month
2. Create/update Google Sheets workbook with tabs:
   - Summary: Weighted average holdings across funds
   - Detail: Fund × Stock matrix
   - Stock Trends: MoM changes
   - Fund Overlap: Which stocks appear in N+ funds
3. Update via Google Sheets API
"""
import logging
import pandas as pd
import gspread
from pathlib import Path
from datetime import date
from config.settings import PROCESSED_DATA_DIR, GOOGLE_SHEETS_CREDENTIALS_PATH, GOOGLE_SHEETS_SPREADSHEET_ID

logger = logging.getLogger(__name__)


def push_to_sheets(config_path: str, month: date) -> None:
    """
    Export all processed CSVs for a month to Google Sheets.
    
    Args:
        config_path: Path to funds.yaml (for reference)
        month: Month to export (YYYY-MM-01 format)
    """
    # Check if credentials are configured
    if not GOOGLE_SHEETS_CREDENTIALS_PATH or not GOOGLE_SHEETS_SPREADSHEET_ID:
        logger.warning("Google Sheets not configured in .env")
        logger.warning("  - Set GOOGLE_SHEETS_CREDENTIALS_PATH")
        logger.warning("  - Set GOOGLE_SHEETS_SPREADSHEET_ID")
        logger.warning("Skipping Google Sheets export for V1")
        return
    
    try:
        # For V1: Just log what would be exported
        processed_dir = Path(PROCESSED_DATA_DIR)
        
        if not processed_dir.exists():
            logger.warning(f"No processed data found in {processed_dir}")
            return
        
        # Find all CSVs for this month
        month_str = month.strftime('%Y-%m')
        csv_files = list(processed_dir.glob(f"*{month_str}*.csv"))
        
        if not csv_files:
            logger.warning(f"No processed CSV files found for {month_str}")
            return
        
        logger.info(f"Found {len(csv_files)} CSV file(s) for export:")
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            logger.info(f"  - {csv_file.name}: {len(df)} rows")
        
        # V1: Log what we would do
        logger.info("\n" + "="*80)
        logger.info("GOOGLE SHEETS EXPORT (V1 - Logged Only)")
        logger.info("="*80)
        logger.info("In V2, this would:")
        logger.info("  1. Read all processed CSVs")
        logger.info("  2. Create tabs for each sheet:")
        logger.info("     - Summary: Weighted avg by stock")
        logger.info("     - Detail: Fund × Stock matrix")
        logger.info("     - Trends: MoM changes")
        logger.info("     - Overlap: Multi-fund appearances")
        logger.info("  3. Update Google Sheets workbook")
        logger.info("\nTo enable Google Sheets export:")
        logger.info("  1. Create Google service account: https://console.cloud.google.com")
        logger.info("  2. Download credentials JSON")
        logger.info("  3. Add to .env: GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/credentials.json")
        logger.info("  4. Create Sheets workbook, share with service account email")
        logger.info("  5. Add to .env: GOOGLE_SHEETS_SPREADSHEET_ID=<spreadsheet_id>")
        logger.info("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Google Sheets export failed: {e}")
        raise


def _create_summary_sheet(processed_dir: Path, month: date) -> pd.DataFrame:
    """
    Create summary sheet: weighted average holdings across all funds.
    
    Returns:
        DataFrame with columns: stock_name, avg_pct_of_nav, num_funds
    """
    # TODO: Aggregate CSVs, compute weighted averages
    pass


def _create_detail_sheet(processed_dir: Path, month: date) -> pd.DataFrame:
    """
    Create detail sheet: Fund × Stock matrix.
    
    Rows: stocks, Columns: funds
    Values: pct_of_nav
    """
    # TODO: Pivot tables from processed CSVs
    pass


def _create_trends_sheet(processed_dir: Path, month: date, prev_month: date) -> pd.DataFrame:
    """
    Create trends sheet: Month-over-month changes.
    
    Tracks: entries, exits, position size changes
    """
    # TODO: Compare CSVs from two months
    pass


def _create_overlap_sheet(processed_dir: Path, month: date) -> pd.DataFrame:
    """
    Create overlap sheet: Which stocks appear in N+ funds.
    """
    # TODO: Count fund appearances per stock
    pass

