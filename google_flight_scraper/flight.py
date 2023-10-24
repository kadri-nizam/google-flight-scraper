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


@dataclass
class GoogleFlightQuery:
    origin: str
    destination: str
    departure_date: str
    return_date: str = ""
    num_adults: int = 1
    num_children: int = 0
    num_infants: int = 0
    cabin: str = Cabin.ECONOMY
    airline: str = Airlines.ANY

    def __post_init__(self):
        self._check_inputs()

    def to_string(self) -> str:
        return " ".join(
            [
                f"Flights from {self.origin}",
                f"to {self.destination}",
                f"on {self.departure_date}",
                f"returning {self.return_date}" if self.return_date else "one-way",
                f"for {self.num_adults} adults",
                f"for {self.num_children} children",
                f"for {self.num_infants} infants",
                f"on {self.cabin} class",
                f"with {self.airline} airline",
            ]
        )

    @property
    def url(self) -> str:
        url_base = "https://www.google.com/travel/flights"
        return f"{url_base}?hl=en&q={self.to_string()}"

    def _check_inputs(self):
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
