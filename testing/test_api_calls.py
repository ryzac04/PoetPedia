"""API call tests."""

## Run the command in the line below in bash terminal ##
# python -m unittest testing/test_api_calls.py #

import os
from unittest import TestCase, mock
from utility import (
    fetch_poem_from_api,
    search_poem_title,
    search_poem_author,
    search_poem_line,
)
from models import db, Poem, User, Favorite

os.environ["DATABASE_URL"] = "postgresql:///PoetPedia_db_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class APITestCase(TestCase):
    """Test cases for various API calls."""

    @mock.patch("utility.requests.get")
    def test_search_poem_title_success(self, mock_requests):
        """Test that search_poem_title function works as expected."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "title": "Test Poem",
                "author": "Test Author",
            }
        ]

        mock_requests.return_value = mock_response

        result = search_poem_title("test-poem")

        self.assertEqual(result, [{"Title": "Test Poem", "Author": "Test Author"}])

        mock_requests.assert_called_once_with("https://poetrydb.org/title/test-poem")

    @mock.patch("utility.requests.get")
    def test_search_poem_title_failure(self, mock_requests):
        """Test that search_poem_title will only work with correct query."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 404

        mock_response.json.return_value = []

        mock_requests.return_value = mock_response

        result = search_poem_title("non-existent-poem")

        self.assertEqual(result, [])

        mock_requests.assert_called_once_with(
            "https://poetrydb.org/title/non-existent-poem"
        )

    @mock.patch("utility.requests.get")
    def test_search_poem_author_success(self, mock_requests):
        """Test that search_poem_author function works as expected."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "author": "Test Author",
            }
        ]

        mock_requests.return_value = mock_response

        result = search_poem_author("test author")

        self.assertEqual(result, [{"Author": "Test Author"}])

        mock_requests.assert_called_once_with("https://poetrydb.org/author/test author")

    @mock.patch("utility.requests.get")
    def test_search_poem_author_failure(self, mock_requests):
        """Test that search_poem_author will only work with correct query."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 404

        mock_response.json.return_value = {}

        mock_requests.return_value = mock_response

        result = search_poem_author("non-existent-author")

        self.assertEqual(result, [])

        mock_requests.assert_called_once_with(
            "https://poetrydb.org/author/non-existent-author"
        )

    @mock.patch("utility.requests.get")
    def test_search_poem_line_success(self, mock_requests):
        """Test that search_poem_line function works as expected."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"title": "", "author": ""}]

        mock_requests.return_value = mock_response

        result = search_poem_line("this is a poetry line")

        self.assertEqual(result, [{"Title": "", "Author": ""}])

        mock_requests.assert_called_once_with(
            "https://poetrydb.org/lines/this is a poetry line"
        )

    @mock.patch("utility.requests.get")
    def test_search_poem_line_failure(self, mock_requests):
        """Test that search_poem_line will only work with correct query."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 404

        mock_response.json.return_value = {}

        mock_requests.return_value = mock_response

        result = search_poem_line("non-existent-lines")

        self.assertEqual(result, [])

        mock_requests.assert_called_once_with(
            "https://poetrydb.org/lines/non-existent-lines"
        )

    @mock.patch("utility.requests.get")
    def test_fetch_poem_from_api_success(self, mock_requests):
        """Test that fetch_peom_from_api function works as expected."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test Poem",
            "author": "Test Author",
        }

        mock_requests.return_value = mock_response

        result = fetch_poem_from_api("test-poem")

        self.assertEqual(result, {"title": "Test Poem", "author": "Test Author"})

        mock_requests.assert_called_once_with("https://poetrydb.org/title/test-poem")

    @mock.patch("utility.requests.get")
    def test_fetch_poem_from_api_failure(self, mock_requests):
        """Test that fetch_poem_from_api will only work with correct query."""

        mock_response = mock.MagicMock()
        mock_response.status_code = 404

        mock_response.json.return_value = None

        mock_requests.return_value = mock_response

        result = fetch_poem_from_api("non-existent-poem")

        self.assertIsNone(result)

        mock_requests.assert_called_once_with(
            "https://poetrydb.org/title/non-existent-poem"
        )
