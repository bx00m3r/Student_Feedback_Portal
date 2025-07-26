from flask import Flask, render_template, request, redirect, url_for, session, flash, request as flask_request
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key
DATABASE = 'feedback.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        feedback_text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def alter_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Add columns if they don't exist
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN category TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN rating INTEGER")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN roll_no TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN branch TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN semester TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE feedback ADD COLUMN sub_category TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

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
        # Backend validation
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
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO feedback (student_name, roll_no, branch, semester, category, sub_category, rating, feedback_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (name, roll_no, branch, semester, category, sub_category, rating, feedback))
        conn.commit()
        conn.close()
        return redirect(url_for('index', success=1))
    # GET request
    if flask_request.args.get('success') == '1':
        success = 'Thank you for your feedback!'
    return render_template('index.html', success=success, error=error, categories=categories, facility_options=facility_options, teacher_options=teacher_options)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hardcoded admin credentials
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
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''SELECT student_name, roll_no, branch, semester, category, sub_category, rating, feedback_text, timestamp FROM feedback ORDER BY timestamp DESC''')
    feedbacks = c.fetchall()
    conn.close()
    return render_template('admin.html', feedbacks=feedbacks)

@app.route('/clear_feedback')
def clear_feedback():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM feedback')
    conn.commit()
    conn.close()
    return 'All feedback entries deleted. Remove this route from app.py after use!'

if __name__ == '__main__':
    init_db()
    alter_db()
    app.run(debug=True) 