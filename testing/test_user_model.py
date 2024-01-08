"""User model tests."""

## Run the command in the line below in bash terminal ##
# python -m unittest testing/tests_user_model.py #

import os
from unittest import TestCase
from models import db, User

os.environ["DATABASE_URL"] = "postgresql:///PoetPedia_db_test"

from app import app

db.create_all()

app.config["WTF_CSRF_ENABLED"] = False


class UserModelTestCase(TestCase):
    """Test views for user model."""

    def setUp(self):
        """Create test clients, add sample data for each test."""

        db.drop_all()
        db.create_all()

        user1 = User.signup(
            "test_first_name1",
            "test_last_name1",
            "test_name1@email.com",
            "test_username1",
            "test_password1",
            None,
        )
        id1 = 1111
        user1.id = id1

        user2 = User.signup(
            "test_first_name2",
            "test_last_name2",
            "test_name2@email.com",
            "test_username2",
            "test_password2",
            None,
        )
        id2 = 222
        user2.id = id2

        db.session.commit()

        user1 = User.query.get(id1)
        user2 = User.query.get(id2)

        self.user1 = user1
        self.user2 = user2

    def tearDown(self):
        """Tear down test clients after each test."""

        res = super().tearDown()
        db.session.rollback()
        db.session.remove()
        return res

    def test_user_model(self):
        """Test that the basic user model works."""

        user = User(
            first_name="test1",
            last_name="test2",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None,
        )

        db.session.add(user)
        db.session.commit()

        self.assertEqual(len(user.poems), 0)

    def test_user_signup(self):
        """Test that the signup classmethod works as expected."""

        user = User.signup(
            "testname1",
            "testname2",
            "testname1@test.com",
            "testusername1",
            "test_password1",
            None,
        )
        db.session.commit()

        self.assertEqual(user.username, "testusername1")
        self.assertTrue(user.password.startswith("$2b$"))
        self.assertEqual(user.image_url, "/static/images/default-pic.png")

    def test_authenticate(self):
        """Test that the authenticate class method works as expected."""

        user = User.signup(
            "testname1",
            "testname2",
            "testname1@test.com",
            "testusername1",
            "test_password1",
            "someurl",
        )
        db.session.commit()

        user_account = User.authenticate("testusername1", "test_password1")

        self.assertEqual(user, user_account)

    def test_authenticate_invalid_username(self):
        """Test that authentication will fail if given invalid username."""

        user = User.signup(
            "testname1",
            "testname2",
            "testname1@test.com",
            "testusername1",
            "test_password1",
            "someurl",
        )
        db.session.commit()

        user_account = User.authenticate("testusername2", "test_password1")

        self.assertNotEqual(user, user_account)

    def test_authenticate_invalid_password(self):
        """Test that authentication will fail if given invalid password."""

        user = User.signup(
            "testname1",
            "testname2",
            "testname1@test.com",
            "testusername1",
            "test_password1",
            "someurl",
        )
        db.session.commit()

        user_account = User.authenticate("testusername2", "test_password2")

        self.assertNotEqual(user, user_account)
