from flask import Blueprint, flash, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

debate = Blueprint('debate', __name__)

@debate.route('/create_topic', methods=['GET', 'POST'])
def create_topic():
    if request.method == 'POST':
        topic_name = request.form['topicName']
        user_id = session.get('user_id')
        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Capitalize the first letter and make the rest lowercase
        topic_name = topic_name.strip().capitalize()

        with sqlite3.connect("debate.sqlite") as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM topic WHERE topicName = ?", (topic_name,))
            count = cursor.fetchone()[0]

            if count > 0:
                flash("A topic with this name already exists. Please choose a different name.", "error")
                return redirect(url_for('debate.create_topic'))

            # Insert the new topic into the database
            cursor.execute(
                "INSERT INTO topic (topicName, postingUser, creationTime, updateTime) VALUES (?, ?, ?, ?)",
                (topic_name, user_id, creation_time, creation_time)
            )
            db.commit()

        flash("Topic created successfully!", "success")
        return redirect(url_for('index'))

    return render_template('debate/create_topic.html')
