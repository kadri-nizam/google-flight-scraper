from google_flight_scraper.query import FlightQuery, TravelPlan


def test_multiple_departure_and_return_dates():
    queries = FlightQuery.from_travel_plans(
        TravelPlan(
            "LAX",
            "SFO",
            departure_dates=["2023-12-25", "2023-12-26", "2023-12-27"],
            return_dates=["2023-12-30", "2023-12-31"],
        ),
    )

    assert len(queries) == 6


def test_multiple_travel_plans():
    queries = FlightQuery.from_travel_plans(
        TravelPlan(
            "LAX", "SFO", ["2023-12-25", "2023-12-26", "2023-12-27", "2023-12-28"]
        ),
        TravelPlan(
            "SFO", "ORD", ["2023-12-30", "2023-12-31"], ["2024-01-01", "2024-01-02"]
        ),
    )

    assert len(queries) == 8
