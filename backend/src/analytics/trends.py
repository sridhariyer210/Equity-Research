"""Trends - month-over-month and time-series analysis"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def compute_stock_trends(current_holdings: pd.DataFrame, previous_holdings: pd.DataFrame) -> pd.DataFrame:
    """
    Compare holdings month-over-month.
    Identify entries, exits, and position size changes.
    
    Args:
        current_holdings: Latest month holdings
        previous_holdings: Previous month holdings
        
    Returns:
        DataFrame with trend metrics
    """
    # TODO: Implement trend calculation
    pass
