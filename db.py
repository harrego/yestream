import sqlite3

def connect():
	con = sqlite3.connect("../db.sqlite3")
	cur = con.cursor()
	
	cur.execute("CREATE TABLE IF NOT EXISTS messages (id text, content text, guild_id text, guild_name text)")
	cur.execute("CREATE TABLE IF NOT EXISTS attachments (id text, file_name text, message_id text, FOREIGN KEY(message_id) REFERENCES messages(id))")
	
	return (con, cur)
	
def close(db):
	(con, cur) = db
	con.close()
	
def write_msg(db, id, content, guild_id, guild_name):
	(con, cur) = db
	cur.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (id, content, guild_id, guild_name))	
	
	con.commit()

def write_attachment(db, id, file_name, message_id):
	(con, cur) = db
	cur.execute("INSERT INTO attachments VALUES (?, ?, ?)", (id, file_name, message_id))
	con.commit()

