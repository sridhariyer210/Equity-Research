"""
V1 Pipeline: Fetch → Parse → Export (CSV/XLSX only, no database)

Usage:
    python scripts/run_monthly.py --step fetch
    python scripts/run_monthly.py --step parse
    python scripts/run_monthly.py --step push
    python scripts/run_monthly.py --step all
    python scripts/run_monthly.py --step all --month 2026-05

Output:
    Fetch: downloads to backend/data/raw/{amc_id}_{YYYY-MM}.xlsx
    Parse: processes to backend/data/processed/{amc_id}_{YYYY-MM}_normalized.csv
    Push: exports to Google Sheets (configured in .env)
"""
import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="MF Holdings Tracker — V1 Pipeline (Fetch → Parse → Export)"
    )
    parser.add_argument(
        "--step",
        choices=["fetch", "parse", "push", "all"],
        required=True,
        help="Pipeline step to run"
    )
    parser.add_argument(
        "--month",
        type=str,
        default=None,
        help="Month to process in YYYY-MM format. Defaults to current month."
    )
    parser.add_argument(
        "--config",
        default="config/funds.yaml",
        help="Path to funds.yaml configuration"
    )
    
    args = parser.parse_args()

    # Parse month
    if args.month:
        try:
            month = datetime.strptime(args.month, "%Y-%m").date().replace(day=1)
        except ValueError:
            logger.error("Invalid month format. Use YYYY-MM (e.g., 2026-05)")
            sys.exit(1)
    else:
        today = date.today()
        month = today.replace(day=1)

    print(f"\n{'='*80}")
    print(f"MF Holdings Tracker — V1 Pipeline")
    print(f"Step: {args.step} | Month: {month.strftime('%B %Y')}")
    print(f"{'='*80}\n")

    try:
        if args.step in ("fetch", "all"):
            print("→ STEP 1: Fetching raw disclosure files...")
            _run_fetch(args.config, month)
            print("✓ Fetch completed\n")

        if args.step in ("parse", "all"):
            print("→ STEP 2: Parsing and normalizing data...")
            _run_parse(args.config, month)
            print("✓ Parse completed\n")

        if args.step in ("push", "all"):
            print("→ STEP 3: Exporting to Google Sheets...")
            _run_push(args.config, month)
            print("✓ Export completed\n")

        print(f"{'='*80}")
        print("✅ Pipeline completed successfully!")
        print(f"{'='*80}\n")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


def _run_fetch(config_path: str, month: date) -> None:
    """Fetch raw files from AMCs"""
    from src.ingestion.fetcher import fetch_all
    
    logger.info(f"Fetching files for {month.strftime('%B %Y')}...")
    downloads = fetch_all(config_path, month)
    
    if downloads:
        logger.info(f"✓ Downloaded {len(downloads)} file(s)")
        for amc_id, path in downloads.items():
            logger.info(f"  - {amc_id}: {path}")
    else:
        logger.warning("No files downloaded. Check manually placed files in data/raw/")


def _run_parse(config_path: str, month: date) -> None:
    """Parse and normalize raw files to CSV"""
    from src.parsing.parser import parse_and_export
    
    logger.info(f"Parsing files for {month.strftime('%B %Y')}...")
    results = parse_and_export(config_path, month)
    
    if results:
        logger.info(f"✓ Parsed and exported {len(results)} file(s)")
        for amc_id, path in results.items():
            logger.info(f"  - {amc_id}: {path}")
    else:
        logger.error("No files parsed. Check data/raw/ folder.")
        raise Exception("Parse failed: no input files")


def _run_push(config_path: str, month: date) -> None:
    """Export aggregated data to Google Sheets"""
    from src.exporters.sheets_writer import push_to_sheets
    
    logger.info(f"Exporting to Google Sheets for {month.strftime('%B %Y')}...")
    push_to_sheets(config_path, month)
    logger.info("✓ Data exported to Google Sheets")


if __name__ == "__main__":
    main()
