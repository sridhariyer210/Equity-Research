"""Portfolio - user portfolio overlay analytics (future)"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def compute_portfolio_metrics(user_allocations: pd.DataFrame, holdings: pd.DataFrame) -> pd.DataFrame:
    """
    Overlay user portfolio allocations on fund holdings.
    Compute portfolio-level metrics.
    
    Args:
        user_allocations: User's fund allocations
        holdings: All fund holdings
        
    Returns:
        Portfolio-level metrics
    """
    # TODO: Implement portfolio metrics
    pass
