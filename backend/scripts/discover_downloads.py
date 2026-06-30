"""
Utility script to discover download links and CSS selectors for AMCs.
Helps with configuring new fund houses in funds.yaml.

Usage:
    python scripts/discover_downloads.py --amc nippon
    python scripts/discover_downloads.py --amc sbi --show-selectors
"""
import argparse
import logging
from pathlib import Path
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import from src
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.fetcher import discover_links


def main():
    parser = argparse.ArgumentParser(
        description="Discover download links and selectors for AMCs"
    )
    parser.add_argument(
        "--amc",
        required=True,
        help="AMC ID (e.g., 'nippon', 'sbi')"
    )
    parser.add_argument(
        "--config",
        default="config/funds.yaml",
        help="Path to funds.yaml config"
    )
    parser.add_argument(
        "--show-selectors",
        action="store_true",
        help="Show CSS selectors for each link"
    )
    
    args = parser.parse_args()
    
    print(f"\n🔍 Discovering download links for {args.amc}...")
    print("-" * 80)
    
    try:
        links = discover_links(args.amc, args.config)
        
        if not links:
            print(f"❌ No links found. Check if base_url is correct in {args.config}")
            return
        
        print(f"\n✓ Found {len(links)} download links:\n")
        
        for i, link in enumerate(links, 1):
            text = link['text']
            href = link['href']
            
            print(f"{i}. {text}")
            if args.show_selectors:
                print(f"   Link: {href}")
            print()
        
        # Suggest config update
        print("\n" + "="*80)
        print("📋 SUGGESTED CONFIG UPDATE for funds.yaml:\n")
        
        # Extract a good link text pattern from the first link
        first_link_text = links[0]['text']
        
        # Try to find a month pattern (e.g., "May 2026")
        import re
        month_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', first_link_text)
        
        if month_match:
            pattern_suggestion = f"Monthly portfolio for the month of"
        else:
            # Use first few words
            pattern_suggestion = " ".join(first_link_text.split()[:4])
        
        print(f"""
amcs:
  - id: {args.amc}
    name: {args.amc.title()} Mutual Fund
    file_pattern: multi_tab  # or single_file
    download_method: selenium
    base_url: "{links[0]['href'].split('?')[0] if links[0]['href'] else ''}"
    selectors:
      link_text_pattern: "{pattern_suggestion}"
      link_selector: "a"
      wait_element: "body"
        """)
        
        print("\n💡 Tips:")
        print("  - Update 'base_url' with the correct portfolio disclosures page URL")
        print("  - Update 'link_text_pattern' with text that matches the month-specific link")
        print("  - Test with: python -c \"from src.ingestion.fetcher import discover_links; discover_links('{args.amc}', 'config/funds.yaml')\"")
        
    except Exception as e:
        logger.error(f"Failed to discover links: {e}")
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print(f"  1. {args.amc} is defined in {args.config}")
        print(f"  2. base_url is filled in for {args.amc}")
        print("  3. Chrome/Chromium browser is installed")
        print("  4. Internet connection is available")


if __name__ == "__main__":
    main()
