from flask import Flask, render_template, sessions
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

"""
Possible Future Enhancements:
* utilize the Blueprint class in flask to organize routes into multiple files. Examples: https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
"""

app = Flask(__name__)

# Set a secret key in order to use sessions
app.secret_key = b'dde02f8c8fb32d19708474f175f062559a3239e5224f651ff6b79c030cf53d70'

# Initialize database (flask-sqlalchemy) in the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://workoutapp.db'
db = SQLAlchemy(app)

# Add authentication (flask-login) to the application
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return "Login"


@app.route("/logout", methods=["GET", "POST"])
def logout():
    return "Logout"