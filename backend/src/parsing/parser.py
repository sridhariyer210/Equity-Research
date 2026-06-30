"""
Parser orchestration - V1: Parses raw files to normalized CSVs (no database)

Process:
1. Load funds.yaml configuration
2. Find raw files in data/raw/
3. For each AMC, instantiate correct parser
4. Export normalized CSV to data/processed/
"""
import logging
import pandas as pd
import yaml
from datetime import date
from pathlib import Path
from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.parsing.normalizer import normalize_holdings

logger = logging.getLogger(__name__)


def parse_and_export(config_path: str, month: date) -> dict:
    """
    Parse raw files for all AMCs and export to CSV.
    
    Args:
        config_path: Path to funds.yaml
        month: Month to process (YYYY-MM-01 format)
        
    Returns:
        dict of {amc_id: output_csv_path}
    """
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    amcs = {amc['id']: amc for amc in config.get('amcs', [])}
    funds = {fund['id']: fund for fund in config.get('funds', [])}
    
    results = {}
    
    for amc_id, amc_config in amcs.items():
        # Find raw file for this AMC
        raw_file = _find_raw_file(amc_id, month)
        
        if not raw_file:
            logger.warning(f"[{amc_id}] No raw file found for {month.strftime('%Y-%m')}")
            continue
        
        try:
            logger.info(f"[{amc_id}] Parsing {raw_file.name}...")
            
            # Get all funds for this AMC
            amc_funds = [f for f in funds.values() if f['amc_id'] == amc_id and f['is_active']]
            
            if not amc_funds:
                logger.warning(f"[{amc_id}] No active funds configured")
                continue
            
            # Parse and aggregate all funds from this AMC
            all_holdings = []
            
            for fund in amc_funds:
                try:
                    holdings_df = _parse_fund(raw_file, amc_config, fund)
                    if not holdings_df.empty:
                        all_holdings.append(holdings_df)
                        logger.info(f"  ✓ {fund['id']}: {len(holdings_df)} holdings")
                except Exception as e:
                    logger.error(f"  ✗ {fund['id']}: {e}")
            
            if all_holdings:
                # Combine all funds for this AMC
                combined_df = pd.concat(all_holdings, ignore_index=True)
                
                # Export to CSV
                output_path = _get_output_path(amc_id, month)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                combined_df.to_csv(output_path, index=False)
                
                logger.info(f"[{amc_id}] ✓ Exported {len(combined_df)} rows to {output_path.name}")
                results[amc_id] = output_path
            else:
                logger.warning(f"[{amc_id}] No holdings parsed")
        
        except Exception as e:
            logger.error(f"[{amc_id}] Parse failed: {e}", exc_info=True)
    
    return results


def _parse_fund(raw_file: Path, amc_config: dict, fund_config: dict) -> pd.DataFrame:
    """
    Parse a single fund using the appropriate AMC parser.
    
    Args:
        raw_file: Path to raw Excel file
        amc_config: AMC configuration from funds.yaml
        fund_config: Fund configuration from funds.yaml
        
    Returns:
        DataFrame with normalized holdings
    """
    amc_id = amc_config['id']
    
    # Import appropriate parser
    if amc_id == 'nippon':
        from src.parsing.amc.nippon import NipponParser
        parser = NipponParser()
    elif amc_id == 'sbi':
        from src.parsing.amc.sbi import SBIParser
        parser = SBIParser()
    else:
        raise NotImplementedError(f"Parser not implemented for AMC: {amc_id}")
    
    # Get raw dataframe
    raw_df = parser.get_raw_dataframe(str(raw_file), fund_config)
    
    # Normalize to standard schema
    normalized_df = parser.normalize(raw_df, fund_config)
    
    # Add metadata
    normalized_df['fund_id'] = fund_config['id']
    normalized_df['date'] = pd.Timestamp(year=2026, month=6, day=1)  # Use appropriate month
    
    return normalized_df


def _find_raw_file(amc_id: str, month: date) -> Path | None:
    """Find raw Excel file for AMC + month combination"""
    raw_dir = Path(RAW_DATA_DIR)
    
    if not raw_dir.exists():
        return None
    
    # Try standard naming: {amc_id}_{YYYY-MM}.xlsx
    expected_path = raw_dir / f"{amc_id}_{month.strftime('%Y-%m')}.xlsx"
    if expected_path.exists():
        return expected_path
    
    # Try alternative patterns
    month_str = month.strftime('%Y-%m')
    month_no_dash = month.strftime('%Y%m')
    
    for pattern in [f"*{amc_id}*{month_str}*", f"*{amc_id}*{month_no_dash}*"]:
        matches = list(raw_dir.glob(pattern))
        if matches:
            return matches[0]
    
    return None


def _get_output_path(amc_id: str, month: date) -> Path:
    """Generate output CSV path"""
    filename = f"{amc_id}_{month.strftime('%Y-%m')}_normalized.csv"
    return Path(PROCESSED_DATA_DIR) / filename

