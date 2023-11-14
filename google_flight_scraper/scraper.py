from __future__ import annotations

import datetime
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime as dt
from typing import Any

import pandas as pd
from price_parser.parser import parse_price
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from google_flight_scraper.driver import WebDriver
from google_flight_scraper.flight import FlightDetail
from google_flight_scraper.query import FlightQuery


@dataclass
class Scraper:
    timeout_seconds: int = field(default=10)
    more_flights_btn_xpath: str = field(
        init=False, default=r"//ul/li/div/span/div/button"
    )
    flight_info_xpath: str = field(init=False, default=r"//c-wiz/div/div/div/ul/li")

    def _expand_more_flights(self, driver: WebDriver) -> None:
        try:
            driver.find_element(By.XPATH, self.more_flights_btn_xpath).click()
            WebDriverWait(driver, self.timeout_seconds).until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, self.flight_info_xpath)
                )
            )
        except TimeoutException:
            pass
        except NoSuchElementException:
            pass

    def _parse(
        self, raw_flight_details: list[str], departure_date: str
    ) -> list[list[str]]:
        INDEX_OF_LAYOVER_DETAIL = 5

        cleaned = []
        for flight_text in raw_flight_details:
            nonstop = "Nonstop" in flight_text
            split_text = flight_text.split("\n")

            if nonstop:
                split_text.insert(INDEX_OF_LAYOVER_DETAIL, "")

            cleaned.append(Scraper.clean_flight_text(departure_date, *split_text))

        return cleaned

    def _get_all_flight_elements(self, driver: WebDriver) -> list[str]:
        INDEX_OF_FLIGHT_PRICE = -2

        # Get all text elements to avoid stale requests
        list_elements = driver.find_elements(By.XPATH, self.flight_info_xpath)
        texts = [element.text for element in list_elements]

        raw_flight_details = []
        for text in texts:
            # One-way flights don't have "one-way" in the text on Google Flights
            # so we'll add it back in here
            if not "round trip" in text and not "entire trip" in text:
                text += "\nOne-Way"

            # We're only interested in list elements that have a price
            currency = parse_price(text.split("\n")[INDEX_OF_FLIGHT_PRICE]).currency

            if currency:
                raw_flight_details.append(text)

        return raw_flight_details

    def _get_flights(self, driver: WebDriver, query: FlightDetail) -> list[list[str]]:
        driver.get(query.url)

        WebDriverWait(driver, self.timeout_seconds).until(
            EC.visibility_of_all_elements_located((By.XPATH, self.flight_info_xpath))
        )

        self._expand_more_flights(driver)
        return self._parse(
            self._get_all_flight_elements(driver),
            query.departure_date,
        )

    def __call__(self, driver: WebDriver, queries: FlightQuery) -> pd.DataFrame:
        flights: list[list[list[str]]] = []
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

        df["Price"] = df["Price"].str.replace(",", "")
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
        *leftover,
    ) -> list[str]:
        # Discard emission info if present
        *_, price, trip_type = leftover

        depart, *_ = unicodedata.normalize("NFKD", depart_and_arrive_time).split(" – ")

        if not "hr" in duration:
            duration = f"0 hr {duration.strip()}"
        elif not "min" in duration:
            duration = f"{duration.strip()} 0 min"

        hr, min = [int(x) for x in duration.split(" ") if x.isdigit()]
        delta = datetime.timedelta(hours=hr, minutes=min)

        depart_datetime = dt.strptime(
            f"{departure_date} {depart}".strip(), "%Y-%m-%d %I:%M %p"
        )
        arrive_datetime = depart_datetime + delta

        airline = airline.strip()

        # – in origin_and_destination is the U+2013 unicode character
        # which is different from the ASCII hyphen-minus character
        origin, destination = (
            origin_and_destination.encode("ascii", "replace").decode().split("?")
        )

        # First character of num_stops is the number of stops
        num_stops = "0" if "Nonstop" in num_stops else num_stops[0]

        layover_detail = layover_detail.strip()
        price = parse_price(price).amount_text or ""
        trip_type = trip_type.strip().title()

        return [
            depart_datetime.strftime("%Y-%m-%d %H:%M"),
            arrive_datetime.strftime("%Y-%m-%d %H:%M"),
            origin,
            destination,
            price,
            airline,
            num_stops,
            layover_detail,
            trip_type,
        ]


_DATAFRAME_COLUMNS: dict[str, Any] = {
    "Departs": "datetime64[ns]",
    "Arrives": "datetime64[ns]",
    "Origin": "category",
    "Destination": "category",
    "Price": float,
    "Airline": "category",
    "Num_Stops": int,
    "Layover_Detail": str,
    "Trip_Type": "category",
}
