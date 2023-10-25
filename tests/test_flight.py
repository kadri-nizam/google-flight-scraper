import datetime

import pytest

from google_flight_scraper.flight import FlightDetail

_TODAY_DATE = datetime.datetime.now().strftime("%Y-%m-%d")


def test_invalid_departure_date_format():
    with pytest.raises(ValueError, match="Invalid departure date format."):
        FlightDetail(
            origin="SFO",
            destination="LAX",
            departure_date="2023-15-40",
            num_adults=3,
            num_children=1,
        )


def test_invalid_return_date_format():
    with pytest.raises(ValueError, match="Invalid return date format."):
        FlightDetail(
            origin="SFO",
            destination="LAX",
            departure_date=_TODAY_DATE,
            return_date="12/12/2023",
            num_adults=3,
            num_children=1,
        )


def test_departure_date_in_the_past():
    with pytest.raises(ValueError, match="Departure date is in the past."):
        FlightDetail(
            origin="SFO",
            destination="LAX",
            departure_date="2020-10-02",
            num_adults=3,
            num_children=1,
        )


def test_return_date_in_the_past():
    with pytest.raises(ValueError, match="Return date is before departure date."):
        FlightDetail(
            origin="SFO",
            destination="LAX",
            departure_date=_TODAY_DATE,
            return_date="2023-09-02",
            num_adults=3,
            num_children=1,
        )


def test_invalid_airport_code():
    with pytest.raises(
        ValueError, match="Both origin and destination must be IATA airport codes."
    ):
        FlightDetail(
            origin="NONE",
            destination="LAX",
            departure_date=_TODAY_DATE,
            num_adults=3,
            num_children=1,
        )
