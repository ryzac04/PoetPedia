from flask import Flask, render_template, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User, Poem
from forms import PoemSearchForm, RegisterForm, LoginForm, EditForm
from helpers import (
    search_poem_author,
    search_poem_line,
    search_poem_title,
    get_poems_by_author,
    get_poem_content,
)

CURR_USER_KEY = "curr_user"

API_URL = "https://poetrydb.org/"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///PoetPedia_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


################################################################################ Poetry Search Routes


@app.route("/")
def home_page():
    """Redirect to welcome page."""
    return redirect("/welcome")


@app.route("/welcome", methods=["GET", "POST"])
def welcome_page():
    """Welcome page where user can search for poems by chosen criteria."""

    form = PoemSearchForm()
    results = []

    if form.validate_on_submit():
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
            return render_template("poems/welcome.html", results=results, form=form)

    return render_template("poems/welcome.html", results=results, form=form)


@app.route("/author/<author_name>")
def poems_by_author(author_name):
    """Show all poems on an author's page."""

    poems = get_poems_by_author(author_name)

    return render_template("poems/author.html", author_name=author_name, poems=poems)


@app.route("/poem/<poem_title>")
def poem_content(poem_title):
    """Shows poem content on own page."""

    poem = get_poem_content(poem_title)

    return render_template("poems/show.html", poem_title=poem_title, poem=poem)


###############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Login user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


################################################################################ User Routes


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = RegisterForm()
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
        except IntegrityError:
            flash("Username already taken! Try again?", "warning")

        do_login(user)

        return redirect("/")
    else:
        return render_template("users/signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")
        flash("Invalid Credentials!", "warning")

    return render_template("users/login.html", form=form)


@app.route("/logout")
def logout():
    """Handle user logout."""

    do_logout()

    flash("You have successfully logged out!", "success")
    return redirect("/login")


@app.route("/users/profile/<int:user_id>")
def show_user(user_id):
    """Show user profile."""

    user = User.query.get(user_id)

    return render_template("users/show.html", user=user)


@app.route("/users/edit/<int:user>", methods=["GET", "POST"])
def edit_profile(user):
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = g.user
    form = EditForm()

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data or "/static/images/default-pic.png"

            db.session.commit()
            return redirect(f"/users/profile/{user.id}")
        
        flash("Incorrect password! Try again?", "danger")
    return render_template("users/edit.html", form=form, user_id=user.id)


@app.route("/users/delete", methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


