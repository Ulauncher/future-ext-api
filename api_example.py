from typing import Callable
from dataclasses import dataclass, field


# Instead of using dataclass it could also
# subclass BaseDataClass from ulauncher.utils.
# These classes should not include any logic except validation.
@dataclass
class RowResult:
    name: str
    on_enter: "OnUserActionType" = None
    on_alt_enter: "OnUserActionType" = None
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
    on_alt_enter: "OnUserActionType" = None


@dataclass
class DetailResult:
    markdown: str  # Markdown support with a limited set of features
    show_header: bool = False
    header_title: str = ""
    on_enter: "OnUserActionType" = None
    on_alt_enter: "OnUserActionType" = None
    keep_app_open: bool = False


@dataclass
class RowResultContainer:
    items: list[RowResult] = field(default_factory=list)
    show_header: bool = False
    header_title: str = ""


@dataclass
class ImageResultContainer:
    items: list["ImageResult"] = field(default_factory=list)
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
    items: list[RowResult | RowResultContainer | ImageResultContainer | DetailResult] = (
        field(default_factory=list)
    )
    navigation: Navigation | None = None


class Action:
    """
    Base class for actions that can be performed on a result.
    All subclasses must implement the `to_dict` method.
    """

    def to_dict(self) -> dict:
        raise NotImplementedError()


class OpenUrlAction(Action):
    def __init__(self, url: str) -> None:
        self.url = url

    def to_dict(self) -> dict:
        raise NotImplementedError()


OnUserActionType = Callable[[], list[RowResult] | Results | Action | None] | None


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

    def on_input(
        self, input_text: str, trigger_id: str
    ) -> list[RowResult] | Results | Action | None:
        """
        list[RowResult] in the return type is for backward compatibility and convenience
        when needed to return a simple list of results.
        """
        raise NotImplementedError()
