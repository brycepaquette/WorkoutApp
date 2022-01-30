import re
from flask import Flask, render_template, request, session, sessions, redirect
from sqlalchemy import distinct
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user


"""
Possible Future Enhancements:
* utilize the Blueprint class in flask to organize routes into multiple files. Examples: https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
* implement flashing messages
"""

app = Flask(__name__)

# Set a secret key in order to use sessions
app.secret_key = b'dde02f8c8fb32d19708474f175f062559a3239e5224f651ff6b79c030cf53d70'

# Add authentication (flask-login) to the application
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database (flask-sqlalchemy) in the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workoutapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Added due to warning suggesting it be set to False
db = SQLAlchemy(app)

# User Model
class Users(UserMixin, db.Model):
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

    def check_password(self, password):
        result = check_password_hash(self.password, password)
        return result

    def __repr__(self):
        return '<User %r>' % self.email

# Exercise Model
class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    target = db.Column(db.String(100), unique=False, nullable=False)
    equipment = db.Column(db.String(100), unique=False, nullable=False)
    gif_url = db.Column(db.String(100), unique=False, nullable=False)

    def __repr__(self):
        return '<Exercise %r>' % self.name


exercise_list = Exercises.query.all()
targets = set()
for exercise in exercise_list:
    targets.add(exercise.target)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@app.route("/log", methods=["GET", "POST"])
@login_required
def log():
    return render_template("log.html")


@app.route("/exercises", methods=["GET", "POST"])
@login_required
def exercises():
    global targets
    targets = sorted(targets)    
    return render_template("exercises.html", targets=targets)

@app.route("/exercises/<target>", methods=["GET", "POST"])
@login_required
def targetExercises(target):
    global exercise_list
    list = []
    for exercise in exercise_list:
        if exercise.target == target:
            list.append(exercise)
    return render_template("targetExercises.html", exercises=list, target=target)


@app.route("/profile", methods=["GET"])
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        form = request.form
        
        # Confirm all required fields were sent
        missingFields = []
        for key, value in form.items():
            if value == "":
                missingFields.append(key)
        if missingFields:
            litem = missingFields.pop()
            return f"Error: {', '.join(missingFields)}, and {litem} are required fields!"
        
        # Check for valid weight
        weight = form['Weight']
        if not re.search('[0-9]', weight):
            return "Invalid weight"
        if int(weight) < 60 or int(weight) > 900:
            return "Invalid Weight"
        
        # Check for valid email
        emailRegex = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
        if not re.search(emailRegex, form['Email']):
            return "Invalid Email"
        
        # Check for valid phone number
        phoneRegex = """^[0-9]{3}\.[0-9]{3}\.[0-9]{4}"""
        if not re.search(phoneRegex, form["Phone Number"]):
            return "Invalid Phone Number. Use Format: 555.555.5555"

        # Check if user exists, redirect if exists
        if Users.query.filter_by(email=form['Email']).first():
            return 'User already exists. Please sign in or use a different email.'
        if Users.query.filter_by(phoneNo=form['Phone Number']).first():
            return 'User already exists. Please sign in or use a different phone number.'
                
        # Convert height to inches
        height = int(form["Height-in"]) + (int(form['Height-ft']) * 12)

        # Hash password
        hash = generate_password_hash(form['Password'])

        # Create a new user
        user = Users(
            fname = form['First Name'],        lname = form['Last Name'],
            password = hash,                   email = form['Email'],
            phoneNo = form['Phone Number'],    bYear = int(form['Birth Year']),
            bMonth = int(form['Birth Month']), bDay = int(form['Birth Day']),
            gender = form['Gender'],           height = int(height),
            weight = float(form['Weight'])
        )

        # Add user to the database
        db.session.add(user)
        db.session.commit()

        #redirect to the login page
        return redirect("/login")
    
    return render_template("signup.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = request.form
    if request.method == "POST":
        # Confirm all required fields were sent
        missingFields = []
        for key, value in form.items():
            if value == "":
                missingFields.append(key)
        if missingFields:
            litem = missingFields.pop()
            return f"Error: {', '.join(missingFields)}, and {litem} are required fields!"
        
        # Check for valid email
        emailRegex = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
        if not re.search(emailRegex, form['Email']):
            return "Invalid Email"
        
        # Check if user exists and validate password
        user = Users.query.filter_by(email=form['Email']).first()
        if not user or not user.check_password(form['Password']):
                return 'Email or Password is incorrect.'
        login_user(user, remember=False)
        return redirect('/')
    return render_template('login.html')


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect('/login')

@app.route("/delete", methods=["POST"])
def delete():
    logout_user()
    return redirect('/login')