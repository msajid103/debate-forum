from datetime import datetime
from flask import Flask, render_template, session
from routes.auth import auth
from routes.debate import debate
from controllers.debate import get_claims, get_topics

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Register blueprints with their respective URL prefixes
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(debate, url_prefix='/debate')

@app.template_filter('format_datetime')
def format_datetime(value):
    try:
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return value

@app.route('/')
def index(): 
    topic_details = get_topics()
    claims = get_claims()
    return render_template('home/index.html', topics=topic_details, claims=claims)

@app.route('/contact')
def contact():
    return render_template('home/contact.html')

@app.route('/about')
def about():
    return render_template('home/about.html')

if __name__ == "__main__":
    app.run(debug=True)
