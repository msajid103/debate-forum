import sqlite3

db = sqlite3.connect("debate.sqlite")
cursor = db.cursor()
with open("5013dbinit.sql", "r") as f:
    cursor.executescript(f.read())
db.commit()
db.close()
