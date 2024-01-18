from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, Length


class PoemSearchForm(FlaskForm):
    """Form for searching for poems by title."""

    query = StringField("What are you looking for?", validators=[DataRequired()])
    criteria = SelectField(
        "Search By",
        choices=[("title", "Title"), ("author", "Author"), ("line", "Line")],
    )


class RegisterForm(FlaskForm):
    """Form for adding first-time users."""

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])
    image_url = StringField("(Optional) Image URL")


class LoginForm(FlaskForm):
    """Form for logging in already-registered users."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])


class EditForm(FlaskForm):
    """Form for editing user information."""

    first_name = StringField("Change First Name")
    last_name = StringField("Change Last Name")
    email = StringField("Change E-mail")
    username = StringField("Change Username")
    image_url = StringField("Change Image URL")
    password = PasswordField(
        "Enter password to confirm changes", validators=[Length(min=6)]
    )


class DeleteForm(FlaskForm):
    """Form to confirm profile deletion."""

    delete = PasswordField("Enter password to confirm")
