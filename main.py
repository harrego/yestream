import math
import discord
import os
import db
import img

database = db.connect()

client = discord.Client()
env = os.environ

DISCORD_TOKEN = env.get("DISCORD_TOKEN")
CHANS = env.get("DISCORD_CHANS")
if CHANS:
	CHANS = list(map(lambda x: int(x), CHANS.split(",")))
else:
	CHANS = []

print(CHANS)

@client.event
async def on_ready():
    print("Logged in")

@client.event
async def on_message(message):
	if message.channel.id not in CHANS:
		return

	content = message.content
	attachments = message.attachments
	
	guild_id = str(message.guild.id)
	guild_name = message.guild.name
	message_id = message.id
	if len(content) > 0 or len(attachments) > 0:
		print("[msg][" + guild_id + "] " + content)
		#if (len(attachments) > 0):
		#	print("    + " + str(len(attachments) + " attachments")
			
		db.write_msg(database, message_id, content, guild_id, guild_name)
		
		for attachment in attachments:
			(attachment_id, file_name) = img.save(attachment.url)
			db.write_attachment(database, attachment_id, file_name, message_id)

client.run(DISCORD_TOKEN)
db.close(database)
