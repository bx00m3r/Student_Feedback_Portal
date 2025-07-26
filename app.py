from flask import Flask, render_template, request, redirect, url_for, session, flash, request as flask_request
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

# Use DATABASE_URL from environment or fallback to SQLite for local dev
db_url = os.environ.get('DATABASE_URL', 'sqlite:///feedback.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(50), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    success = None
    error = None
    categories = ['Facility', 'Teacher', 'Other']
    facility_options = ['Library', 'Canteen', 'Hostel', 'Lab', 'Sports Complex', 'Other Facility']
    teacher_options = ['Prof. A', 'Prof. B', 'Prof. C', 'Prof. D']
    if request.method == 'POST':
        name = request.form.get('student_name', '').strip()
        roll_no = request.form.get('roll_no', '').strip()
        branch = request.form.get('branch', '').strip()
        semester = request.form.get('semester', '').strip()
        category = request.form['category']
        sub_category = request.form.get('sub_category', '')
        rating = request.form['rating']
        feedback = request.form['feedback_text']
        import re
        if not name or not roll_no or not branch or not semester:
            error = 'All fields (Name, Roll No, Branch, Semester) are required.'
        elif not re.match(r'^[A-Za-z0-9\-]+$', roll_no):
            error = 'Roll Number must be alphanumeric.'
        elif not semester.isdigit() or int(semester) <= 0:
            error = 'Semester must be a positive integer.'
        elif not branch:
            error = 'Branch is required.'
        if error:
            return render_template('index.html', error=error, success=None, categories=categories, facility_options=facility_options, teacher_options=teacher_options)
        fb = Feedback(
            student_name=name,
            roll_no=roll_no,
            branch=branch,
            semester=semester,
            category=category,
            sub_category=sub_category,
            rating=int(rating),
            feedback_text=feedback
        )
        db.session.add(fb)
        db.session.commit()
        return redirect(url_for('index', success=1))
    if flask_request.args.get('success') == '1':
        success = 'Thank you for your feedback!'
    return render_template('index.html', success=success, error=error, categories=categories, facility_options=facility_options, teacher_options=teacher_options)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('admin.html', feedbacks=[(
        fb.student_name, fb.roll_no, fb.branch, fb.semester, fb.category, fb.sub_category, fb.rating, fb.feedback_text, fb.timestamp
    ) for fb in feedbacks])

@app.route('/clear_feedback')
def clear_feedback():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    Feedback.query.delete()
    db.session.commit()
    return 'All feedback entries deleted. Remove this route from app.py after use!'

if __name__ == '__main__':
    app.run(debug=True) 