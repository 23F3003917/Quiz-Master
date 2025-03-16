from models import db 
from datetime import datetime


class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    num_questions = db.Column(db.Integer, default=0)  
    quizzes = db.relationship("Quiz", backref="chapter", lazy=True)