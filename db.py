import sqlite3
import datetime
import re
import metadata
import html

DATABASE_VERSION = 1

def connect():
	con = sqlite3.connect("db.sqlite3")
	cur = con.cursor()
	
	cur.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL UNIQUE, date INTEGER NOT NULL, text TEXT, guild_name TEXT NOT NULL, guild_channel TEXT NOT NULL, attachments BOOLEAN NOT NULL, PRIMARY KEY(id))")
	
	# external data
	
	# an attachment is assigned to a message and as such has a message_id foreign key
	cur.execute("CREATE TABLE IF NOT EXISTS attachments (id TEXT NOT NULL UNIQUE, file_name TEXT NOT NULL, file_size INTEGER, message_id TEXT NOT NULL, FOREIGN KEY(message_id) REFERENCES messages(id), PRIMARY KEY(id))")
	# a link is not assigned to a specific message and as such is looked up at random and written into the database on first encounter of a url
	cur.execute("CREATE TABLE IF NOT EXISTS links (url TEXT NOT NULL UNIQUE, date INTEGER NOT NULL, title TEXT, description TEXT)")
	# a tweet is not assigned to a specific message and as such is looked up at random and written into the database on first encounter of a tweet id
	cur.execute("CREATE TABLE IF NOT EXISTS tweets (id TEXT NOT NULL UNIQUE, date INTEGER NOT NULL, text TEXT NOT NULL, username TEXT, name TEXT)")
	
	# keeping track of the database versions, the highest value in the table should be considered the current version, used for migrations and debugging
	cur.execute("CREATE TABLE IF NOT EXISTS info (db_version INTEGER NOT NULL UNIQUE)")
	cur.execute("INSERT OR REPLACE INTO info VALUES(?)", (DATABASE_VERSION,))
	
	con.commit()
	
	return (con, cur)
	
def close(db):
	(con, cur) = db
	con.close()
	
def write_msg(db, id, date, text, guild_name, guild_channel, attachments):
	(con, cur) = db
	cur.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)", (id, date, text, guild_name, guild_channel, attachments))
	
	con.commit()

def write_attachment(db, id, file_name, file_size, message_id):
	(con, cur) = db
	cur.execute("INSERT INTO attachments VALUES (?, ?, ?, ?)", (id, file_name, file_size, message_id))
	con.commit()
	
def write_link(db, url, date, title, description):
	(con, cur) = db
	cur.execute("INSERT OR REPLACE INTO links VALUES (?, ?, ?, ?)", (url, date, title, description))
	con.commit()

def write_tweet(db, id, date, text, username, name):
	(con, cur) = db
	cur.execute("INSERT OR IGNORE INTO tweets VALUES (?, ?, ?, ?, ?)", (id, date, text, username, name))
	con.commit()
	
def write_raw_tweet(db, status):
	(con, cur) = db
	
	tweet_id = status.id
	tweet_date = status.created_at_in_seconds
	tweet_text = html.unescape(status.text)
	tweet_username = status.user.screen_name
	tweet_name = status.user.name
	write_tweet(db, tweet_id, tweet_date, tweet_text, tweet_username, tweet_name)	

def get_msgs(db, twitter_api=None):
	(con, cur) = db
	msgs = []
	for row in con.execute("SELECT id, date, text, guild_name, guild_channel, attachments FROM messages ORDER BY date DESC LIMIT 150"):
		msg = {
			"date": datetime.datetime.fromtimestamp(row[1]),
			"guild": row[3],
			"channel": row[4]
		}
		if row[2]:
			msg["text"] = row[2]
		
		attachments = []
		if row[5]:
			for attachment_row in cur.execute("SELECT id, file_name, file_size FROM attachments WHERE message_id=? LIMIT 40", (row[0],)):
				attachments.append({
					"id": attachment_row[0],
					"file_name": attachment_row[1],
					"file_size": attachment_row[2]
				})
		msg["attachments"] = attachments
		
		# (id TEXT NOT NULL NULL UNIQUE, date INTEGER NOT NULL, text TEXT NOT NULL, username TEXT, name TEXT)
		
		links = []
		if "text" in msg:
			found_links = re.findall(r'(https?://[^\s]+)', msg["text"])
			for url in found_links:
				cur.execute("SELECT title, description FROM links WHERE url=?", (url,))
				link_row = cur.fetchone()
				if link_row:
					link_data = {}
					if link_row[0]:
						link_data["title"] = link_row[0]
					if link_row[1]:
						link_data["description"] = link_row[1]
					if link_row[0] or link_row[1]:	
						links.append(link_data)
		msg["links"] = links
		
		tweets = []
		if row[2] != None:
			text = row[2]
			tweet_ids = metadata.tweet_ids_from_str(text)
			for tweet_id in tweet_ids:
				cur.execute("SELECT id, date, text, username, name FROM tweets WHERE id=?", (tweet_id,))
				row = cur.fetchone()
				if row == None:
					if twitter_api:
						status = metadata.tweet_metadata(twitter_api, tweet_id)
						if status:
							write_raw_tweet(db, status)
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
