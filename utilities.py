import re
from os import linesep
from typing import List


def generate_css_selector(element) -> str:
    """
    Generate a CSS selector for a given HTML element.

    Args:
        element: The HTML element for which to generate the selector.

    Returns:
        A string representing the CSS selector for the given element.
    """
    components: List[str] = []
    while element and element.tag_name.lower() != "html":
        if "id" in element.attrs:
            selector = f"#{element.attrs['id']}"
        elif "class" in element.attrs and " " not in element.attrs["class"]:
            selector = f"{element.tag_name.lower()}.{element.attrs['class']}"
        else:
            selector = element.tag_name.lower()
        components.append(selector)
        element = element.parent

    components.append("html")
    return " > ".join(reversed(components))


def clean_text(text: str) -> str:
    """
    Clean the input text by removing empty lines and consecutive spaces.

    Args:
        text: The input text to clean.

    Returns:
        A cleaned string with no empty lines and no consecutive spaces.
    """
    return re.sub(r"\s+", " ", linesep.join(filter(None, text.splitlines())).strip())
