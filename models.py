# Define User model
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_authorized = db.Column(db.Boolean, default=False)
    clock_records = db.relationship("ClockRecord", back_populates="user")

# Define ClockRecord model
class ClockRecord(db.Model):
    __tablename__ = 'clock_records'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clock_in_time = db.Column(db.DateTime, nullable=True)
    clock_out_time = db.Column(db.DateTime, nullable=True)
    
    # Define the relationship to User with back_populates
    user = db.relationship("User", back_populates="clock_records")

    