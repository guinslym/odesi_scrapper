"""
ODESI Browse Data Scraper

Scrapes survey series and surveys from ODESI API and exports to Excel.
"""

import requests
import pandas as pd
from typing import List, Dict, Any
import time
from urllib.parse import quote
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ODESIScraper:
    """Scraper for ODESI browse API."""

    BASE_URL = "https://odesi.ca/api/browse"

    # List of main categories from ODESI browse page
    CATEGORIES = [
        "Agriculture",
        "Business and Financial",
        "Census of Population",
        "Communications and Information",
        "Consumer Surveys",
        "COVID-19",
        "Crime and Justice",
        "Demographics and Population",
        "Education",
        "Elections and Politics",
        "Geography",
        "Government Finances and Economic Indicators",
        "Health",
        "Labour and Employment",
        "Natural Resources and Environment",
        "Public Opinion Polls",
        "Social Surveys",
        "Trade",
        "Travel"
    ]

    def __init__(self, delay: float = 1.0):
        """
        Initialize the scraper.

        Args:
            delay: Delay between API requests in seconds (default: 1.0)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_category_data(self, category: str) -> Dict[str, Any]:
        """
        Fetch data for a specific category.

        Args:
            category: Category name (e.g., "Agriculture")

        Returns:
            Dictionary containing the API response
        """
        url = f"{self.BASE_URL}?category={quote(category)}"
        logger.info(f"Fetching data for category: {category}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {category}: {e}")
            return {}

    def parse_category_data(self, category: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse the API response and extract series and surveys.

        Args:
            category: Category name
            data: API response data

        Returns:
            List of dictionaries containing parsed survey information
        """
        records = []

        if not data or 'content' not in data:
            logger.warning(f"No data found for category: {category}")
            return records

        content = data.get('content', {})
        datasets = content.get('datasets', {})

        # Handle case where datasets might be a string instead of object
        if not isinstance(datasets, dict):
            logger.warning(f"No datasets found for category: {category} (datasets is {type(datasets).__name__})")
            return records

        items = datasets.get('items', [])

        for series_item in items:
            series_name = series_item.get('series', 'Unknown')
            years = series_item.get('years', [])

            for year_data in years:
                year = year_data.get('year', 'Unknown')
                surveys = year_data.get('item', [])

                for survey in surveys:
                    record = {
                        'Category': category,
                        'Series_Name': series_name,
                        'Year': year,
                        'Survey_Title': survey.get('title', ''),
                        'URI': survey.get('uri', ''),
                    }
                    records.append(record)

        logger.info(f"Parsed {len(records)} records from {category}")
        return records

    def scrape_all_categories(self, categories: List[str] = None) -> pd.DataFrame:
        """
        Scrape all categories and return as DataFrame.

        Args:
            categories: List of categories to scrape (uses default if None)

        Returns:
            DataFrame containing all scraped data
        """
        if categories is None:
            categories = self.CATEGORIES

        all_records = []

        for i, category in enumerate(categories, 1):
            logger.info(f"Processing category {i}/{len(categories)}: {category}")

            # Fetch data
            data = self.fetch_category_data(category)

            # Parse data
            records = self.parse_category_data(category, data)
            all_records.extend(records)

            # Delay between requests
            if i < len(categories):
                time.sleep(self.delay)

        df = pd.DataFrame(all_records)
        logger.info(f"Total records scraped: {len(df)}")

        return df

    def find_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Find potential duplicate surveys (similar titles).

        Args:
            df: DataFrame containing survey data

        Returns:
            DataFrame containing potential duplicates
        """
        if df.empty:
            return pd.DataFrame()

        # Create a normalized title for comparison (lowercase, stripped)
        df['Title_Normalized'] = df['Survey_Title'].str.lower().str.strip()

        # Find duplicates based on normalized title, series, and year
        duplicates = df[
            df.duplicated(subset=['Title_Normalized', 'Series_Name', 'Year'], keep=False)
        ].sort_values(['Series_Name', 'Year', 'Survey_Title'])

        return duplicates.drop(columns=['Title_Normalized'])

    def export_to_excel(self, df: pd.DataFrame, filename: str = "odesi_data.xlsx"):
        """
        Export data to Excel with multiple sheets.

        Args:
            df: DataFrame containing survey data
            filename: Output filename
        """
        logger.info(f"Exporting data to {filename}")

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='All_Data', index=False)

            # Summary by category
            if not df.empty:
                category_summary = df.groupby('Category').agg({
                    'Series_Name': 'nunique',
                    'Survey_Title': 'count'
                }).rename(columns={
                    'Series_Name': 'Unique_Series',
                    'Survey_Title': 'Total_Surveys'
                })
                category_summary.to_excel(writer, sheet_name='Category_Summary')

                # Summary by series
                series_summary = df.groupby(['Category', 'Series_Name']).agg({
                    'Survey_Title': 'count',
                    'Year': ['min', 'max']
                })
                series_summary.columns = ['Survey_Count', 'First_Year', 'Last_Year']
                series_summary.to_excel(writer, sheet_name='Series_Summary')

                # Potential duplicates
                duplicates = self.find_duplicates(df)
                if not duplicates.empty:
                    duplicates.to_excel(writer, sheet_name='Potential_Duplicates', index=False)
                    logger.info(f"Found {len(duplicates)} potential duplicate records")

        logger.info(f"Export complete: {filename}")


def main():
    """Main execution function."""
    # Initialize scraper
    scraper = ODESIScraper(delay=1.0)

    # Scrape all categories
    logger.info("Starting ODESI data scraping...")
    df = scraper.scrape_all_categories()

    # Export to Excel
    if not df.empty:
        scraper.export_to_excel(df, "odesi_surveys.xlsx")
        logger.info(f"Successfully scraped {len(df)} records")
        logger.info(f"Categories: {df['Category'].nunique()}")
        logger.info(f"Unique series: {df['Series_Name'].nunique()}")
    else:
        logger.warning("No data was scraped!")


if __name__ == "__main__":
    main()
