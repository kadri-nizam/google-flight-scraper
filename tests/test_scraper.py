import datetime as dt
from datetime import datetime
from unittest.mock import Mock

import pytest
from selenium import webdriver

from google_flight_scraper.driver import Driver
from google_flight_scraper.query import FlightQuery, TravelPlan
from google_flight_scraper.scraper import Scraper


@pytest.fixture
def mock_driver_one_way_12h(mocker):
    mocked_driver = Mock()
    mocked_web_element = Mock()

    mocked_web_element.configure_mock(
        **{
            "text": (
                "1:00 PM – 11:15 AM+2\nEVA Air\n31 hr 15 min\nSFO–KUL\n"
                "1 stop\n13 hr TPE\n1,208 kg CO2\n+26% emissions\n$1,096"
            )
        }
    )

    mocked_driver.configure_mock(
        **{
            "find_elements.return_value": 20 * [mocked_web_element],
        }
    )

    mocker.patch(
        "google_flight_scraper.driver.Driver.__enter__",
        return_value=mocked_driver,
    )
    mocker.patch(
        "google_flight_scraper.driver.Driver.__exit__",
        return_value=None,
    )


@pytest.fixture
def mock_driver_return_trip_24h(mocker):
    mocked_driver = Mock()
    mocked_web_element = Mock()

    mocked_web_element.configure_mock(
        **{
            "text": (
                "17:45 – 22:20+1\nCathay PacificMalaysia Airlines\n19 hrs 35 min\n"
                "PIT–AUS\n1 stop\n2 hrs 55 min HKG\n789 kg CO2\n-16% emissions\n"
                "US$969\nround trip"
            )
        }
    )

    mocked_driver.configure_mock(
        **{
            "find_elements.return_value": 20 * [mocked_web_element],
        }
    )

    mocker.patch(
        "google_flight_scraper.driver.Driver.__enter__",
        return_value=mocked_driver,
    )
    mocker.patch(
        "google_flight_scraper.driver.Driver.__exit__",
        return_value=None,
    )


def test_scrape_one_way(mock_driver_one_way_12h):
    queries = FlightQuery.from_travel_plans(
        TravelPlan(
            "SFO",
            "KUL",
            departure_dates=["2023-12-25"],
        ),
    )

    with Driver(webdriver.Firefox, webdriver.FirefoxOptions) as driver:
        df = Scraper()(driver, queries)

    assert len(df) == 20
    assert df["Price"].unique() == 1096.0
    assert df["Departs"].unique() == datetime(2023, 12, 25, 13, 0)
    assert df["Arrives"].unique() == datetime(2023, 12, 27, 11, 15)
    assert df["Origin"].unique() == "SFO"
    assert df["Destination"].unique() == "KUL"
    assert df["Duration"].unique() == dt.timedelta(hours=31, minutes=15)


def test_scrape_return_trip(mock_driver_return_trip_24h):
    queries = FlightQuery.from_travel_plans(
        TravelPlan(
            "PIT",
            "AUS",
            departure_dates=["2023-12-25"],
            return_dates=["2023-12-28"],
        ),
    )

    with Driver(webdriver.Firefox, webdriver.FirefoxOptions) as driver:
        df = Scraper()(driver, queries)

    assert len(df) == 20
    assert df["Price"].unique() == 969.0
    assert df["Departs"].unique() == datetime(2023, 12, 25, 17, 45)
    assert df["Arrives"].unique() == datetime(2023, 12, 26, 22, 20)
    assert df["Origin"].unique() == "PIT"
    assert df["Destination"].unique() == "AUS"
    assert df["Duration"].unique() == dt.timedelta(hours=19, minutes=35)
