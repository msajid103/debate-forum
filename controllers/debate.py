import sqlite3
def get_topics():  
        with sqlite3.connect("debate.sqlite") as db:
            cursor = db.cursor()     
        cursor.execute("SELECT topicID, topicName FROM topic")
        return cursor.fetchall()
def get_claims():
    with sqlite3.connect("debate.sqlite") as db:
        cursor = db.cursor()

        # Modify the query to join the 'user' table and get the 'username' of the posting user
        cursor.execute("""
                        SELECT 
                            claim.claimID, 
                            claim.text, 
                            user.username, 
                            topic.topicName, -- Get the topic name
                            claim.creationTime, 
                            claim.updateTime
                        FROM claim
                        JOIN user ON claim.postingUser = user.userID  -- Join with 'user' table on postingUser
                        JOIN topic ON claim.topic = topic.topicID  -- Join with 'topic' table on topicID
                        ORDER BY claim.updateTime DESC
                    """)
        
        return cursor.fetchall()
