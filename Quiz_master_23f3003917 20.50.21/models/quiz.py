from models import db
from datetime import datetime

class Quiz(db.Model):
    __tablename__ = 'quizzes'  # Ensure table name matches what is referenced
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    time_duration = db.Column(db.String(100), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)  # Ensure correct type
