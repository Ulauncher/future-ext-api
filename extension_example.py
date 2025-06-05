"""
Example of Ulauncher extension API and extension code.
The extension is a search engine via Brave Search API.

UI WIREFRAMES
=============

🖼 https://excalidraw.com/#json=VLwqQiG06HqddDr1nCFvk,5IlaTfPYfIWWyREPc8oPmw

Wireframes show a potential evolution of the UI and functionality of
Ulauncher extensions.


PURPOSE OF THIS CODE
====================

Is to iterate over the API design, making it
- easy to start using (i.e. low boilerplate code for a minimal extension)
- intuitive and consistent
- future-proof (i.e. tile view for images, etc.)

FUTURE EXTENSION FEATURES
=========================

feature                   when                         UI                                    use cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
result actions            after v6                     a bar at the bottom, cicle through    plenty
^                                                      options by Tab key
image results             after v6                     as tiles with images and 2 lines      emoji picker, web search, file search
detailed view             after v6                     one or more items of varying height   file details, LLM output, word definition
pagination                after v6                     via result actions                    search results, file browser
mixed results             when we see demand           as on the wireframes                  searching web
dividers                  when we see demand           as on the wireframes                  for mixed results,
^                                                                                            search results from multiple files
keywordless activation    "how" is more unclear        just type the query                   unit conversion, mixed results from
^                                                                                            multiple extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from api_example import (
    Extension,
    Action,
    OpenUrlAction,
    Results,
    ImageResult,
    Result,
    RowResultContainer,
    ImageResultContainer,
)
from bravesearch import BraveQueries, SearchError


class RunQueryAction(Action):
    type = "run_query"
    label = "Run Query"
    query: str

    def __init__(self, query: str):
        super().__init__()
        self.query = query


class SaveImageAction(Action):
    type = "save_image"
    label = "Save Image"
    image_url: str
    filename: str

    def __init__(self, image_url: str, filename: str):
        super().__init__()
        self.image_url = image_url
        self.filename = filename


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
                Result(
                    name="Error",
                    description="Please set your API keys in the preferences.",
                )
            ]

        # Prompt the user to enter a search query
        if not input_text.strip():
            return [
                Result(
                    name="Brave Search",
                    description="Type your search query...",
                )
            ]

        # Show search suggestions as the user types
        try:
            return [
                Result(
                    compact=True,
                    name=s,
                    actions=[RunQueryAction(s)],
                )
                for s in self.bs().search_suggestions(input_text)
            ]
        except SearchError as e:
            return [e.to_row_result()]
        except Exception:
            return [
                Result(
                    name="Error",
                    description="An error occurred while fetching suggestions.",
                )
            ]

    def on_action(self, action: dict):
        if action.get("type") == "run_query":
            run_query_action = RunQueryAction(**action)
            return self.search(run_query_action.query)
        elif isinstance(action, SaveImageAction):
            # save to ~/Pictures
            pass

    def search(self, query: str):
        try:
            results = Results()
            results.auto_pagination = True

            brave_res = self.bs().search(query)
            if brave_res.has_results is False:
                return [
                    Result(
                        name="No results found",
                        description="Try a different query.",
                    )
                ]
            for s in brave_res.pages:
                results.items.append(
                    Result(
                        icon=s.domain_icon_url,
                        name=s.name,
                        description=s.snippet,
                        actions=[OpenUrlAction(s.url)],
                    )
                )
            if brave_res.discussions:
                # create a container for discussion results
                discussion_container = RowResultContainer(
                    show_header=True, header_title="Discussions"
                )
                for s in brave_res.discussions:
                    discussion_container.items.append(
                        Result(
                            compact=True,
                            icon=s.domain_icon_url,
                            name=s.name,
                            description=s.snippet,
                            actions=[OpenUrlAction(s.url)],
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
                            actions=[
                                OpenUrlAction(s.url),
                                SaveImageAction(s.image_url, s.name),
                            ],
                        )
                    )
                results.items.append(image_container)

            return results
        except SearchError as e:
            return [e.to_row_result()]
        except Exception:
            return [
                Result(
                    name="Error",
                    description="An error occurred while searching.",
                )
            ]

    def bs(self):
        return BraveQueries(
            self.preferences["search_api_key"], self.preferences["autosuggest_api_key"]
        )


if __name__ == "__main__":
    BraveExtension().run()
