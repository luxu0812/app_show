## Overview
This project is a Dash-based interactive dashboard that provides insights into the mobile app advertising landscape. It brings together data from multiple sources—top apps, deliveries, placements, publisher URLs, advertiser URLs, and their relationships—and visualizes them using various plots and charts, including choropleths, histograms, and a Sankey diagram. The dashboard helps users understand what's happening in the app market, how ads are delivered, and the relationships between different advertiser and publisher apps.

## Features
- **Top-Free and Top-Paid Apps:**
  Displays a world map highlighting the countries where top apps appear, as well as a histogram showing the top 20 apps by the number of territories they occupy.

- **Ad Deliveries and Placements Over Time:**
  Uses animated maps (updated every 2 seconds) to show how ad deliveries and placements change hour by hour globally.

- **Publisher and Advertiser URLs:**
  Shows which regions each publisher or advertiser URL is present in, helping to understand their global footprint.

- **Sankey Diagram for Flows:**
  Visualizes the directional flow from advertisers to publishers, illustrating which advertisers deliver ads to which publishers and the relative magnitude of those relationships.

## Data Sources
- **SQLite Database (DB_PATH):**
  Used to fetch top-free and top-paid app data.

- **CSV Files:**

  - `delivery_data.csv`: Contains ad delivery data by region and hour.
  - `placement_data.csv`: Contains placement counts by region and hour.
  - `publisher_data.csv`: Contains PublisherURL counts by region.
  - `advertiser_data.csv`: Contains AdvertiserURL counts by region.
  - `flow_data.csv`: Contains the flow from AdvertizerURL to PublisherURL (Advertiser-Publisher relationships and counts).

All CSV file paths are defined at the top of the code and should be replaced or updated as needed.

## Visualization Tools and Libraries
- **Dash & Dash Bootstrap Components:**
  Used to build the interactive web dashboard and layout.

- **Plotly Express & Graph Objects:**
  Used for creating choropleth maps, histograms, and the Sankey diagram.

- **CountryCodeConverter & pycountry:**
  Used for converting country codes and mapping them to ISO alpha-3 formats required by the choropleths.

- **DatabaseManager & SQLite:**
  Handles data retrieval from the local SQLite database.

## How to Run
1. **Install Dependencies:**
  ```bash
  pip install dash dash-bootstrap-components plotly pycountry pandas sqlite3 google-play-scraper
  ```
  Also ensure country_code_converter.py and database_manager.py are available and correctly implemented.

2. **Set Up Your Data:**
  - Update the paths for all CSV files at the top of the code.
  - Ensure hackathon.db is in place and accessible.
  - Confirm that the CSV files contain the necessary columns and formats.

3. **Run the App:**
  ```bash
  python your_script_name.py
  ```
  The app will start a local server. Open your web browser and navigate to http://127.0.0.1:8050 to view the dashboard.

## Interactions
- Automatic Updates:
  Some views update every 2 seconds, cycling through apps or time periods automatically.

- Hover & Click:
  Hover over maps, histograms, or the Sankey diagram to see detailed tooltips.

- Responsive Layout:
  The dashboard uses a fluid container and bootstrap styles, making it reasonably responsive.

## Notes
- This dashboard is designed as a proof-of-concept for internal analysis, providing a snapshot of how ads are delivered, where top apps are located, and how advertiser-publisher relationships flow.
- Ensure that the data in CSV files and the SQLite database is accurate and up-to-date for meaningful insights.
- Depending on your environment, you may need additional adjustments or installations.
