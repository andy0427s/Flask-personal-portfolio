from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '<52f2f7bbd0899acac4c4cc57bad53e4bc96af3abc9128ff2>'

# DB Connection

# suppress SQLAlchemy warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c22011528:Twente0508$@csmysql.cs.cf.ac.uk:3306' \
                                        '/c22011528_mydb'

db = SQLAlchemy(app)

from blog import routes
