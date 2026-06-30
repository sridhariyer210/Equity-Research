"""
Fetcher: Multi-method file acquisition with fallbacks.
1. Try direct HTTP download (if direct URL available)
2. Try Selenium web scraping (for dynamic sites)
3. Fall back to manual upload (user places file in data/raw/)
"""
import os
import logging
from pathlib import Path
from datetime import date
import yaml
from config.settings import RAW_DATA_DIR
from src.ingestion.downloader import download_file, download_file_selenium, discover_download_links

logger = logging.getLogger(__name__)


def fetch_all(funds_config_path: str, month: date) -> dict:
    """
    Fetch raw files for all AMCs for a given month.
    Tries multiple download methods with fallbacks.
    
    Args:
        funds_config_path: Path to funds.yaml
        month: Month to fetch (YYYY-MM format as date object)
        
    Returns:
        dict of {amc_id: local_file_path}
    """
    # Load fund config
    with open(funds_config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    amcs = {amc['id']: amc for amc in config.get('amcs', [])}
    downloaded = {}

    for amc_id, amc_config in amcs.items():
        file_path = _get_file_path(amc_id, month)

        if file_path.exists():
            logger.info(f"[{amc_id}] File already exists locally, skipping download.")
            downloaded[amc_id] = file_path
            continue

        method = amc_config.get('download_method', 'manual')
        
        try:
            if method == 'direct':
                logger.info(f"[{amc_id}] Attempting direct HTTP download...")
                _download_direct(amc_config, file_path, month)
                downloaded[amc_id] = file_path
                
            elif method == 'selenium':
                logger.info(f"[{amc_id}] Attempting Selenium web scraping...")
                if _download_selenium(amc_config, file_path, month):
                    downloaded[amc_id] = file_path
                else:
                    raise Exception("Selenium download failed")
                    
            elif method == 'manual':
                logger.info(f"[{amc_id}] Manual upload required - check data/raw/ folder")
                manual_path = _find_manual_file(amc_id, month)
                if manual_path:
                    downloaded[amc_id] = manual_path
                    logger.info(f"[{amc_id}] Found manually uploaded file: {manual_path}")
                else:
                    logger.warning(f"[{amc_id}] No manual file found")
                    
        except Exception as e:
            logger.warning(f"[{amc_id}] Primary method failed: {e}")
            
            # Fallback 1: Try Selenium if not already tried
            if method != 'selenium':
                try:
                    logger.info(f"[{amc_id}] Falling back to Selenium...")
                    if _download_selenium(amc_config, file_path, month):
                        downloaded[amc_id] = file_path
                    else:
                        raise Exception("Selenium fallback failed")
                except Exception as e2:
                    logger.warning(f"[{amc_id}] Selenium fallback failed: {e2}")
            
            # Fallback 2: Check for manual upload
            try:
                logger.info(f"[{amc_id}] Checking for manual upload...")
                manual_path = _find_manual_file(amc_id, month)
                if manual_path:
                    downloaded[amc_id] = manual_path
                    logger.info(f"[{amc_id}] Using manually uploaded file: {manual_path}")
                else:
                    logger.error(f"[{amc_id}] No file obtained via any method. Skipping.")
            except Exception as e3:
                logger.error(f"[{amc_id}] All download methods failed: {e3}")

    return downloaded


def _download_direct(amc_config: dict, file_path: Path, month: date) -> None:
    """Download via direct HTTP URL"""
    url = amc_config.get('direct_url')
    if not url:
        raise ValueError(f"No direct_url in config")
    
    download_file(url, file_path)
    logger.info(f"Downloaded via direct URL: {file_path}")


def _download_selenium(amc_config: dict, file_path: Path, month: date) -> bool:
    """Download using Selenium web scraping"""
    base_url = amc_config.get('base_url')
    if not base_url:
        logger.error("No base_url in config")
        return False
    
    selectors = amc_config.get('selectors', {})
    link_pattern = selectors.get('link_text_pattern')
    wait_element = selectors.get('wait_element', 'body')
    
    if not link_pattern:
        logger.error("No link_text_pattern in config selectors")
        return False
    
    return download_file_selenium(
        base_url=base_url,
        link_text_pattern=link_pattern,
        destination=file_path,
        wait_element=wait_element,
    )


def _get_file_path(amc_id: str, month: date) -> Path:
    """Generate standardized file path for AMC + month"""
    return Path(RAW_DATA_DIR) / f"{amc_id}_{month.strftime('%Y-%m')}.xlsx"


def _find_manual_file(amc_id: str, month: date) -> Path | None:
    """
    Look for a manually downloaded file in data/raw/ matching naming convention.
    Supports multiple naming patterns.
    """
    expected_path = _get_file_path(amc_id, month)
    if expected_path.exists():
        return expected_path
    
    # Try alternative naming patterns (user might name it differently)
    month_str = month.strftime('%Y-%m')
    month_str_no_dash = month.strftime('%Y%m')
    
    raw_dir = Path(RAW_DATA_DIR)
    if not raw_dir.exists():
        return None
    
    for pattern in [f"*{amc_id}*{month_str}*", f"*{amc_id}*{month_str_no_dash}*", f"*{amc_id}*.xlsx"]:
        matches = list(raw_dir.glob(pattern))
        if matches:
            return matches[0]
    
    return None


def discover_links(amc_id: str, config_path: str) -> list:
    """
    Discover all download links for an AMC.
    Useful for finding the correct selectors.
    
    Usage:
        links = discover_links('nippon', 'config/funds.yaml')
        for link in links:
            print(link['text'], link['href'])
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    amcs = {amc['id']: amc for amc in config.get('amcs', [])}
    amc_config = amcs.get(amc_id)
    
    if not amc_config:
        logger.error(f"AMC {amc_id} not found in config")
        return []
    
    base_url = amc_config.get('base_url')
    if not base_url:
        logger.error(f"No base_url for {amc_id}")
        return []
    
    logger.info(f"Discovering links for {amc_id} at {base_url}")
    return discover_download_links(base_url)

