from models import db
from datetime import datetime
 


class User(db.Model):
    __tablename__ = 'users'  # Ensure table name matches foreign key reference
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    scores = db.relationship('Score', backref='user', lazy=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    
    