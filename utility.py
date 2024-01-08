from flask import Flask, flash
from sqlalchemy.exc import IntegrityError
from models import db, User, Poem
import requests, json

API_URL = "https://poetrydb.org/"

app = Flask(__name__)


###############################################################################
# Helper Functions for Search Criteria:


def search_poem_title(title):
    """Search for a poem by title and receive matching titles with author."""

    res = requests.get(f"{API_URL}/title/{title}")
    poem_data = res.json()

    title_author_list = []

    for data in sorted(poem_data, key=lambda x: x.get("title", "").lower()):
        poem_title = data.get("title", "")
        poem_author = data.get("author", "")
        title_author_list.append({"Title": poem_title, "Author": poem_author})

    return title_author_list


def search_poem_author(author):
    """Search for author and receive a list of unique matching names."""

    res = requests.get(f"{API_URL}/author/{author}")
    author_data = res.json()

    unique_authors = {}

    for data in sorted(author_data, key=lambda x: x.get("author", "").lower()):
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

    for data in sorted(poem_data, key=lambda x: x.get("title", "").lower()):
        poem_title = data.get("title", "")
        poem_author = data.get("author", "")
        lines_list.append({"Title": poem_title, "Author": poem_author})

    return lines_list


###############################################################################
# Misc helper functions to clean up routes:


def handle_welcome_page(form):
    """Handle search criteria on home page."""

    results = []
    try:
        query = form.query.data
        criteria = form.criteria.data

        if criteria == "title":
            results = search_poem_title(query)
        elif criteria == "author":
            results = search_poem_author(query)
        elif criteria == "line":
            results = search_poem_line(query)
        else:
            results = []
    except AttributeError:
        flash("Couldn't find that! Try again?", "warning")

    return results


def handle_poems_by_author(author_name):
    """List of all poem titles in alphabetical order for a specific author."""

    res = requests.get(f"{API_URL}/author/{author_name}")

    try:
        poem_data = res.json()
    except json.JSONDecodeError:
        return []

    title_list = []

    for data in sorted(poem_data, key=lambda x: x.get("title", "").lower()):
        if not isinstance(data, dict):
            continue

        poem_title = data.get("title", "")
        title_list.append({"Title": poem_title})

    return title_list


def fetch_poem_from_api(title):
    """Fetches poem data from the API."""

    res = requests.get(f"{API_URL}/title/{title}")

    try:
        poem_data = res.json()
    except json.JSONDecodeError:
        return []

    return poem_data


def add_poem_to_database(poem_data, user_id):
    """Adds a poem to the database."""

    if not poem_data:
        return None

    for data in poem_data:
        title = data.get("title")
        author = data.get("author")
        lines = data.get("lines")

        existing_poem = Poem.query.filter_by(title=title, user_id=user_id).first()

        if not existing_poem:
            new_poem = Poem(title=title, author=author, lines=lines, user_id=user_id)
            db.session.add(new_poem)
            db.session.commit()

            return new_poem

    return None


def handle_poem_content(title):
    """Gets all poem content."""

    poem_data = fetch_poem_from_api(title)

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


def handle_signup_form(form):
    """Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message and re-present form.
    """

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                username=form.username.data,
                password=form.password.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()
            return user, None
        except IntegrityError:
            return None, "Username already taken! Try again?"

    return None, None


def is_username_taken(username):
    """Check if a username is already taken."""

    return User.query.filter_by(username=username).first() is not None


def handle_edit_profile(user, form):
    """Update user profile if the password is correct and the username is not taken."""

    try:
        if not User.authenticate(user.username, form.password.data):
            flash("Incorrect password! Try again?", "danger")
            return False

        new_username = form.username.data
        if new_username != user.username and is_username_taken(new_username):
            flash("Username already taken! Try again?", "danger")
            return False

        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.username = new_username
        user.image_url = form.image_url.data or "/static/images/default-pic.png"

        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        flash("An error occurred while updating the profile.", "danger")
        return False
