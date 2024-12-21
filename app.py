from flask import Flask, render_template, session
from routes.auth import auth
from routes.debate import debate
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Register blueprints with their respective URL prefixes
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(debate, url_prefix='/debate')

@app.route('/')
def index():
    # Fetch topics from the database
    with sqlite3.connect("debate.sqlite") as db:
        cursor = db.cursor()
        cursor.execute("SELECT topicName FROM topic")
        topics = cursor.fetchall()

    # Check if the user is logged in
    user_logged_in = 'user_id' in session

    return render_template('home/index.html', topics=topics)

@app.route('/contact')
def contact():
    return render_template('home/contact.html')

@app.route('/about')
def about():
    return render_template('home/about.html')

if __name__ == "__main__":
    app.run(debug=True)
