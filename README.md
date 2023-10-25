# google-flight-scraper
A library to scrape and analyze Google Flight data

# Using the library

## Quickstart
You'll want to first define your travel plans:
```python
from google_flight_scraper.query import TravelPlan, FlightQuery

seattle_vacation = TravelPlan(
    origin="SFO",
    destination="SEA",
    departure_dates=[
        f"2023-10-{day}" for day in range(2, 12)
    ],
    num_adults=2,
    num_children=1
)

queries = FlightQuery.from_travel_plans(seattle_vacation)
```
This will set up the library to search for all one-way flights from San Francisco to Seattle/Tacoma between October 2, 2023 and October 12, 2023. Pass your travel plans into `FlightQuery` for it to construct all the pertinent queries. Any number of travel plans can be provided.

Lastly, we define the webdriver we'd like to use and start scraping. A `Driver` class is provided for easily switching between different browsers and their associated webdrivers.
```python
from selenium import webdriver
from google_flight_scraper.driver import Driver
from google_flight_scraper.scraper import Scraper

with Driver(webdriver.Firefox, webdriver.FirefoxOptions) as driver:
    df = Scraper(timeout_seconds=5)(driver, queries)
```
Scraped data will be in the `df` DataFrame for further analysis.
