from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import Any, Protocol


class Options(Protocol):
    def add_argument(self, argument: str) -> None:
        ...


class WebDriver(Protocol):
    def __init__(
        self,
        options: Any = None,
        service: Any = None,
        keep_alive: bool = True,
    ):
        ...

    def get(self, url: str) -> None:
        ...

    def find_element(self, by: str, value: str) -> Any:
        ...

    def quit(self) -> None:
        ...


@dataclass
class Driver:
    web_driver: type[WebDriver]
    options: type[Options]

    def __init__(self, web_driver: type[WebDriver], options: type[Options]):
        self.web_driver = web_driver
        self.options = options

    def __enter__(self) -> WebDriver:
        options = self.options()
        options.add_argument("--headless")
        self.driver = self.web_driver(options=options)

        return self.driver

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        self.driver.quit()
