from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_recaptcha import ReCaptcha
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor


app = Flask(__name__)
app.config['SECRET_KEY'] = '<52f2f7bbd0899acac4c4cc57bad53e4bc96af3abc9128ff2>'

# ReCaptcha security config
app.config["RECAPTCHA_PUBLIC_KEY"] = "6Ld-w_EjAAAAAHemkG8kJzpZdHEo-bZWuZmKX4sE"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6Ld-w_EjAAAAAPrqy3uaYdLCtDD151YcGR3H0NFF"

# Uploaded file folder setting
UPLOAD_FOLDER = 'blog/static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# suppress SQLAlchemy warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c22011528:Twente0508$@csmysql.cs.cf.ac.uk:3306' \
                                        '/c22011528_mydb'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask Mail config
# Code to send the mail through the smtp connection
# taken from mailtrap.io
# accessed 10-01-2023
# https://mailtrap.io/blog/flask-email-sending/
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "andy0427s@gmail.com"
app.config['MAIL_PASSWORD'] = "opwcjwhvmsvopmqx"
mail = Mail(app)
# End of referenced code.

# Flask Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# CKeditor
ckeditor = CKEditor(app)

from blog import routes

