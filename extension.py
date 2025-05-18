"""
Example of Ulauncher extension code using imaginary extension API.
Implements a search engine using Brave Search.

UI WIREFRAMES
=============

https://excalidraw.com/#json=BvFSaU23gumXNv3MYrhOU,_oZwH481BzZERrLis8l7gQ
They show a potential evolution of the UI and functionality of Ulauncher extensions.


PURPOSE OF THIS CODE
====================

To iterate over the API design, making it
- easy to start using (i.e. low boilerplate code for a minimal extension)
- intuitive and consistent
- future-proof (i.e. tile view for images, etc.)
"""

from ulauncher.api import Extension, RowResult
from bravesearch.queries import BraveQueries
from bravesearch.errors import SearchError


class BraveExtension(Extension):
    """
    Extension features:
    - Search suggestions as user types the query
    - Search results include a website icon, title, and description (domain name + snippet)
    - Search results are clickable and open in the default browser
    - When the image search keyword is used, the results are displayed as tiles with images and 2 lines of text below (domain name + snippet)
    """

    def on_launch(self):
        # Show user a possibility to search all content, only images, only videos, only discussions:
        self.set_query_modifiers(
            {
                "all": "All",
                "images": "Images",
                "videos": "Videos",
                "discussions": "Discussions",
            }
        )

    def on_input(self, input_text: str, trigger_id: str):
        # Validate the API keys
        if (
            not self.preferences["search_api_key"]
            or not self.preferences["autosuggest_api_key"]
        ):
            return [
                RowResult(
                    name="Error",
                    description="Please set your API keys in the preferences.",
                    keep_app_open=True,
                )
            ]

        # Prompt the user to enter a search query
        bs = BraveQueries(
            self.preferences["search_api_key"], self.preferences["autosuggest_api_key"]
        )
        if not input_text.strip():
            return [
                RowResult(
                    name="Brave Search",
                    description="Type your search query...",
                    keep_app_open=True,
                )
            ]

        # Show search suggestions as the user types
        try:
            return [
                RowResult(compact=True, name=s, on_enter=None) for s in bs.search_suggestions(input_text)
            ]
        except SearchError as e:
            return [e.to_row_result()]
        except Exception:
            return [
                RowResult(
                    name="Error",
                    description="An error occurred while fetching suggestions.",
                    keep_app_open=True,
                )
            ]


if __name__ == "__main__":
    BraveExtension().run()
