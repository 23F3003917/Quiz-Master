from models import db
from datetime import datetime



class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.now)
    user_answers = db.Column(db.Text, nullable=False) 

    # Relationship
    user = db.relationship('User', backref='attempts')
    quiz = db.relationship('Quiz', backref='attempts')
