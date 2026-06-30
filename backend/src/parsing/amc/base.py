"""
Base AMC parser - abstract base class for all AMC-specific parsers.
Every AMC parser must inherit this and implement both methods.
"""
from abc import ABC, abstractmethod
import pandas as pd


class BaseAMCParser(ABC):
    """Abstract base class for AMC-specific parsers"""

    @abstractmethod
    def get_raw_dataframe(self, file_path: str, fund_config: dict) -> pd.DataFrame:
        """
        Read the raw file and return a DataFrame for the specific fund.
        For multi_tab AMCs: read the correct sheet.
        For single_file AMCs: read the whole file.
        """
        pass

    @abstractmethod
    def normalize(self, df: pd.DataFrame, fund_config: dict) -> pd.DataFrame:
        """
        Map AMC-specific column names to the standard schema:
        [date, fund_id, isin, stock_name, sector, instrument_type,
         market_value_cr, pct_of_nav, rank_in_fund]
        """
        pass
