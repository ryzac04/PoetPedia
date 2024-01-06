import requests, json


API_URL = "https://poetrydb.org/"


###############################################################################
# Helper Functions for Search Criteria:


def search_poem_title(title):
    """Search for a poem by title and receive matching titles with author."""

    res = requests.get(f"{API_URL}/title/{title}")
    poem_data = res.json()

    title_author_list = []

    for data in poem_data:
        poem_title = data.get("title", "")
        poem_author = data.get("author", "")
        title_author_list.append({"Title": poem_title, "Author": poem_author})

    return title_author_list


def search_poem_author(author):
    """Search for author and receive a list of unique matching names."""

    res = requests.get(f"{API_URL}/author/{author}")
    author_data = res.json()

    unique_authors = {}

    for data in author_data:
        poem_author = data.get("author", "")

        if poem_author not in unique_authors:
            unique_authors[poem_author] = {"Author": poem_author}

    result = list(unique_authors.values())

    return result


def search_poem_line(lines):
    """Search for poems by lines and receive a list of titles with author in which the searched-for line is present in the poem."""

    res = requests.get(f"{API_URL}/lines/{lines}")
    poem_data = res.json()

    lines_list = []

    for data in poem_data:
        poem_title = data.get("title", "")
        poem_author = data.get("author", "")
        lines_list.append({"Title": poem_title, "Author": poem_author})

    return lines_list


###############################################################################
# Misc Helper Functions:


def get_poems_by_author(author_name):
    """List of all poems by a specific author."""

    res = requests.get(f"{API_URL}/author/{author_name}")

    try:
        poem_data = res.json()
    except json.JSONDecodeError:
        return []

    title_list = []

    for data in poem_data:
        if not isinstance(data, dict):
            continue

        poem_title = data.get("title", "")
        title_list.append({"Title": poem_title})

    return title_list


def get_poem_content(title):
    """Gets all poem content."""

    res = requests.get(f"{API_URL}/title/{title}")

    try:
        poem_data = res.json()
    except json.JSONDecodeError:
        return []

    poem_content = []

    for data in poem_data:
        if not isinstance(data, dict):
            continue

        poem_title = data.get("title", "")
        poem_author = data.get("author", "")
        poem_lines = data.get("lines", [])
        poem_content.append(
            {"Title": poem_title, "Author": poem_author, "Poem": poem_lines}
        )

    return poem_content



