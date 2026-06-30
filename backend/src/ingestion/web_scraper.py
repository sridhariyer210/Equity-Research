"""
Web scraper module - handles dynamic/JavaScript-heavy websites.
Uses Selenium for sites that require JavaScript rendering or complex navigation.
"""
import logging
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

logger = logging.getLogger(__name__)


class SeleniumDownloader:
    """Downloads files from dynamic websites using Selenium WebDriver"""

    def __init__(self, headless: bool = True):
        """
        Initialize Selenium WebDriver.
        
        Args:
            headless: Run browser in headless mode (no UI)
        """
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
        
        # Setup download preferences
        prefs = {
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
        }
        options.add_experimental_option("prefs", prefs)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def download_file(
        self,
        base_url: str,
        link_text_pattern: str,
        destination: Path,
        wait_element: str = "body",
        wait_timeout: int = 10,
    ) -> bool:
        """
        Download file from a website by finding and clicking a link.
        
        Args:
            base_url: URL to navigate to
            link_text_pattern: Partial text to match in link (e.g., "Monthly portfolio")
            destination: Path to save the file
            wait_element: CSS selector of element to wait for before clicking
            wait_timeout: How long to wait for elements to load (seconds)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.setup_driver()
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Navigating to {base_url}")
            self.driver.get(base_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, wait_timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, wait_element))
            )
            
            # Add delay for JavaScript to fully render
            time.sleep(2)
            
            # Find link by partial text match
            links = self.driver.find_elements(By.TAG_NAME, "a")
            target_link = None
            
            for link in links:
                link_text = link.text.strip()
                if link_text_pattern.lower() in link_text.lower():
                    target_link = link
                    logger.info(f"Found link: {link_text}")
                    break
            
            if not target_link:
                logger.error(f"Could not find link with text containing '{link_text_pattern}'")
                return False
            
            # Get the download URL
            download_url = target_link.get_attribute("href")
            if not download_url:
                logger.error("Link has no href attribute")
                return False
            
            logger.info(f"Download URL: {download_url}")
            
            # Handle relative URLs
            if download_url.startswith("/"):
                from urllib.parse import urlparse
                parsed = urlparse(base_url)
                download_url = f"{parsed.scheme}://{parsed.netloc}{download_url}"
            
            # Click the link and download
            target_link.click()
            
            # Wait for download to complete (check if file exists)
            max_wait = 30
            while max_wait > 0:
                if destination.exists():
                    logger.info(f"Downloaded successfully: {destination}")
                    return True
                time.sleep(1)
                max_wait -= 1
            
            logger.error("Download timeout - file not created")
            return False
            
        except Exception as e:
            logger.error(f"Selenium download failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

    def discover_download_links(self, base_url: str, wait_timeout: int = 10) -> list:
        """
        Discover all downloadable links on a page.
        Useful for finding the correct selectors and link patterns.
        
        Args:
            base_url: URL to scan
            wait_timeout: How long to wait for page to load
            
        Returns:
            List of dicts with link text and href
        """
        try:
            self.setup_driver()
            
            logger.info(f"Scanning {base_url} for download links...")
            self.driver.get(base_url)
            
            WebDriverWait(self.driver, wait_timeout).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
            )
            
            time.sleep(2)
            
            links = []
            for link in self.driver.find_elements(By.TAG_NAME, "a"):
                text = link.text.strip()
                href = link.get_attribute("href")
                if text and href and ("portfolio" in text.lower() or "disclosure" in text.lower()):
                    links.append({"text": text, "href": href})
            
            return links
            
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
