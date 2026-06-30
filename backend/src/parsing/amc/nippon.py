"""Nippon India Mutual Fund parser"""
from src.parsing.amc.base import BaseAMCParser
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class NipponParser(BaseAMCParser):
    """Parser for Nippon India Mutual Fund (multi-tab format)"""

    def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
        """Read specific sheet from multi-tab Nippon Excel file"""
        sheet_name = fund_config.get('sheet_name')
        if not sheet_name:
            raise ValueError(f"sheet_name required for Nippon fund: {fund_config['fund_id']}")
        
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df

    def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
        """
        Normalize Nippon-specific columns to standard schema.
        
        Nippon column mapping:
            ISIN → isin
            Security Name → stock_name
            Sector → sector
            Market Value (Rs. Cr.) → market_value_cr
            % of NAV → pct_of_nav
        """
        # Map Nippon columns to standard schema
        normalized = pd.DataFrame()
        
        # Direct column mappings
        normalized['isin'] = df['ISIN'].astype(str).str.strip()
        normalized['stock_name'] = df['Security Name'].astype(str).str.strip()
        normalized['sector'] = df['Sector'].astype(str).str.strip()
        
        # Numeric columns - handle potential formatting issues
        normalized['market_value_cr'] = pd.to_numeric(
            df['Market Value (Rs. Cr.)'], 
            errors='coerce'
        )
        normalized['pct_of_nav'] = pd.to_numeric(
            df['% of NAV'], 
            errors='coerce'
        )
        
        # Default instrument type to equity
        normalized['instrument_type'] = 'equity'
        
        # Calculate rank by market value (descending)
        normalized['rank_in_fund'] = (
            normalized['market_value_cr']
            .rank(method='min', ascending=False)
            .astype(int)
        )
        
        # Remove rows with invalid data
        normalized = normalized.dropna(subset=['isin', 'market_value_cr'])
        
        logger.info(f"✓ Normalized {len(normalized)} holdings for {fund_config['id']}")
        
        return normalized

