from flask import Flask, render_template, request, sessions, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

"""
Possible Future Enhancements:
* utilize the Blueprint class in flask to organize routes into multiple files. Examples: https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
* implement flashing messages
"""

app = Flask(__name__)

# Set a secret key in order to use sessions
app.secret_key = b'dde02f8c8fb32d19708474f175f062559a3239e5224f651ff6b79c030cf53d70'

# Initialize database (flask-sqlalchemy) in the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workoutapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Added due to warning suggesting it be set to False
db = SQLAlchemy(app)

# User Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), unique=False, nullable=False)
    lname = db.Column(db.String(100), unique=False, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phoneNo = db.Column(db.String(100), unique=True, nullable=False)
    bYear = db.Column(db.Integer, unique=False, nullable=False)
    bMonth = db.Column(db.Integer, unique=False, nullable=False)
    bDay = db.Column(db.Integer, unique=False, nullable=False)
    gender = db.Column(db.Integer, unique=False, nullable=False)
    height = db.Column(db.Integer, unique=False, nullable=False)
    weight = db.Column(db.Float, unique=False, nullable=False)

# Add authentication (flask-login) to the application
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.get(user_id)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        form = request.form
        hash = generate_password_hash(form['password'])

        # Confirm all required fields were sent
        # TODO

        # Check if user exists, redirect if exists
        user = Users.query.filter_by(username=form['username'])
        if user:
            return 'User already exists.'

        # Create a new user
        user = Users(
            fname = form['fname'],       lname = form['lname'],
            password = form['password'], email = form['email'],
            phoneNo = form['phoneNo'],   bYear = form['bYear'],
            bMonth = form['bMonth'],     bDay = form['bDay'],
            gender = form['gender'],     height = form['height'],
            weight = form['weight']
        )

        # Add user to the database
        db.session.add(user)
        db.session.commit()

        #redirect to the login page
        return redirect("/login")
    
    return render_template("signup.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure all fields were submitted
        pass
        # Check if the user exists
    return


@app.route("/logout", methods=["GET", "POST"])
def logout():
    return "Logout"