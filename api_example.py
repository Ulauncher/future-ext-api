from typing import Callable
from dataclasses import dataclass


class Extension:
    preferences: dict[str, str]

    def __init__(self) -> None:
        self.preferences = {}

    def set_query_modifiers(
        self, modifiers: dict[str, str], default_key: str | None = None
    ) -> None:
        raise NotImplementedError()

    def run(self) -> None:
        raise NotImplementedError()

    def on_input(self, input_text: str, trigger_id: str):
        raise NotImplementedError()


@dataclass
class RowResult:
    name: str
    on_enter: "OnUserActionType" = None
    icon: str | None = None
    description: str | None = None
    compact: bool = False
    keep_app_open: bool = False


@dataclass
class ImageResult:
    image: str
    name: str
    description: str | None = None
    on_enter: "OnUserActionType" = None


@dataclass
class RowResultContainer:
    items: list[RowResult]
    show_header: bool = False
    header_title: str = ""


@dataclass
class ImageResultContainer:
    items: list["ImageResult"]
    show_header: bool = False
    header_title: str = ""


@dataclass
class NavItem:
    name: str | None = None
    enabled: bool = True


@dataclass
class Navigation:
    "None means Ulauncher will decide what to show"

    back: NavItem | None
    forward: NavItem | None
    enter: NavItem | None
    alt_enter: NavItem | None


@dataclass
class Results:
    items: list[RowResult | RowResultContainer | ImageResultContainer] | None = None
    navigation: Navigation | None = None


OnUserActionType = Callable[[], list[RowResult] | Results | None] | None
