from models import db
from datetime import datetime



class Score(db.Model):
    __tablename__ = 'scores'  # Define table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Ensure 'users.id' matches `User.__tablename__`
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)