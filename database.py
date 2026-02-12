from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(150), unique=True, nullable=False)
    password     = db.Column(db.String(150), nullable=False)
    allergies    = db.Column(db.Text, default="")  # comma separated e.g. "peanuts,dairy,gluten"
    diet_notes   = db.Column(db.Text, default="")  # any extra notes e.g. "vegetarian"