from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("debate.sqlite") as db:
            cursor = db.cursor()
            cursor.execute("SELECT userID, passwordHash FROM user WHERE userName = ?", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user[1], password):
                # Update the lastVisit field to the current timestamp
                cursor.execute(
                    "UPDATE user SET lastVisit = CURRENT_TIMESTAMP WHERE userID = ?",
                    (user[0],)
                )
                db.commit()

                # Store the user ID in the session
                session['user_id'] = user[0]
                return redirect(url_for('index'))
            else:
                return "Invalid credentials, please try again."

    return render_template('auth/login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Get the current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect("debate.sqlite") as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO user (username, passwordHash, isAdmin, creationTime, lastVisit) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_password, 0, current_time, current_time)  # 0 for False (not admin)
            )
            db.commit()

        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')


@auth.route('/logout')
def logout():
    # Clear the session to log out the user
    session.pop('user_id', None)  # Remove user_id from session
    return redirect(url_for('index'))  # Redirect to the home page after logging out
