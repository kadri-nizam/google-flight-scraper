from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime as dt
from enum import auto

from strenum import LowercaseStrEnum


class Cabin(LowercaseStrEnum):
    ECONOMY = auto()
    BUSINESS = auto()
    FIRST = auto()


class Airlines(LowercaseStrEnum):
    ANY = auto()
    ALASKA = auto()
    AMERICAN = auto()
    CHINA_EASTERN = auto()
    DELTA = auto()
    EMIRATES = auto()
    FIJI_AIRWAYS = auto()
    FRONTIER = auto()
    HAWAIIAN = auto()
    JETBLUE = auto()
    QATAR_AIRWAYS = auto()
    SOUTHWEST = auto()
    SPIRIT = auto()
    SUN_COUNTRY = auto()
    UNITED = auto()
    WESTJET = auto()


_DATE_FORMAT = r"%Y-%m-%d"


@dataclass(frozen=True)
class FlightDetail:
    origin: str
    destination: str
    departure_date: str
    return_date: str = ""
    num_adults: int = 1
    num_children: int = 0
    num_infants: int = 0
    cabin: str = Cabin.ECONOMY
    airline: str = Airlines.ANY

    def __post_init__(self) -> None:
        self._check_inputs()

    def __repr__(self) -> str:
        return (
            "FlightDetail(\n"
            f"  {self.origin} -> {self.destination}\n"
            f"  departs: {self.departure_date}"
            f"  returns: {self.return_date or 'One-Way Flight'}\n"
            f"  Adults: {self.num_adults}, Children: {self.num_children}, Infants: {self.num_infants}\n"
            f"  Cabin: {self.cabin}, Airline: {self.airline}\n"
            ")"
        )

    def make_query(self) -> str:
        query = [
            f"Flights from {self.origin}",
            f"to {self.destination}",
            f"on {self.departure_date}",
            f"returning {self.return_date}" if self.return_date else "one-way",
        ]

        if self.num_adults:
            query.append(f"{self.num_adults} adults")

        if self.num_children:
            query.append(f"{self.num_children} children")

        if self.num_infants:
            query.append(f"and {self.num_infants} infants")

        query.append(f"{self.cabin} class")

        if self.airline != Airlines.ANY:
            query.append(f"{self.airline} airline")

        return " ".join(query)

    @property
    def url(self) -> str:
        url_base = "https://www.google.com/travel/flights"
        return f"{url_base}?hl=en&q={self.make_query()}"

    def _check_inputs(self) -> None:
        if len(self.origin) != 3 or len(self.destination) != 3:
            raise ValueError("Both origin and destination must be IATA airport codes.")

        try:
            departure_date = dt.strptime(self.departure_date, _DATE_FORMAT).date()
        except ValueError:
            raise ValueError("Invalid departure date format.")

        if departure_date < dt.now().date():
            raise ValueError("Departure date is in the past.")

        if self.return_date:
            try:
                return_date = dt.strptime(self.return_date, _DATE_FORMAT).date()
            except ValueError:
                raise ValueError("Invalid return date format.")

            if return_date < departure_date:
                raise ValueError("Return date is before departure date.")

        if self.num_adults + self.num_children + self.num_infants <= 0:
            raise ValueError("At least one passenger is required.")

        if self.num_adults < 0 and self.num_infants > 0:
            raise ValueError("At least one adult is required for lap-seated infants.")
