"""SBI Mutual Fund parser"""
from src.parsing.amc.base import BaseAMCParser
import pandas as pd


class SBIParser(BaseAMCParser):
    """Parser for SBI Mutual Fund (single-file format)"""

    def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
        """Read entire SBI Excel file"""
        df = pd.read_excel(file_path)
        return df

    def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
        """Normalize SBI-specific columns to standard schema"""
        # TODO: Implement SBI-specific normalization
        pass
