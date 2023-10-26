# google-flight-scraper
A library to scrape and analyze Google Flight data

# Installing
Clone the repository into your local drive. This project was developed with [Poetry](https://python-poetry.org/) as the dependency manager. Simply run `poetry install` in the cloned directory to install the required dependencies.

# Using the library

## Quickstart
First define our travel plans:
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
This will set up the library to search for all one-way flights from San Francisco to Seattle/Tacoma between October 2, 2023 and October 12, 2023. Pass the travel plans into `FlightQuery` for it to construct all the pertinent queries. Any number of travel plans can be provided.

Lastly, we define the webdriver we'd like to use to scrape. A `Driver` class is provided for easily switching between different browsers and their associated webdrivers.
```python
from selenium import webdriver
from google_flight_scraper.driver import Driver
from google_flight_scraper.scraper import Scraper

with Driver(webdriver.Firefox, webdriver.FirefoxOptions) as driver:
    df = Scraper(timeout_seconds=5)(driver, queries)
```
Scraped data will be in the `df` DataFrame for further analysis.

## One-way vs return trip behaviour
There is a difference in the way that the library queries return trips and returning one-way flights (return trip, two one-way tickets). The reason for doing this is that the latter may have cheaper flight combinations. We can set up both searches by providing multiple `TravelPlan` to `FlightQuery`:
```python
# ...
FlightQuery.from_travel_plans(
    # Searches for return trip tickets on Google Flights
    TravelPlan(
        "SFO",
        "SEA",
        departure_dates=[f"2023-12-{d}" for d in range(1, 10)],
        return_dates=[f"2023-12-{d}" for d in range(11, 20)],
    ),
    # Searches to-and-fro one-way tickets on Google Flights
    TravelPlan(
        "SFO",
        "SEA",
        departure_dates=[f"2023-12-{d}" for d in range(1, 10)],
    ),
    TravelPlan(
        "SEA",
        "SFO",
        departure_dates=[f"2023-12-{d}" for d in range(11, 20)],
    ),
)
```
