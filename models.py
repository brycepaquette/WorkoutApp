from enum import unique
from . import db

class User(db.model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), unique=False, nullable=False)
    lname = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phoneNo = db.Column(db.String(100), unique=True, nullable=False)
    bYear = db.Column(db.Integer, unique=False, nullable=False)
    bMonth = db.Column(db.Integer, unique=False, nullable=False)
    bDay = db.Column(db.Integer, unique=False, nullable=False)
    gender = db.Column(db.Integer, unique=False, nullable=False)
    height = db.Column(db.Integer, unique=False, nullable=False)
    weight = db.Column(db.Float, unique=False, nullable=False)