"""
Normalizer - Maps AMC-specific columns to standard CSV schema (V1: No database)

All normalized data is exported to CSV with this standard schema:
- fund_id: Fund identifier
- date: First day of month (YYYY-MM-01)
- isin: ISIN code
- stock_name: Name of holding
- sector: Sector classification  
- instrument_type: equity | debt | etf | reit
- market_value_cr: Value in crores
- pct_of_nav: Percentage of NAV
- rank_in_fund: Rank within fund (1=largest)
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def normalize_holdings(df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
    """
    Normalize holdings DataFrame to standard CSV schema.
    
    Each AMC parser's normalize() method should return a DataFrame with these columns:
    - fund_id
    - date
    - isin
    - stock_name
    - sector
    - instrument_type
    - market_value_cr
    - pct_of_nav
    - rank_in_fund
    
    Args:
        df: Raw DataFrame from AMC-specific parser
        fund_config: Fund configuration from funds.yaml
        
    Returns:
        Normalized DataFrame with standard schema
    """
    # This is called by individual AMC parsers
    # Each parser's normalize() method implements this mapping
    # Example for Nippon:
    #   normalized = pd.DataFrame({
    #       'fund_id': fund_config['fund_id'],
    #       'isin': df['ISIN'],
    #       'stock_name': df['Scrip Name'],
    #       'sector': df['Sector'],
    #       ...
    #   })
    
    logger.info(f"Normalizing {len(df)} holdings for {fund_config['fund_id']}")
    return df


# Standard CSV schema definition
STANDARD_SCHEMA = {
    'fund_id': 'str',           # Fund identifier
    'date': 'datetime64[ns]',   # First day of month
    'isin': 'str',              # Security ISIN code
    'stock_name': 'str',        # Security name
    'sector': 'str',            # Sector classification
    'instrument_type': 'str',   # equity|debt|etf|reit
    'market_value_cr': 'float', # Value in crores
    'pct_of_nav': 'float',      # Percentage of NAV
    'rank_in_fund': 'int',      # Rank in fund (1=largest)
}


def validate_schema(df: pd.DataFrame) -> bool:
    """
    Validate DataFrame has standard schema.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_cols = set(STANDARD_SCHEMA.keys())
    actual_cols = set(df.columns)
    
    if required_cols != actual_cols:
        missing = required_cols - actual_cols
        extra = actual_cols - required_cols
        
        if missing:
            logger.warning(f"Missing columns: {missing}")
        if extra:
            logger.warning(f"Extra columns: {extra}")
        
        return False
    
    return True

