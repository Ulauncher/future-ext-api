from extension_example import RowResult


class WebPageResult:
    url: str
    name: str
    snippet: str
    domain_icon_url: str


class ImageResult:
    url: str
    image_url: str
    domain_icon_url: str
    name: str
    description: str


class SearchResults:
    has_results: bool
    pages: list[WebPageResult]
    discussions: list[WebPageResult]
    images: list[ImageResult]


class BraveQueries:
    def __init__(self, search_api_key: str, autosuggest_api_key: str):
        self.api_key = search_api_key
        self.autosuggest_api_key = autosuggest_api_key

    def search_suggestions(self, query: str) -> list[str]:
        return []

    def search(self, query: str) -> SearchResults:
        raise NotImplementedError("Search method not implemented")


class SearchError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_row_result(self) -> RowResult:
        return RowResult(
            name="Error",
            description=self.message,
            keep_app_open=True,
        )
