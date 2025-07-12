from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import json
import uuid
from main import rank_resumes_against_job

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Directories
app.config['UPLOAD_FOLDER'] = 'resume_sample'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('Sign-up_details', exist_ok=True)

# Home (protected)
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('signin'))
    return render_template('index.html')

# Sign-Up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if not all([username, email, password, confirm_password]):
            flash('All fields are required.')
            return render_template('sign-up.html')

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template('sign-up.html')

        filepath = os.path.join('Sign-up_details', f'{username}.json')
        if os.path.exists(filepath):
            flash("User already exists. Please sign in.")
            return redirect(url_for('signin'))

        user_data = {
            'username': username,
            'email': email,
            'password': password
        }

        with open(filepath, 'w') as f:
            json.dump(user_data, f)

        flash("Sign-up successful. Please sign in.")
        return redirect(url_for('signin'))

    return render_template('sign-up.html')

# Sign-In
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        filepath = os.path.join('Sign-up_details', f'{username}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                user_data = json.load(f)
                if user_data['password'] == password:
                    session['user'] = username
                    flash("Signed in successfully.")
                    return redirect(url_for('index'))
                else:
                    flash("Incorrect password.")
        else:
            flash("User not found.")
        return render_template('sign-in.html')

    return render_template('sign-in.html')

# Sign-Out
@app.route('/signout')
def signout():
    session.pop('user', None)
    flash("You have been signed out.")
    return redirect(url_for('signin'))

# Upload Resume
@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if 'user' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        if 'resume' not in request.files:
            return "No file part", 400

        file = request.files['resume']
        job_title = request.form.get('job_title')

        if not job_title:
            return "Job title is required.", 400

        if file.filename == '':
            return "No selected file", 400

        if file and file.filename and file.filename.lower().endswith('.pdf'):
            # Use username from session as filename (sanitized)
            username = session['user']
            sanitized_username = "".join(x for x in username if x.isalnum() or x in (' ', '_', '-')).rstrip()
            filename = f"{sanitized_username}.pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            job_skills_csv = "job_skills.csv"
            ranked_resumes = rank_resumes_against_job(job_title, app.config['UPLOAD_FOLDER'], job_skills_csv)
            total_resumes = len(ranked_resumes)

            user_rank = None
            user_score = None
            for idx, (fname, total_score, skill_score, exp_score) in enumerate(ranked_resumes, start=1):
                if fname == filename:
                    user_rank = idx
                    user_score = total_score
                    break

            return render_template('result.html',
                                   filename=filename,
                                   score=user_score,
                                   rank=user_rank,
                                   total=total_resumes,
                                   job_title=job_title)

        return "Invalid file format. Only PDFs are allowed.", 400

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
