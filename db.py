import sqlite3

def connect():
	con = sqlite3.connect("db.sqlite3")
	cur = con.cursor()
	
	cur.execute("CREATE TABLE IF NOT EXISTS messages (id TEXT NOT NULL UNIQUE, content TEXT, guild_id TEXT NOT NULL, guild_name TEXT NOT NULL, attachments BOOLEAN NOT NULL, PRIMARY KEY(id))")
	cur.execute("CREATE TABLE IF NOT EXISTS attachments (id TEXT NOT NULL UNIQUE, file_name TEXT NOT NULL, message_id TEXT NOT NULL, FOREIGN KEY(message_id) REFERENCES messages(id), PRIMARY KEY(id))")
	
	return (con, cur)
	
def close(db):
	(con, cur) = db
	con.close()
	
def write_msg(db, id, content, guild_id, guild_name, attachments):
	(con, cur) = db
	cur.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?)", (id, content, guild_id, guild_name, attachments))
	
	con.commit()

def write_attachment(db, id, file_name, message_id):
	(con, cur) = db
	cur.execute("INSERT INTO attachments VALUES (?, ?, ?)", (id, file_name, message_id))
	con.commit()

