from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Text
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Model for site user(s)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.Text, nullable=False)

    last_name = db.Column(db.Text, nullable=False)

    email = db.Column(db.Text, nullable=False)

    username = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    image_url = db.Column(db.Text, default="/static/images/default-pic.png")

    poems = db.relationship("Poem", backref="user", cascade="all, delete-orphan")

    favorites = db.relationship(
        "Favorite", backref="user", cascade="all, delete-orphan"
    )

    @classmethod
    def signup(cls, first_name, last_name, email, username, password, image_url):
        """Register user with hashed password and return user."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists and password is correct. Return user if valid; else return False."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        else:
            return None


class Poem(db.Model):
    """Model for poems."""

    __tablename__ = "poems"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Text)

    author = db.Column(db.Text)

    lines = db.Column(db.Text)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False
    )

    favorites = db.relationship(
        "Favorite", backref="poem", cascade="all, delete-orphan"
    )


class Favorite(db.Model):
    """Mapping user likes to chosen poems."""

    __tablename__ = "favorites"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="cascade"), primary_key=True
    )

    poem_id = db.Column(
        db.Integer, db.ForeignKey("poems.id", ondelete="cascade"), primary_key=True
    )
