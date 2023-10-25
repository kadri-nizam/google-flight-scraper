import datetime
from dataclasses import dataclass, field
from datetime import datetime as dt
from re import split

import pandas as pd
from price_parser.parser import parse_price
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from google_flight_scraper.driver import WebDriver
from google_flight_scraper.flight import FlightDetail
from google_flight_scraper.query import FlightQuery


@dataclass
class Scraper:
    timeout_seconds: int = field(default=10)
    more_flights_btn_class: str = field(init=False, default=r"bEfgkb")

    def _expand_more_flights(self, driver):
        try:
            driver.find_element(By.CLASS_NAME, self.more_flights_btn_class).click()
        except NoSuchElementException:
            # No more flights to expand so just pass
            pass

    def _parse(self, raw_flight_details: list[str], departure_date: str) -> list[str]:
        TOTAL_ELEMENT_IF_FULL_DETAIL = 10
        INDEX_OF_LAYOVER_DETAIL = 5

        cleaned = []
        for flight_text in raw_flight_details:
            nonstop = "Nonstop" in flight_text
            split_text = flight_text.split(r"\n")

            if nonstop:
                split_text.insert(INDEX_OF_LAYOVER_DETAIL, "")

            if len(split_text) < TOTAL_ELEMENT_IF_FULL_DETAIL:
                raise AttributeError(f"Flight details are incomplete:\n{split_text}")

            cleaned.append(Scraper.clean_flight_text(departure_date, *split_text))

        return cleaned

    def _get_all_flight_elements(self, driver: WebDriver) -> list[str]:
        INDEX_OF_FLIGHT_PRICE = -2

        list_elements = driver.find_elements(By.TAG_NAME, "li")

        raw_flight_details = []
        for element in list_elements:
            text = element.text

            if not text or "Hide" in text:
                continue

            # One-way flights don't have "one-way" in the text on Google Flights
            # so we'll add it back in here
            if not "round trip" in text and not "entire trip" in text:
                text += r"\nOne-Way"

            # We're only interested in list elements that have a price
            currency = parse_price(text.split(r"\n")[INDEX_OF_FLIGHT_PRICE]).currency

            if currency:
                raw_flight_details.append(text)

            print(raw_flight_details)

        return raw_flight_details

    def _get_flights(self, driver: WebDriver, query: FlightDetail) -> list[str]:
        driver.get(query.url)

        MIN_FLIGHTS_SHOWN = 5
        WebDriverWait(driver, self.timeout_seconds).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "li")) > MIN_FLIGHTS_SHOWN
        )

        self._expand_more_flights(driver)
        return self._parse(
            self._get_all_flight_elements(driver),
            query.departure_date,
        )

    def __call__(self, driver: WebDriver, queries: FlightQuery) -> pd.DataFrame:
        flights = []
        for query in tqdm(queries):
            try:
                flights.append(self._get_flights(driver, query))
            except TimeoutException:
                print(
                    f"Timeout for query:\n\n{query}\n\n"
                    "It is possible that no flights are available. "
                    "Skipping..."
                )
                continue

        # flatten the list of lists to render into a dataframe
        df = pd.DataFrame(
            [flight for dates in flights for flight in dates],
            columns=list(_DATAFRAME_COLUMNS.keys()),
        )

        for columns in df.columns:
            df[columns] = df[columns].astype(_DATAFRAME_COLUMNS[columns])

        df["Duration"] = df["Arrives"] - df["Departs"]

        return df

    @staticmethod
    def clean_flight_text(
        departure_date: str,
        depart_and_arrive_time: str,
        airline: str,
        duration: str,
        origin_and_destination: str,
        num_stops: str,
        layover_detail: str,
        amount_emission: str,
        relative_emission: str,
        price: str,
        trip_type: str,
    ) -> list[str]:
        depart, _ = depart_and_arrive_time.encode("ascii", "ignore").decode().split()
        split_duration = [int(x) for x in duration.split() if x.isdigit()]

        if len(split_duration) == 2:
            hr, min = split_duration
            delta = datetime.timedelta(hours=hr, minutes=min)
        elif "hr" in duration:
            (hr,) = split_duration
            delta = datetime.timedelta(hours=hr)
        elif "min" in duration:
            (min,) = split_duration
            delta = datetime.timedelta(minutes=min)
        else:
            raise ValueError(f"Unrecognized duration: {duration}")

        depart = dt.strptime(f"{departure_date} {depart}".strip(), "%Y-%m-%d %I:%M%p")
        arrive = depart + delta

        airline = airline.strip()

        # – in origin_and_destination is the U+2013 unicode character
        # which is different from the ASCII hyphen-minus character
        origin, destination = (
            origin_and_destination.encode("ascii", "replace").decode().split("?")
        )

        # First character of num_stops is the number of stops
        num_stops = "0" if "Nonstop" in num_stops else num_stops[0]

        layover_detail = layover_detail.strip()
        amount_emission = amount_emission.strip()
        relative_emission = relative_emission.strip().title()
        price = parse_price(price).amount_text or ""
        trip_type = trip_type.strip().title()

        return [
            depart.strftime("%Y-%m-%d %H:%M"),
            arrive.strftime("%Y-%m-%d %H:%M"),
            origin,
            destination,
            price,
            airline,
            num_stops,
            layover_detail,
            amount_emission,
            relative_emission,
            trip_type,
        ]


_DATAFRAME_COLUMNS = {
    "Departs": "datetime64[ns]",
    "Arrives": "datetime64[ns]",
    "Origin": "category",
    "Destination": "category",
    "Price": float,
    "Airline": "category",
    "Num_Stops": int,
    "Layover_Detail": str,
    "Amount_Emission": str,
    "Relative_Emission": str,
    "Trip_Type": "category",
}
