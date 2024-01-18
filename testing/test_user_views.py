"""User view tests."""

## Run the command in the line below in bash terminal ##
# python -m unittest testing/test_user_views.py #

import os
from flask import session
from unittest import TestCase
from models import db, Poem, User, Favorite

os.environ["DATABASE_URL"] = "postgresql:///PoetPedia_db_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class UserViewTestCase(TestCase):
    """Test views for a user."""

    def setUp(self):
        """Create test users and poems with sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user1 = User.signup(
            "test_first_name1",
            "test_last_name1",
            "test_name1@email.com",
            "test_username1",
            "test_password1",
            None,
        )
        id1 = 1111
        self.user1.id = id1

        db.session.add(self.user1)
        db.session.commit()

    def tearDown(self):
        """Tear down test clients and poems after each test."""

        res = super().tearDown()
        db.session.rollback()
        db.session.remove()
        return res

    def setup_favorites(self):
        """Favorites set up for use in other tests."""

        poem1 = Poem(
            id=1234,
            title="Favorite Poem",
            author="Favorite Author",
            lines="Some poetry here.",
            user_id=self.user1.id,
        )

        db.session.add(poem1)
        db.session.commit()

        favorite = Favorite(user_id=self.user1.id, poem_id=1234)
        db.session.add(favorite)
        db.session.commit()

    def test_welcome_page(self):
        """Test first page a user sees"""

        with self.client as c:
            resp = c.get("/welcome")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome", html)

    def test_toggle_favorite(self):
        """Test the toggle_favorite route."""

        user = User.signup(
            "test_first_name",
            "test_last_name",
            "test_name1@email.com",
            "test_username",
            "test_password",
            None,
        )
        id = 0000
        user.id = id

        test_poem = Poem(
            title="Poem Title",
            author="John Doe",
            lines="This is a test poem",
            user_id=user.id,
        )

        db.session.add_all([user, test_poem])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = User.query.first().id

            poem_id = Poem.query.first().id
            response = c.post(f"/toggle_favorite/{poem_id}")

            self.assertEqual(response.status_code, 302)

            user_id = session[CURR_USER_KEY]
            favorite = Favorite.query.filter_by(
                user_id=user_id, poem_id=poem_id
            ).first()

            self.assertIsNotNone(favorite)

    def test_sign_up(self):
        """Test that a user can sign up."""

        with self.client as c:
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sign-Up Form!", html)

    def test_log_in(self):
        """Test that a user can log in."""

        with self.client as c:
            resp = c.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Login Below.", html)

    def test_favorites_list(self):
        """Test favorites list route."""

        self.setup_favorites()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            resp = c.get(f"/users/favorites/{self.user1.id}/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Favorite Author", html)

    def test_show_user(self):
        """Test user profile page."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
        resp = c.get(f"/users/profile/{self.user1.id}")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("test_username1", html)

    def test_edit_profile(self):
        """Test editing user's information."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

        user1 = User.query.filter_by(username="test_username1").first()
        self.user1.id = user1.id

        resp = c.post(
            f"/users/edit/{user1.id}",
            data={
                "first_name": "edited_first_name",
                "last_name": "edited_last_name",
                "email": "edited@email.com",
                "username": "edited_username",
                "password": "test_password1",
                "image_url": "edited_url",
            },
            follow_redirects=True,
        )
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)

        self.assertIn("edited@email.com", html)
        self.assertIn("edited_first_name", html)
        self.assertNotIn("test_username1", html)

    def test_unauthorized_edit_profile(self):
        """Test that a user cannot edit profile if not logged in."""

        with self.client as c:
            user1 = User.query.filter_by(username="test_username1").first()
            self.user1.id = user1.id

            resp = c.post(
                f"/users/edit/{user1.id}",
                data={
                    "first_name": "edited_first_name",
                    "last_name": "edited_last_name",
                    "email": "edited@email.com",
                    "username": "edited_username",
                    "password": "test_password1",
                    "image_url": "edited_url",
                },
                follow_redirects=True,
            )
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)

        self.assertIn("Access unauthorized", html)
