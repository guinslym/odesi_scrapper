"""
Example usage of the ODESI scraper
"""

import sys
sys.path.insert(0, 'src')

from odesi_scraper import ODESIScraper

# Example 1: Scrape all categories (full run)
print("Example 1: Full scrape of all categories")
print("-" * 50)
scraper = ODESIScraper(delay=1.0)
df_all = scraper.scrape_all_categories()
scraper.export_to_excel(df_all, "odesi_surveys_full.xlsx")
print(f"Scraped {len(df_all)} total records")
print()

# Example 2: Scrape specific categories only
print("Example 2: Scrape specific categories")
print("-" * 50)
scraper = ODESIScraper(delay=0.5)
selected_categories = ["Agriculture", "Health", "Education and Training"]
df_selected = scraper.scrape_all_categories(categories=selected_categories)
scraper.export_to_excel(df_selected, "odesi_surveys_selected.xlsx")
print(f"Scraped {len(df_selected)} records from {len(selected_categories)} categories")
print()

# Example 3: Analyze the data
print("Example 3: Data analysis")
print("-" * 50)
print(f"Total surveys: {len(df_all)}")
print(f"Total categories: {df_all['Category'].nunique()}")
print(f"Total unique series: {df_all['Series_Name'].nunique()}")
print(f"\nTop 10 series by survey count:")
print(df_all['Series_Name'].value_counts().head(10))
print()

# Example 4: Find duplicates
print("Example 4: Finding potential duplicates")
print("-" * 50)
duplicates = scraper.find_duplicates(df_all)
print(f"Found {len(duplicates)} potential duplicate records")
if len(duplicates) > 0:
    print("\nSample duplicates:")
    print(duplicates[['Series_Name', 'Year', 'Survey_Title']].head())
