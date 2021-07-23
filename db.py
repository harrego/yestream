import sqlite3
import datetime
import re
import metadata

def connect():
	con = sqlite3.connect("db.sqlite3")
	cur = con.cursor()
	
	cur.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL UNIQUE, date INTEGER NOT NULL, text TEXT, guild_id TEXT NOT NULL, guild_name TEXT NOT NULL, guild_channel TEXT NOT NULL, attachments BOOLEAN NOT NULL, PRIMARY KEY(id))")
	
	# external data
	
	# an attachment is assigned to a message and as such has a message_id foreign key
	cur.execute("CREATE TABLE IF NOT EXISTS attachments (id TEXT NOT NULL UNIQUE, file_name TEXT NOT NULL, message_id TEXT NOT NULL, FOREIGN KEY(message_id) REFERENCES messages(id), PRIMARY KEY(id))")
	# a link is not assigned to a specific message and as such is looked up at random and written into the database on first encounter of a url
	cur.execute("CREATE TABLE IF NOT EXISTS links (url TEXT NOT NULL UNIQUE, date INTEGER NOT NULL, title TEXT, description TEXT)")
	# a tweet is not assigned to a specific message and as such is looked up at random and written into the database on first encounter of a tweet id
	cur.execute("CREATE TABLE IF NOT EXISTS tweets (id TEXT NOT NULL UNIQUE, date INTEGER NOT NULL, text TEXT NOT NULL, username TEXT, name TEXT)")
	
	return (con, cur)
	
def close(db):
	(con, cur) = db
	con.close()
	
def write_msg(db, id, date, text, guild_id, guild_name, guild_channel, attachments):
	(con, cur) = db
	cur.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?)", (id, date, text, guild_id, guild_name, guild_channel, attachments))
	
	con.commit()

def write_attachment(db, id, file_name, message_id):
	(con, cur) = db
	cur.execute("INSERT INTO attachments VALUES (?, ?, ?)", (id, file_name, message_id))
	con.commit()
	
def write_link(db, url, date, title, description):
	(con, cur) = db
	cur.execute("INSERT OR IGNORE INTO links VALUES (?, ?, ?, ?)", (url, date, title, description))
	con.commit()

def write_tweet(db, id, date, text, username, name):
	(con, cur) = db
	cur.execute("INSERT OR IGNORE INTO tweets VALUES (?, ?, ?, ?, ?)", (id, date, text, username, name))
	con.commit()

def get_msgs(db):
	(con, cur) = db
	msgs = []
	for row in con.execute("SELECT id, date, text, guild_name, guild_channel, attachments FROM messages ORDER BY date DESC LIMIT 25"):
		msg = {
			"date": datetime.datetime.fromtimestamp(row[1]),
			"guild": row[3],
			"channel": row[4]
		}
		if row[2]:
			msg["text"] = row[2]
		
		attachments = []
		if row[5]:
			for attachment_row in cur.execute("SELECT id, file_name FROM attachments WHERE message_id=? LIMIT 40", (row[0],)):
				attachments.append({
					"id": attachment_row[0],
					"file_name": attachment_row[1]
				})
		msg["attachments"] = attachments
		
		# (id TEXT NOT NULL NULL UNIQUE, date INTEGER NOT NULL, text TEXT NOT NULL, username TEXT, name TEXT)
		
		tweets = []
		if row[2] != None:
			text = row[2]
			tweet_ids = metadata.tweet_ids_from_str(text)
			for tweet_id in tweet_ids:
				cur.execute("SELECT id, date, text, username, name FROM tweets WHERE id=?", (tweet_id,))
				row = cur.fetchone()
				if row == None:
					continue
				tweets.append({
					"id": row[0],
					"date": datetime.datetime.fromtimestamp(row[1]),
					"text": row[2],
					"username": row[3],
					"name": row[4]
				})
		msg["tweets"] = tweets
		
		msgs.append(msg)
	return msgs
