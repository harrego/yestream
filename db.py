import sqlite3
import datetime

def connect():
	con = sqlite3.connect("db.sqlite3")
	cur = con.cursor()
	
	cur.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL UNIQUE, date INTEGER NOT NULL, text TEXT, guild_id TEXT NOT NULL, guild_name TEXT NOT NULL, guild_channel TEXT NOT NULL, attachments BOOLEAN NOT NULL, PRIMARY KEY(id))")
	cur.execute("CREATE TABLE IF NOT EXISTS attachments (id TEXT NOT NULL UNIQUE, file_name TEXT NOT NULL, message_id TEXT NOT NULL, FOREIGN KEY(message_id) REFERENCES messages(id), PRIMARY KEY(id))")
	
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
		msgs.append(msg)
	return msgs
