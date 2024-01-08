"""Poem model tests."""

## Run the command in the line below in bash terminal ##
# python -m unittest testing/test_poem_model.py #

import os
from unittest import TestCase
from models import db, Poem, User, Favorite

os.environ["DATABASE_URL"] = "postgresql:///PoetPedia_db_test"

from app import app

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class PoemModelTestCase(TestCase):
    """Test views for poem model."""

    def setUp(self):
        """Create test client, add sample data for each test."""

        db.drop_all()
        db.create_all()

        self.cleint = app.test_client()

        user = User.signup(
            "testname1",
            "testname2",
            "testname1@test.com",
            "testusername1",
            "test_password1",
            None,
        )
        id = 1111
        user.id = id

        db.session.commit()

        user = User.query.get(id)

        self.user = user

    def tearDown(self):
        """Tear down test client after each test."""

        res = super().tearDown()
        db.session.rollback()
        db.session.remove()
        return res

    def test_poem_model(self):
        """Test that the basic poem model works."""

        test_user = User(
            first_name="test1",
            last_name="test2",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None,
        )
        id = 1111
        test_user.id = id

        test_poem = Poem(
            title="Poem Title",
            author="John Doe",
            lines="This is a test poem",
            user_id=test_user.id,
        )

        db.session.add(test_poem)
        db.session.commit()

        self.assertEqual(test_poem.title, "Poem Title")
        self.assertEqual(test_poem.user_id, test_user.id)

    def test_favorite_poem(self):
        """Test that favoriting a poem works appropriately."""

        test_user = User(
            first_name="test1",
            last_name="test2",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None,
        )
        id = 2222
        test_user.id = id

        test_poem1 = Poem(
            title="Poem Title1",
            author="John Doe",
            lines="This is a test poem.",
            user_id=test_user.id,
        )

        db.session.add_all([test_user, test_poem1])
        db.session.commit()

        favorites = Favorite.query.filter(Favorite.user_id == test_user.id)
        self.assertIsNotNone(favorites)
