import calendar
from datetime import date, datetime
import re
from flask import Flask, render_template, request, redirect
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
    phoneNo = db.Column(db.String(100), unique=True, nullable=False) # Must be in format 555.555.5555
    bYear = db.Column(db.Integer, unique=False, nullable=False)
    bMonth = db.Column(db.Integer, unique=False, nullable=False)
    bDay = db.Column(db.Integer, unique=False, nullable=False)
    gender = db.Column(db.Integer, unique=False, nullable=False) # 0 = Female, 1 = Male, 2 = Other
    height = db.Column(db.Integer, unique=False, nullable=False) # Height stored as inches
    weight = db.Column(db.Float, unique=False, nullable=False) # Weight stored as pounds

    def check_password(self, password):
        result = check_password_hash(self.password, password)
        return result

    def __repr__(self):
        return '<User %r>' % self.email

# Exercise Model
class Exercises(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    target = db.Column(db.String(100), unique=False, nullable=False) # Area of Body (ex. Arms, Legs, Cardio, etc.)
    equipment = db.Column(db.String(100), unique=False, nullable=False) # Equipment needed to perform exercise
    gif_url = db.Column(db.String(100), unique=False, nullable=False) # Instructional GIF of exercise

    def __repr__(self):
        return '<Exercise %r>' % self.name

# Workout Log Model
class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    recorded = db.Column(db.DateTime, unique=False, nullable=False)
    exercise = db.Column(db.String(100), unique=False, nullable=False)
    type = db.Column(db.String(100), unique=False, nullable=False) # Cardio or weightlift
    reps = db.Column(db.Integer, unique=False, nullable=True)
    weight = db.Column(db.Float, unique=False, nullable=True) # Measured in lbs.
    duration = db.Column(db.Integer, unique=False, nullable=True) # Measured in mins
    distance = db.Column(db.Float, unique=False, nullable=True) # Measured in mi.
    avgSpeed = db.Column(db.Float, unique=False, nullable=True) # Measured in MPH
    calories = db.Column(db.Integer, unique=False, nullable=True) # Calorie Estimation using formula from https://fitness.stackexchange.com/questions/32401/how-to-calculate-calories-in-kcal-from-time-and-distance-running
    difficulty = db.Column(db.Integer, unique=False, nullable=True) # Difficulty scale from 0 to 10

    def __repr__(self):
        return '<WorkoutLog %r>' % self.id


# Generate a unique list of targets for exercises page
exerciseList = Exercises.query.all()
targets = set()
for exercise in exerciseList:
    targets.add(exercise.target)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route("/", methods=["GET"])
@login_required
def index():
    # Get info for dashboard if user is logged in
    if current_user.is_authenticated:
        today = date.today()
        monthName = today.strftime("%B")
        daysInMonth = calendar.monthrange(today.year, today.month)[1]
        count = 0
        totalDist = 0
        BMI = round(((current_user.weight / (current_user.height ** 2)) * 703),1)
        workouts = WorkoutLog.query.filter_by(userId=current_user.id)
        last_date = None
        for workout in workouts:
            print(workout.recorded.date())
            if workout.recorded.date() >= today.replace(day=1):
                if workout.recorded.date() != last_date:
                    count += 1
                    last_date = workout.recorded.date()
                if workout.distance != None:
                    totalDist += workout.distance

    return render_template("index.html", count=count, daysInMonth=daysInMonth, totalDist=totalDist, monthName=monthName, BMI=BMI)


@app.route("/workouts", methods=["GET"])
@login_required
def workout():
    workouts = ["cardio", "strength training"]
    return render_template("workouts.html", workouts=workouts)


@app.route("/workouts/<workout>", methods=["GET", "POST"])
@login_required
def workoutLog(workout):
    recorded = date.today()
    exercise_value = ""
    weight_value = ""
    diff_value = ""
    reps_value = 0
    exercises = []
    workoutLogs = WorkoutLog.query.filter_by(recorded=f"{recorded.strftime('%Y-%m-%d')} 00:00:00.000000", userId=current_user.id).all()
    scale = range(1,11)
    reps = range(20, 0, -1)


    # List of exercises dependant on the workout passed from url
    for exercise in exerciseList:
        if workout == "cardio" and exercise.target == "cardio":
            exercises.append(exercise)
        elif workout == "strength training" and exercise.target != "cardio":
            exercises.append(exercise)

    if request.method == "POST":
        form = request.form
        age = recorded.year - current_user.bYear
        weight = current_user.weight
        gender = current_user.gender
        exercise_value = form['Exercise']
        diff_value = int(form['Difficulty'])
        
        if workout == "cardio":
            duration = form['Duration']
            dist = form['Distance']
            # Calculate Calories Burned
            calories = None

            if gender == 1:
                age_coeff = 0.2017
                weight_coeff = 0.09036
            else:
                age_coeff = 0.074
                weight_coeff = 0.05741
            calories = round(abs((((age * age_coeff) - (weight * weight_coeff)) * int(duration)) / 4.184))

            # Calculate AVG speed if time and duration are not blank
            avgSpeed = None
            if dist != "":
                avgSpeed = float(dist) / int(duration) * 60

            log = WorkoutLog(
                userId = current_user.id,
                recorded = recorded,
                exercise = form['Exercise'],
                type = workout,
                duration = duration,
                distance = dist if dist != "" else None,
                avgSpeed = avgSpeed,
                calories = calories,
                difficulty = form['Difficulty']
            )
        elif workout == "strength training":
            reps_value = int(form['Reps'])
            weight_value = form['Weight']
            log = WorkoutLog(
                userId = current_user.id,
                recorded = recorded,
                exercise = form['Exercise'],
                type = workout,
                reps = form['Reps'],
                weight = form['Weight'],
                difficulty = form['Difficulty']
            )

        # Add user to the database
        db.session.add(log)
        db.session.commit()
    return render_template("workoutLog.html", workout=workout, 
                                                exercises=exercises, 
                                                workoutLogs=workoutLogs, 
                                                scale=scale, 
                                                reps=reps, 
                                                today=recorded, 
                                                exercise=exercise,
                                                reps_value = reps_value,
                                                exercise_value = exercise_value,
                                                weight_value = weight_value,
                                                diff_value = diff_value)



@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    recorded = date.today().strftime('%Y-%m-%d')
    if request.method == "POST":
        recorded = request.form['date']
    workoutLogs = WorkoutLog.query.filter_by(recorded=f"{recorded} 00:00:00.000000", userId=current_user.id).all()
    date_msg = datetime.strptime(recorded, '%Y-%m-%d').strftime('%m/%d/%Y')
    return render_template("history.html", workoutLogs=workoutLogs, recorded=recorded, date_msg=date_msg)


@app.route("/exercises", methods=["GET"])
@login_required
def exercises():
    global targets
    targets = sorted(targets)
    return render_template("exercises.html", targets=targets)

@app.route("/exercises/<target>", methods=["GET"])
@login_required
def targetExercises(target):
    global exerciseList
    list = []
    for exercise in exerciseList:
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