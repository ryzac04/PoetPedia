import os

from flask import Flask, render_template, redirect, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Poem, Favorite
from forms import PoemSearchForm, RegisterForm, LoginForm, EditForm, DeleteForm
from utility import (
    handle_poems_by_author,
    handle_poem_content,
    handle_welcome_page,
    handle_signup_form,
    handle_edit_profile,
    fetch_poem_from_api,
    add_poem_to_database,
    handle_delete_profile,
)

CURR_USER_KEY = "curr_user"

API_URL = "https://poetrydb.org/"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///PoetPedia_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "abc123")
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)


################################################################################
# Poetry Search Routes


@app.route("/")
def home_page():
    """Redirect to welcome page."""

    return redirect("/welcome")


@app.route("/welcome", methods=["GET", "POST"])
def welcome_page():
    """Welcome page where user can search for poems by chosen criteria."""

    form = PoemSearchForm()

    if form.validate_on_submit():
        results = handle_welcome_page(form)
        return render_template("poems/welcome.html", results=results, form=form)

    return render_template("poems/welcome.html", form=form)


@app.route("/author/<author_name>")
def poems_by_author(author_name):
    """Show all poems on an author's page."""

    poems = handle_poems_by_author(author_name)

    return render_template("poems/author.html", author_name=author_name, poems=poems)


@app.route("/poem/<poem_title>")
def poem_content(poem_title):
    """Shows poem content on separate page."""

    poem = handle_poem_content(poem_title)
    poem_data = fetch_poem_from_api(poem_title)
    poem_id = None
    is_favorited = False

    if g.user:
        if poem_data:
            new_poem = Poem.query.filter_by(title=poem_title, user_id=g.user.id).first()
            poem_id = new_poem.id if new_poem else None

            if poem_id:
                is_favorited = Favorite.query.filter_by(
                    user_id=g.user.id, poem_id=poem_id
                ).first()

            if not poem_id:
                add_poem = add_poem_to_database(poem_data, g.user.id)
                poem_id = add_poem.id

    return render_template(
        "poems/show.html",
        poem_title=poem_title,
        poem=poem,
        poem_id=poem_id,
        is_favorited=is_favorited,
    )


@app.route("/toggle_favorite/<int:poem_id>", methods=["POST"])
def toggle_favorite(poem_id):
    """Toggles a favorited or un-favorited poem."""

    user_id = session.get(CURR_USER_KEY)

    if user_id:
        poem = Poem.query.get(poem_id)

        if poem:
            is_favorited = Favorite.query.filter_by(
                user_id=user_id, poem_id=poem.id
            ).first()

            if is_favorited:
                db.session.delete(is_favorited)
                flash(f"{poem.title} has been removed from your favorites", "success")
            else:
                new_favorite = Favorite(user_id=user_id, poem_id=poem.id)
                db.session.add(new_favorite)
                flash(f"{poem.title} has been added to your favorites", "success")

            db.session.commit()

    return redirect(f"/poem/{poem.title}")


###############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If user logged in, add current user to Flask global."""

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


###############################################################################
# User Routes


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """Handle user signup."""

    form = RegisterForm()
    user, error = handle_signup_form(form)

    if user:
        do_login(user)
        flash(
            f"Welcome, {user.username}! You've successfuly created your account!",
            "success",
        )
        return redirect("/")
    elif error:
        flash(error, "warning")

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

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    flash("You have successfully logged out!", "success")
    return redirect("/login")


@app.route("/users/favorites/<int:user_id>/")
def favorites_list(user_id):
    """List of user's favorited poems."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    favorite_poems = user.favorites

    return render_template(
        "users/favorites.html", user=user, favorite_poems=favorite_poems
    )


@app.route("/users/profile/<int:user_id>", methods=["GET", "POST"])
def show_user(user_id):
    """Show user profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template("users/show.html", user=user)


@app.route("/users/edit/<int:user>", methods=["GET", "POST"])
def edit_profile(user):
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    current_user = g.user
    form = EditForm()

    if form.validate_on_submit():
        if handle_edit_profile(current_user, form):
            return redirect(f"/users/profile/{current_user.id}")

    return render_template("users/edit.html", form=form, user_id=current_user.id)


@app.route("/users/delete/<int:user>", methods=["GET", "POST"])
def delete_profile(user):
    """Form to verify that user wants to delete their profile."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    current_user = g.user
    form = DeleteForm()

    if form.validate_on_submit():
        if handle_delete_profile(current_user, form):
            flash("You have successfully deleted your account!", "success")
            return redirect("/welcome")

    return render_template("users/delete.html", form=form, user_id=current_user.id)
