from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, Email
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


class NameForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired(), Regexp("^[A-Za-z0-9]{8,30}$",
                                                                          message='Your username should be between 8 '
                                                                                  'and 30 characters long, '
                                                                                  'and can only contain alphanumeric '
                                                                                  'letters.')])
    email = StringField("Email", validators=[DataRequired(), Email()])
    about_author = TextAreaField("About Author")
    password_hash = PasswordField("Password", validators=[DataRequired(), Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)("
                                                                                 "?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,"
                                                                                 "10}$", message="Your password "
                                                                                                 "should contain "
                                                                                                 "minimum eight "
                                                                                                 "characters, "
                                                                                                 "at least 1 "
                                                                                                 "uppercase letter, "
                                                                                                 "1 lowercase "
                                                                                                 "letter, 1 number "
                                                                                                 "and 1 special "
                                                                                                 "character:")])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password_hash',
                                                                  message='Passwords '
                                                                          'Must '
                                                                          'Match!')])
    profile_pic = FileField("Profile Pic")
    # recaptcha = RecaptchaField()
    submit = SubmitField("Submit")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    # recaptcha = RecaptchaField()
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    # name == pass data from name in the form/html by WETForm
    searched = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')
