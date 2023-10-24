from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from functools import partial
from typing import Generator

from google_flight_scraper.flight import Airlines, Cabin, FlightDetail


@dataclass
class TravelPlan:
    origin: str
    destination: str
    departure_dates: list[str]
    return_dates: list[str] = field(default_factory=lambda: [""])


@dataclass
class FlightQuery:
    flight_details: list[FlightDetail] = field(default_factory=list)

    @classmethod
    def from_travel_plans(
        cls,
        *travel_plans: TravelPlan,
        num_adults=1,
        num_children=0,
        num_infants=0,
        cabin=Cabin.ECONOMY,
        airline=Airlines.ANY,
    ):
        queries = cls()
        for travel_plan in travel_plans:
            flight_detail = partial(
                FlightDetail,
                origin=travel_plan.origin,
                destination=travel_plan.destination,
                num_adults=num_adults,
                num_children=num_children,
                num_infants=num_infants,
                cabin=cabin,
                airline=airline,
            )

            date_combination = itertools.product(
                travel_plan.departure_dates, travel_plan.return_dates
            )

            for d, r in date_combination:
                queries.flight_details.append(
                    flight_detail(departure_date=d, return_date=r)
                )

        return queries

    def __len__(self) -> int:
        return len(self.flight_details)

    def __getitem__(self, index: int) -> FlightDetail:
        return self.flight_details[index]

    def __iter__(self) -> Generator[FlightDetail, None, None]:
        yield from self.flight_details

    def __repr__(self) -> str:
        return f"FlightQuery(num_queries={len(self)})"
