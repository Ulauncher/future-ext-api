"""
Example of Ulauncher extension API and extension code.
The extension is a search engine via Brave Search API.

UI WIREFRAMES
=============

https://excalidraw.com/#json=BvFSaU23gumXNv3MYrhOU,_oZwH481BzZERrLis8l7gQ
Wireframes show a potential evolution of the UI and functionality of
Ulauncher extensions.


PURPOSE OF THIS CODE
====================

Is to iterate over the API design, making it
- easy to start using (i.e. low boilerplate code for a minimal extension)
- intuitive and consistent
- future-proof (i.e. tile view for images, etc.)
"""

from api_example import (
    Extension,
    NavItem,
    Navigation,
    OpenUrlAction,
    Results,
    ImageResult,
    RowResult,
    RowResultContainer,
    ImageResultContainer,
)
from bravesearch import BraveQueries, SearchError
from functools import partial


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
                RowResult(
                    compact=True,
                    name=s,
                    on_enter=lambda: self.search(s),
                )
                for s in self.bs().search_suggestions(input_text)
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

    def search(self, query: str, offset: int = 0, limit: int = 10):
        try:
            results = Results()
            brave_res = self.bs().search(query)
            if brave_res.has_results is False:
                return [
                    RowResult(
                        name="No results found",
                        description="Try a different query.",
                        keep_app_open=True,
                    )
                ]
            for s in brave_res.pages:
                results.items.append(
                    RowResult(
                        icon=s.domain_icon_url,
                        name=s.name,
                        description=s.snippet,
                        on_enter=partial(OpenUrlAction, s.url),
                    )
                )
            if brave_res.discussions:
                # create a container for discussion results
                discussion_container = RowResultContainer(
                    show_header=True, header_title="Discussions"
                )
                for s in brave_res.discussions:
                    discussion_container.items.append(
                        RowResult(
                            compact=True,
                            icon=s.domain_icon_url,
                            name=s.name,
                            description=s.snippet,
                            on_enter=partial(OpenUrlAction, s.url),
                        )
                    )
                results.items.append(discussion_container)
            if brave_res.images:
                image_container = ImageResultContainer(
                    show_header=True, header_title="Images"
                )
                for s in brave_res.images:
                    image_container.items.append(
                        ImageResult(  # can optionally accept width and height
                            image=s.image_url,
                            name=s.name,
                            description=s.description,
                            on_enter=partial(OpenUrlAction, s.url),
                            on_alt_enter=partial(
                                self.on_image_options,
                                s.image_url
                            )
                        )
                    )
                results.items.append(image_container)

            # Set navigation config
            total_items = (
                len(results.items) + len(brave_res.discussions) + len(brave_res.images)
            )
            results.navigation = Navigation(
                back=NavItem(name="go back", enabled=offset > 0),
                forward=NavItem(name="see more", enabled=total_items == limit),
                enter=NavItem(name="open in browser"),
                alt_enter=NavItem(name="options"),
            )

            return results
        except SearchError as e:
            return [e.to_row_result()]
        except Exception:
            return [
                RowResult(
                    name="Error",
                    description="An error occurred while searching.",
                    keep_app_open=True,
                )
            ]

    def on_image_options(self, image_url: str):
        """
        Show options for the image, such as saving it to Downloads.
        """
        raise NotImplementedError()

    def bs(self):
        return BraveQueries(
            self.preferences["search_api_key"], self.preferences["autosuggest_api_key"]
        )


if __name__ == "__main__":
    BraveExtension().run()
