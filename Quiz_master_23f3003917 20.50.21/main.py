from flask import Flask, render_template , session, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import os
from datetime import datetime
from sqlalchemy.types import Date
from sqlalchemy import func





app = Flask(__name__, template_folder="templates")


# Configure SQLite database
curr_dir = os.path.dirname(os.path.abspath(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{os.path.join(curr_dir, "db.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "Anirudh"

db = SQLAlchemy(app)







# Models
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


class Subject(db.Model):
    __tablename__ = 'subjects'  # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    chapters = db.relationship('Chapter', backref='subject', lazy=True)


class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    num_questions = db.Column(db.Integer, default=0)  
    quizzes = db.relationship("Quiz", backref="chapter", lazy=True)


class Quiz(db.Model):
    __tablename__ = 'quizzes'  # Ensure table name matches what is referenced
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    time_duration = db.Column(db.String(100), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)  # Ensure correct type



class Question(db.Model):
    __tablename__ = 'questions'  # Explicitly define table name
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)  # Match 'quizzes.id'
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)



class Score(db.Model):
    __tablename__ = 'scores'  # Define table name explicitly
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Ensure 'users.id' matches `User.__tablename__`
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    
    


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

    



#Creating ADmin 
def create_admin():
    with app.app_context():  # Ensure the database operations run within the app context
        # Check if admin already exists
        existing_admin = User.query.filter_by(email="admin123@gmail.com").first()
        if existing_admin:
            print("Admin already exists.")
            return


        # Create an admin user (storing password in plain text)
        admin = User(
            email="admin123@gmail.com",
            password="0000",  # Plain text (Insecure)
            full_name="Master",
            dob=datetime.strptime("2004-12-18", "%Y-%m-%d").date(),
            qualification="BTech",
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")


with app.app_context():
    db.create_all()
    create_admin()   
    
    
    
@app.route("/")    
def index():
    return render_template("index.html")


#Creating Admin Login Route
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        admin_password = request.form.get("admin_password")

        if email == "admin123@gmail.com" and admin_password == "0000":
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid Credentials", "danger")

    return render_template("admin_login.html")



#Creating User registration route
from werkzeug.security import check_password_hash, generate_password_hash

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        qualification = request.form.get("qualification")
        dob = request.form.get("dob")

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered. Please login.", "warning")
            return redirect(url_for("user_login"))

        # Hash the password before saving it
        hashed_password = generate_password_hash(password)

        # Convert DOB string to date format
        if dob:
            try:
                dob = datetime.strptime(dob, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD", "danger")
                return render_template("register.html")

        # Create a new user
        new_user = User(email=email, password=hashed_password, full_name=full_name, qualification=qualification, dob=dob)
        db.session.add(new_user)
        
        try:
            db.session.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("user_login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error occurred: {str(e)}", "danger")

    return render_template("register.html")




from werkzeug.security import check_password_hash, generate_password_hash
#Creating User Login Route

@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # ✅ Store user ID and email in session
            session["user_id"] = user.id  
            session["user"] = user.email  

            flash("Login successful!", "success")
            return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("user_login.html")



#creating admin_dashboard route@app.route("/user_dashboard", methods=["GET", "POST"])
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin_logged_in" not in session:
        flash("Unauthorized access! Please log in as an admin.", "danger")
        return redirect(url_for("admin_login"))

    subjects = Subject.query.all()  # Fetch all subjects from the database
    return render_template("admin_dashboard.html", subjects=subjects)


    
    
    
#Creating User_dashboard route
@app.route("/user_dashboard", methods=["GET"])
def user_dashboard():
    print(session)  # Debugging: Print session to check if user is stored
    user_id = session.get('user_id') 

    if "user" not in session:
        flash("Please login first", "danger")
        return redirect(url_for("user_login"))

    user = User.query.filter_by(email=session["user"]).first()
    subjects = Subject.query.options(db.joinedload(Subject.chapters).joinedload(Chapter.quizzes)).all()
    
    
    if not user:
        session.pop("user", None)  # Clear invalid session
        flash("User not found. Please login again.", "danger")
        return redirect(url_for("user_login"))
    
    
    # ✅ Fetch all quiz attempts for the logged-in user
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()

    # ✅ Create a list of dictionaries for Jinja2 template
    quiz_data = []
    for attempt in attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        subject = Subject.query.get(quiz.chapter.subject_id)
        total_questions = len(quiz.questions)

        # ✅ Determine Status: Passed or Failed
        status = "Passed" if attempt.score >= (total_questions * 0.5) else "Failed"

        # ✅ Append Data
        quiz_data.append({
            'quiz_name': quiz.title,
            'subject_name': subject.name,
            'total_questions': total_questions,
            'score': attempt.score,
            'attempt_date': attempt.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'status': status,
            'quiz_id': attempt.quiz_id
        })

    

    return render_template("user_dashboard.html", user=user, subjects=subjects , quiz_data=quiz_data)





    
# creating route for subject 
@app.route("/create_subject", methods=["GET", "POST"])
def create_subject():

    if request.method == "GET":
        return render_template('create_subject.html')

    if request.method == "POST":
        name = request.form.get("subject")
        description = request.form.get("description")

        if not name or not description:
            flash("All fields are required!", "danger")
            return redirect(url_for("create_subject"))

        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()

        flash("Subject created successfully", "success")
        return redirect(url_for("admin_dashboard"))  # 🚀 Redirect to admin panel after creation
    
    
#Creating route for edit subject
@app.route("/edit_subject/<int:subject_id>", methods=["GET", "POST"])
def edit_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        name = request.form.get("subject")
        description = request.form.get("description")

        if not name or not description:
            flash("All fields are required!", "danger")
            return redirect(url_for("edit_subject", subject_id=subject_id))

        subject.name = name
        subject.description = description
        db.session.commit()

        flash("Subject updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_subject.html", subject=subject)    


#Creating route for delete subject
@app.route("/delete_subject/<int:subject_id>", methods=["POST"])
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    db.session.delete(subject)
    db.session.commit()

    flash("Subject deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))
    
    # Creating route for chapter
    
    
@app.route("/<int:subject_id>/create_chapter", methods=["GET", "POST"])
def create_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        name = request.form.get("name")

        if not name:
            flash("Chapter name is required!", "danger")
            return redirect(url_for("create_chapter", subject_id=subject_id))

        new_chapter = Chapter(name=name, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()

        flash("Chapter created successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("create_chapter.html", subject=subject)   





#Creating route for edit chapter
@app.route("/edit_chapter/<int:subject_id>", methods=["GET", "POST"])
def edit_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        chapter_id = request.form.get("chapter_id")
        name = request.form.get("name")

        if not chapter_id or not name:
            flash("All fields are required!", "danger")
            return redirect(url_for("edit_chapter", subject_id=subject_id))

        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found!", "danger")
            return redirect(url_for("edit_chapter", subject_id=subject_id))

        chapter.name = name
        db.session.commit()

        flash("Chapter updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_chapter.html", subject=subject)



#Creating route for deleting chapter
@app.route("/delete_chapter/<int:chapter_id>", methods=["POST"])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash("Chapter not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))


#Creating route for view chapter
@app.route("/view_chapter/<int:chapter_id>")
def view_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    return render_template("view_chapter.html", chapter=chapter)

#Creating route for quiz

from datetime import datetime

@app.route("/<int:chapter_id>/create_quiz", methods=["GET", "POST"])
def create_quiz(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if not chapter:
        flash("Chapter not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        time_duration = request.form.get("time_duration")
        date_of_quiz_str = request.form.get("date_of_quiz")  # Get date as string

        # Convert string to Python date object
        try:
            date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format!", "danger")
            return redirect(url_for("create_quiz", chapter_id=chapter_id))

        new_quiz = Quiz(
            title=title,
            description=description,
            time_duration=time_duration,
            date_of_quiz=date_of_quiz,  # Store as date object
            chapter_id=chapter_id
        )
        db.session.add(new_quiz)
        db.session.commit()

        flash("Quiz created successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("create_quiz.html", chapter=chapter)



#Creating route fot edit quiz
@app.route("/edit_quiz/<int:quiz_id>", methods=["GET", "POST"])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash("Quiz not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        time_duration = request.form.get("time_duration")

        quiz.title = title
        quiz.description = description
        quiz.time_duration = time_duration
        db.session.commit()

        flash("Quiz updated successfully!", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_quiz.html", quiz=quiz) 


#Creating route for delete quiz
@app.route("/delete_quiz/<int:quiz_id>", methods=["POST"])  
def delete_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        flash("Quiz not found!", "danger")
        return redirect(url_for("admin_dashboard"))

    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for("admin_dashboard"))

#Creating route for view quiz
@app.route("/view_quiz/<int:quiz_id>")
def view_quiz(quiz_id):     
    quiz = Quiz.query.get(quiz_id)
    return render_template("view_quiz.html", quiz=quiz) 


# Create Question Route
@app.route("/<int:quiz_id>/create_question", methods=["GET", "POST"])
def create_question(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        
        if request.method == "POST":
            new_question = Question(
                quiz_id=quiz_id,
                question_text=request.form["question_text"],
                option_a=request.form["option_a"],
                option_b=request.form["option_b"],
                option_c=request.form["option_c"],
                option_d=request.form["option_d"],
                correct_option=request.form["correct_option"]
            )
            
            db.session.add(new_question)
            db.session.commit()
            flash("Question added successfully!", "success")
            return redirect(url_for("view_quiz", quiz_id=quiz_id))
        
        return render_template("create_question.html", quiz=quiz)
                    
    except Exception as e:
        db.session.rollback()
        flash(f"Error creating question: {str(e)}", "danger")
        return redirect(url_for("view_quiz", quiz_id=quiz_id))


# Delete Question Route
@app.route("/delete_question/<int:question_id>", methods=["POST"])
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        quiz_id = question.quiz_id
        
        db.session.delete(question)
        db.session.commit()
        
        flash("Question deleted successfully!", "success")
        return redirect(url_for("view_quiz", quiz_id=quiz_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting question: {str(e)}", "danger")
        return redirect(url_for("view_quiz", quiz_id=quiz_id))


# Edit Question Route
@app.route("/edit_question/<int:question_id>", methods=["GET", "POST"])
def edit_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        
        if request.method == "POST":
            question.question_text = request.form["question_text"]
            question.option_a = request.form["option_a"]
            question.option_b = request.form["option_b"]
            question.option_c = request.form["option_c"]
            question.option_d = request.form["option_d"]
            question.correct_option = request.form["correct_option"]
            
            db.session.commit()
            flash("Question updated successfully!", "success")
            return redirect(url_for("view_quiz", quiz_id=question.quiz_id))
        
        return render_template("edit_question.html", question=question)

    except Exception as e:
        db.session.rollback()
        flash(f"Error updating question: {str(e)}", "danger")
        return redirect(url_for("view_quiz", quiz_id=question.quiz_id))
    
    
# # View Question Route
# @app.route("/view_question/<int:question_id>", methods=["GET"])
# def view_question(question_id):
#     try:
#         question = Question.query.get_or_404(question_id)
#         return render_template("view_question.html", question=question)
#     except Exception as e:
#         flash(f"Error viewing question: {str(e)}", "danger")
#         return redirect(url_for("admin_dashboard"))


#Admin in session route 

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin_logged_in" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

#user in session route
from functools import wraps
def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_logged_in" not in session:
            return redirect(url_for("user_login"))
        return f(*args, **kwargs)
    return decorated_function

#Admin Summary Route
import json
import plotly.express as px
import plotly.io as pio  # Correct import

@app.route("/admin_summary")
@admin_required
def admin_summary():
    total_users = User.query.count()
    total_subject = Subject.query.count()
    total_scores = Score.query.count()
    subjects = Subject.query.all()
    total_quizzes = 0
    quiz_count_dict = {}

    # Collect quiz count per subject
    for subject in subjects:
        quiz_count = sum(len(chapter.quizzes) for chapter in subject.chapters)
        quiz_count_dict[subject.name] = quiz_count
        total_quizzes += quiz_count

    # Create a bar chart using Plotly
    fig = px.bar(
        x=list(quiz_count_dict.keys()),
        y=list(quiz_count_dict.values()),
        labels={"x": "Subjects", "y": "Total Quizzes"},
        title="Quizzes per Subject",
        text_auto=True,
    )

    fig.update_layout(xaxis_title="Subjects", yaxis_title="Quiz Count")

    # ✅ Correct JSON encoding using `pio.to_json(fig)`
    graph_json = pio.to_json(fig)

    return render_template(
        "admin_summary.html",
        total_users=total_users,
        total_subject=total_subject,
        total_scores=total_scores,
        total_quizzes=total_quizzes,
        graph_json=graph_json
    )
 



#Creating admin_search route
@app.route("/admin_search", methods=["GET"])
@admin_required
def admin_search():
    search_query = request.args.get("q", "").strip()  # Get query parameter & remove spaces

    # If no query parameter was provided at all, just render the template
    if "q" not in request.args:
        return render_template("admin_search.html", users=[], subjects=[], chapters=[], quizzes=[], search_query="")

    # Only perform search if the query is not empty
    if search_query:
        users = User.query.filter(User.full_name.ilike(f"%{search_query}%")).all()
        subjects = Subject.query.filter(Subject.name.ilike(f"%{search_query}%")).all()
        chapters = Chapter.query.options(joinedload(Chapter.subject)).filter(Chapter.name.ilike(f"%{search_query}%")).all()
        quizzes = Quiz.query.options(joinedload(Quiz.chapter)).filter(Quiz.title.ilike(f"%{search_query}%")).all()
    else:
        users = subjects = chapters = quizzes = []  # Empty results for empty search

    return render_template(
        "admin_search.html",
        users=users,
        subjects=subjects,
        chapters=chapters,
        quizzes=quizzes,
        search_query=search_query   
    )
    
    
 
 



#Creating route for attempt quiz
@app.route('/attempt_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def attempt_quiz(quiz_id):
    
    current_user_id = session.get('user_id')  # Fetch from session
        
    # Fetch the quiz and its questions
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    if request.method == 'POST':
        # Capture User's Answers
        total_questions = len(questions)
        correct_option = 0
        
        # Loop through all questions
        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            
            # Check if the answer is correct
            if selected_option:
                if selected_option == question.correct_option:
                    correct_option += 1
        
        # Calculate score
        score = round((correct_option / total_questions) * 100, 2)

        # Save the attempt in database
        attempt = AttemptedQuiz(
            user_id=current_user_id,
            quiz_id=quiz.id,
            score=score
        )
        db.session.add(attempt)
        db.session.commit()

        # Redirect to result page
        flash(f'You scored {score}% in the quiz "{quiz.title}"', 'success')
        return redirect(url_for('quiz_result', attempt_id=attempt.id))

    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)







#Creating route for submit quiz
@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    
    
    current_user_id = session.get('user_id')  # Fetch from session
    
    
    # Fetch the quiz and questions from database
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    # Track user's answers and calculate score
    user_answers = {}  # To store user's answers
    total_score = 0
    total_questions = len(questions)

    # Iterate through all questions and check answers
    for question in questions:
        selected_option = request.form.get(f'question_{question.id}')  # Get selected option

        # Store the user's selected answer
        user_answers[question.id] = selected_option

        # Check if the answer is correct
        if selected_option == question.correct_option:
            total_score += 1

    # Calculate percentage
    percentage_score = (total_score / total_questions) * 100

    # Save the quiz attempt in the database
    quiz_attempt = QuizAttempt(
        user_id=current_user_id,
        quiz_id=quiz.id,
        score=total_score,
        user_answers=json.dumps(user_answers),  # Convert dict to JSON string
        submitted_at=datetime.utcnow()
    )
    db.session.add(quiz_attempt)
    db.session.commit()

    # Flash success message
    flash('✅ Quiz submitted successfully!', 'success')

    # Redirect to result page
    return redirect(url_for('quiz_result', quiz_id=quiz.id, attempt_id=quiz_attempt.id))






# Creating route for quiz result
@app.route('/quiz_result/<int:quiz_id>', methods=['GET'])
def quiz_result(quiz_id):
    # ✅ Step 1: Fetch user_id from session
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view quiz results.', 'danger')
        return redirect(url_for('login'))

    # ✅ Step 2: Fetch the latest quiz attempt for this user and quiz
    attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id).order_by(QuizAttempt.submitted_at.desc()).first()

    # ✅ Step 3: Check if the user has even attempted the quiz
    if not attempt:
        flash('You have not attempted this quiz yet.', 'danger')
        return redirect(url_for('user_dashboard'))

    # ✅ Step 4: Render the result page with score
    return render_template('quiz_result.html', attempt=attempt)





 

 #User Summary Route
import json
import plotly.express as px
import plotly.io as pio  # Correct import

@app.route("/user_summary")
def user_summary():
    # ✅ Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view your summary.', 'danger')
        return redirect(url_for('login'))

    # ✅ Fetch All Attempted Quizzes by User
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    total_attempted_quizzes = len(attempts)
    total_score = sum(attempt.score for attempt in attempts)

    # ✅ Prepare Subject-Wise Data
    subject_attempts = {}
    for attempt in attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        subject_name = quiz.chapter.subject.name

        if subject_name in subject_attempts:
            subject_attempts[subject_name] += 1
        else:
            subject_attempts[subject_name] = 1

    # ✅ Create Bar Chart Using Plotly
    fig = px.bar(
        x=list(subject_attempts.keys()),
        y=list(subject_attempts.values()),
        labels={"x": "Subjects", "y": "Quizzes Attempted"},
        title="Quizzes Attempted Per Subject",
        text_auto=True,
        color=list(subject_attempts.keys())
    )

    fig.update_layout(
        xaxis_title="Subjects",
        yaxis_title="Number of Quizzes Attempted",
        title_x=0.5
    )

    # ✅ Convert Plotly Chart to JSON
    graph_json = pio.to_json(fig)

    # ✅ Render Template
    return render_template(
        "user_summary.html",
        total_attempted_quizzes=total_attempted_quizzes,
        total_score=total_score,
        graph_json=graph_json
    )





#Creating route for user_logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('index'))



#creating route for user_profile
@app.route('/user_profile')
def user_profile():
    # ✅ Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view your profile.', 'danger')
        return redirect(url_for('user_login'))
    
    # ✅ Fetch User Details
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('user_login'))
    
    # ✅ Render User Profile Template
    return render_template('user_profile.html', user=user)




#Creating route for edit_profile
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # ✅ Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to edit your profile.', 'danger')
        return redirect(url_for('login'))

    # ✅ Fetch User from Database
    user = User.query.get(user_id)

    if request.method == 'POST':
        # ✅ Update User Details
        user.full_name = request.form['full_name']
        user.dob = datetime.strptime(request.form['dob'], '%Y-%m-%d').date()
        user.qualification = request.form['qualification']
        user.email = request.form['email']

        # ✅ Handle Profile Picture Upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                user.profile_picture = f'static/profile_pics/{filename}'

        # ✅ Update Password (if provided)
        new_password = request.form.get('password')
        if new_password:
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password

        # ✅ Commit Changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))

    # ✅ Render Edit Profile Page
    return render_template('edit_profile.html', user=user)




#Creating route for search
@app.route('/search', methods=['POST'])
def search():
    # ✅ Get Search Query
    search_query = request.form.get('search_query').lower()

    # ✅ Fetch All Quizzes that Match Search Query
    quizzes = Quiz.query.join(Chapter).join(Subject).filter(
        (func.lower(Quiz.title).like(f'%{search_query}%')) |
        (func.lower(Chapter.name).like(f'%{search_query}%')) |
        (func.lower(Subject.name).like(f'%{search_query}%'))
    ).all()

    # ✅ Check Which Quiz Is Attempted By User
    user_id = session.get('user_id')
    attempted_quizzes = QuizAttempt.query.filter_by(user_id=user_id).all()
    attempted_quiz_ids = [attempt.quiz_id for attempt in attempted_quizzes]

    # ✅ Pass Data to Template
    return render_template('search_result.html', 
                           quizzes=quizzes, 
                           attempted_quiz_ids=attempted_quiz_ids)
    
    
   
   
   
#Creating route for user_view_quiz 
@app.route('/user_view_quiz/<int:quiz_id>')
def user_view_quiz(quiz_id):
    # ✅ Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view the quiz.', 'danger')
        return redirect(url_for('login'))

    # ✅ Fetch Quiz Details
    quiz = Quiz.query.get_or_404(quiz_id)

    # ✅ Check if User Has Attempted the Quiz
    attempt = QuizAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()

    # ✅ Determine Status
    if attempt:
        status = 'Attempted'
        button_text = 'View Result'
        button_link = url_for('quiz_result', quiz_id=quiz_id)
    else:
        status = 'Not Attempted'
        button_text = 'Attempt Quiz'
        button_link = url_for('attempt_quiz', quiz_id=quiz_id)

    # ✅ Render Template
    return render_template('user_view_quiz.html', quiz=quiz, status=status, button_text=button_text, button_link=button_link)














if __name__ == "__main__":
    app.run(debug=True, port=5005)
    
