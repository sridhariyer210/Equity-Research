"""CSV writer - exports holdings to CSV"""
import logging
import pandas as pd
from pathlib import Path
from config.settings import PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)


def export_to_csv(holdings_df: pd.DataFrame, filename: str) -> None:
    """
    Export holdings DataFrame to CSV file.
    
    Args:
        holdings_df: DataFrame to export
        filename: Output filename (will be saved in PROCESSED_DATA_DIR)
    """
    output_path = Path(PROCESSED_DATA_DIR) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    holdings_df.to_csv(output_path, index=False)
    logger.info(f"Exported to CSV: {output_path}")
