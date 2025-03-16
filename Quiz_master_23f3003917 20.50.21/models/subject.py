from models import db 
from datetime import datetime

class Subject(db.Model):
    __tablename__ = 'subjects'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)