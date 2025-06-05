from dataclasses import dataclass, field


# Instead of using dataclass it could also
# subclass BaseDataClass from ulauncher.utils.
# These classes should not include any logic except validation.
@dataclass
class Action:
    """
    Base class for actions that can be performed on a result.
    """

    type: str = "default"
    label: str = "Open"  # Default label for the action rendered in the UI


class OpenUrlAction(Action):
    type = "open_url"
    label = "Open In Browser"
    url: str
    keep_app_open: bool = False

    def __init__(self, url: str, keep_app_open: bool = False) -> None:
        super().__init__()
        self.url = url
        self.keep_app_open = keep_app_open


@dataclass
class Result:
    name: str
    # First Action in the list is the default action, activated by Enter key.
    # If empty, no action will be performed on Enter key.
    # For compatibility with current ExtensionResultItem
    # we can on_alt_enter as a second action with label "More Actions"
    actions: list[Action | object] = field(default_factory=list)
    icon: str | None = None
    description: str | None = None
    compact: bool = False


@dataclass
class ImageResult:
    image: str
    name: str
    description: str | None = None
    actions: list[Action | object] = field(default_factory=list)


@dataclass
class DetailResult:
    markdown: str  # Markdown support with a limited set of features
    actions: list[Action | object] = field(default_factory=list)


@dataclass
class RowResultContainer:
    items: list[Result] = field(default_factory=list)
    show_header: bool = False
    header_title: str = ""


@dataclass
class ImageResultContainer:
    items: list["ImageResult"] = field(default_factory=list)
    show_header: bool = False
    header_title: str = ""


@dataclass
class Results:
    items: list[Result | RowResultContainer | ImageResultContainer | DetailResult] = (
        field(default_factory=list)
    )

    # just an idea. Could help developers to enable pagination without coding it
    auto_pagination: bool = False
    items_per_page: int = 10


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
    ) -> list[Result] | Results | Action | None:
        """
        list[RowResult] in the return type is for backward compatibility and convenience
        when needed to return a simple list of results.
        """
        raise NotImplementedError()

    # TODO: action was dataclass in Result but now it's a dict. Need to find a consistent way
    def on_action(self, action: dict) -> list[Result] | Results | Action | None:
        """
        Extensions should implement this method to handle actions
        """
        pass
