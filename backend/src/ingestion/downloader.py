"""
Smart downloader - supports HTTP, Selenium web scraping, and manual fallback.
Tries multiple methods in order of preference.
"""
import logging
import httpx
from pathlib import Path
from config.settings import REQUEST_TIMEOUT, REQUEST_RETRY_COUNT
from src.ingestion.web_scraper import SeleniumDownloader

logger = logging.getLogger(__name__)


def download_file(
    url: str,
    destination: Path,
    timeout: int = REQUEST_TIMEOUT,
    retry_count: int = REQUEST_RETRY_COUNT,
) -> None:
    """
    Download a file from a URL with retry logic (HTTP method).
    
    Args:
        url: URL to download from
        destination: Path to save the file to
        timeout: Request timeout in seconds
        retry_count: Number of retries on failure
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    for attempt in range(retry_count):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                with open(destination, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Downloaded via HTTP: {url} → {destination}")
                return
        except Exception as e:
            logger.warning(f"HTTP attempt {attempt + 1}/{retry_count} failed: {e}")
            if attempt == retry_count - 1:
                raise


def download_file_selenium(
    base_url: str,
    link_text_pattern: str,
    destination: Path,
    wait_element: str = "body",
    wait_timeout: int = 10,
) -> bool:
    """
    Download a file using Selenium web scraping.
    Useful for dynamic/JavaScript-heavy websites.
    
    Args:
        base_url: URL to navigate to
        link_text_pattern: Partial text to match in link (e.g., "Monthly portfolio")
        destination: Path to save the file
        wait_element: CSS selector of element to wait for
        wait_timeout: How long to wait for elements (seconds)
        
    Returns:
        True if successful, False otherwise
    """
    scraper = SeleniumDownloader(headless=True)
    return scraper.download_file(
        base_url=base_url,
        link_text_pattern=link_text_pattern,
        destination=destination,
        wait_element=wait_element,
        wait_timeout=wait_timeout,
    )


def discover_download_links(base_url: str) -> list:
    """
    Discover available download links on a page.
    Useful for setup and debugging.
    
    Args:
        base_url: URL to scan
        
    Returns:
        List of dicts with link text and href
    """
    scraper = SeleniumDownloader(headless=True)
    return scraper.discover_download_links(base_url)

