from flask import Blueprint, flash, jsonify, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import time

debate = Blueprint('debate', __name__)

def get_db_connection():
    return sqlite3.connect("debate.sqlite")

@debate.route('/create_topic', methods=['GET', 'POST'])
def create_topic():
    if request.method == 'POST':
        topic_name = request.form['topicName'].strip().upper()
        user_id = session.get('user_id')
        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not topic_name:
            flash("Topic name cannot be empty!", "error")
            return redirect(url_for('debate.create_topic'))

        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM topic WHERE topicName = ?", (topic_name,))
            if cursor.fetchone()[0] > 0:
                flash("A topic with this name already exists. Please choose a different name.", "error")
                return redirect(url_for('debate.create_topic'))

            cursor.execute(
                "INSERT INTO topic (topicName, postingUser, creationTime, updateTime) VALUES (?, ?, ?, ?)",
                (topic_name, user_id, creation_time, creation_time)
            )
            db.commit()

        flash("Topic created successfully!", "success")
        return redirect(url_for('index'))

    return render_template('debate/create_topic.html')


@debate.route('/create_claim', methods=['GET', 'POST'])
def create_claim():
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute("SELECT topicID, topicName FROM topic")
        topics = cursor.fetchall()

    if request.method == 'POST':
        claim_text = request.form.get('claim_text', '').strip()
        topic_id = request.form.get('topic_id')
        user_id = session.get('user_id')

        if not claim_text or not topic_id:
            flash('Both claim text and topic must be provided!', "error")
            return redirect(url_for('debate.create_claim'))

        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_db_connection() as db:
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO claim (topic, postingUser, creationTime, updateTime, text) VALUES (?, ?, ?, ?, ?)",
                (topic_id, user_id, creation_time, creation_time, claim_text)
            )
            db.commit()

        flash('Claim successfully created!', "success")
        return redirect(url_for('index'))

    return render_template('debate/create_claim.html', topics=topics)


@debate.route('/claim_detail/<int:claim_id>', methods=['GET'])
def claim_detail(claim_id):
    print('claim-----',claim_id)
    with get_db_connection() as db:
        cursor = db.cursor()

        # Fetch the main claim
        cursor.execute("SELECT * FROM claim WHERE claimID = ?", (claim_id,))
        claim = cursor.fetchone()

        # Handle case where claim is not found
        if not claim:
            flash("Claim not found!", "error")
            return redirect(url_for('debate.index'))

        # Fetch Pro Replies (replyToClaimRelType = 2)
        cursor.execute("""
            SELECT rt.replyTextID, rt.text, rt.creationTime, u.userName
            FROM replyText rt
            JOIN replyToClaim rc ON rt.replyTextID = rc.reply
            JOIN user u ON rt.postingUser = u.userID
            WHERE rc.claim = ? AND rc.replyToClaimRelType = 2
        """, (claim_id,))
        pro_replies = cursor.fetchall()

        # Fetch Con Replies (replyToClaimRelType = 3)
        cursor.execute("""
            SELECT rt.replyTextID, rt.text, rt.creationTime, u.userName
            FROM replyText rt
            JOIN replyToClaim rc ON rt.replyTextID = rc.reply
            JOIN user u ON rt.postingUser = u.userID
            WHERE rc.claim = ? AND rc.replyToClaimRelType = 3
        """, (claim_id,))
        con_replies = cursor.fetchall()

    return render_template(
        'debate/claim_detail.html',
        claim=claim,
        pro_replies=pro_replies,
        con_replies=con_replies
    )


@debate.route('/reply', methods=['POST'])
def add_reply():
    data = request.json
    text = data.get('text')
    claim_id = data.get('claim_id')
    user_id = data.get('user_id')
    reply_type = data.get('reply_type')

    if not all([text, claim_id, user_id, reply_type]):
        return jsonify({'error': 'Missing data'}), 400

    creation_time = int(time.time())
    with get_db_connection() as db:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO replyText (postingUser, creationTime, text) VALUES (?, ?, ?)",
            (user_id, creation_time, text)
        )
        reply_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO replyToClaim (reply, claim, replyToClaimRelType) VALUES (?, ?, ?)",
            (reply_id, claim_id, reply_type)
        )
        db.commit()

    return jsonify({'success': 'Reply added successfully'})

@debate.route('/claim/<int:claim_id>', methods=['GET'])
def get_claim_details(claim_id):
    with sqlite3.connect("debate.sqlite") as db:
        db.row_factory = sqlite3.Row
        cursor = db.cursor()

        # Fetch the claim
        claim = cursor.execute("SELECT * FROM claim WHERE claimID = ?", (claim_id,)).fetchone()
        if not claim:
            return jsonify({'error': 'Claim not found'}), 404

        # Fetch pro replies
        pro_replies = cursor.execute(
            "SELECT rt.replyTextID, rt.text, rt.creationTime, u.userName "
            "FROM replyText rt "
            "JOIN replyToClaim rc ON rt.replyTextID = rc.reply "
            "JOIN user u ON rt.postingUser = u.userID "
            "WHERE rc.claim = ? AND rc.replyToClaimRelType = 2", (claim_id,)
        ).fetchall()

        # Fetch con replies
        con_replies = cursor.execute(
            "SELECT rt.replyTextID, rt.text, rt.creationTime, u.userName "
            "FROM replyText rt "
            "JOIN replyToClaim rc ON rt.replyTextID = rc.reply "
            "JOIN user u ON rt.postingUser = u.userID "
            "WHERE rc.claim = ? AND rc.replyToClaimRelType = 3", (claim_id,)
        ).fetchall()

    return jsonify({
        'claim': dict(claim),
        'pro_replies': [dict(reply) for reply in pro_replies],
        'con_replies': [dict(reply) for reply in con_replies]
    })

