# ODESI Browse Scraper

A Python script to scrape survey series and surveys from the ODESI browse API and export them to Excel for analysis.

## Features

- Scrapes all main categories from ODESI browse API
- Extracts series names, survey titles, years, and URIs
- Exports data to Excel with multiple sheets:
  - **All_Data**: Complete dataset with all surveys
  - **Category_Summary**: Summary statistics by category
  - **Series_Summary**: Summary by series with year ranges
  - **Potential_Duplicates**: Identifies potential duplicate surveys (useful for finding typos)

## Installation

1. Install dependencies:

```bash
pip install -e .
```

Or install manually:

```bash
pip install requests pandas openpyxl
```

## Usage

### Run the scraper:

```bash
python src/odesi_scraper.py
```

This will:
1. Scrape all 25 main categories from ODESI
2. Extract all series and surveys
3. Create an Excel file named `odesi_surveys.xlsx` in the current directory

### Use as a module:

```python
from src.odesi_scraper import ODESIScraper

# Initialize scraper with 1 second delay between requests
scraper = ODESIScraper(delay=1.0)

# Scrape all categories
df = scraper.scrape_all_categories()

# Export to Excel
scraper.export_to_excel(df, "my_output.xlsx")

# Or scrape specific categories only
categories = ["Agriculture", "Health", "Education and Training"]
df = scraper.scrape_all_categories(categories=categories)
```

## Output Format

The Excel file contains the following columns:

- **Category**: Main topic category (e.g., "Agriculture")
- **Series_Name**: Survey series or collection name
- **Year**: Year of the survey
- **Survey_Title**: Full title of the survey
- **URI**: Persistent identifier/URI for the survey

## Finding Duplicates

The script automatically identifies potential duplicates in the "Potential_Duplicates" sheet by:
- Normalizing survey titles (lowercase, trimmed)
- Finding surveys with similar titles in the same series and year
- This helps identify typos and inconsistencies

## Categories Scraped

The script scrapes the following 19 categories:

- Agriculture
- Business and Financial
- Census of Population
- Communications and Information
- Consumer Surveys
- COVID-19
- Crime and Justice
- Demographics and Population
- Education
- Elections and Politics
- Geography
- Government Finances and Economic Indicators
- Health
- Labour and Employment
- Natural Resources and Environment
- Public Opinion Polls
- Social Surveys
- Trade
- Travel

## Customization

You can modify the `CATEGORIES` list in the script to add or remove categories as needed.

## License

MIT
# odesi_scrapper
