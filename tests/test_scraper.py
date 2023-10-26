from unittest.mock import Mock

import pytest
from selenium import webdriver

from google_flight_scraper.driver import Driver
from google_flight_scraper.query import FlightQuery, TravelPlan
from google_flight_scraper.scraper import Scraper


@pytest.fixture
def mock_driver_one_way(mocker):
    mocked_driver = Mock()
    mocked_web_element = Mock()

    mocked_web_element.configure_mock(
        **{
            "text": (
                "12:10 PM – 1:15 PM\nDelta\n"
                "2 hr 21 min\nSFO–SEA\nNonstop\n122 kg CO2\n"
                "+20% emissions\n$74"
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
def mock_driver_return_trip(mocker):
    mocked_driver = Mock()
    mocked_web_element = Mock()

    mocked_web_element.configure_mock(
        **{
            "text": (
                "12:10 PM – 1:15 PM\nDelta\n"
                "2 hr 21 min\nSFO–SEA\nNonstop\n122 kg CO2\n"
                "+20% emissions\n$74\nround trip"
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


def test_scrape_one_way(mock_driver_one_way):
    queries = FlightQuery.from_travel_plans(
        TravelPlan(
            "LAX",
            "SFO",
            departure_dates=["2023-12-25"],
        ),
    )

    with Driver(webdriver.Firefox, webdriver.FirefoxOptions) as driver:
        df = Scraper()(driver, queries)

    assert len(df) == 20
    assert df["Price"].unique() == [74.0]


def test_scrape_return_trip(mock_driver_return_trip):
    queries = FlightQuery.from_travel_plans(
        TravelPlan(
            "LAX",
            "SFO",
            departure_dates=["2023-12-25"],
            return_dates=["2023-12-28"],
        ),
    )

    with Driver(webdriver.Firefox, webdriver.FirefoxOptions) as driver:
        df = Scraper()(driver, queries)

    assert len(df) == 20
    assert df["Price"].unique() == [74.0]
