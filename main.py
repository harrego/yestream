import math
import discord
from discord.ext import commands
import os
import db
import img
import web

database = db.connect()

bot = commands.Bot(command_prefix=".")
env = os.environ

DISCORD_TOKEN = env.get("DISCORD_TOKEN")
CHANS = env.get("DISCORD_CHANS")
if CHANS:
	CHANS = list(map(lambda x: int(x), CHANS.split(",")))
else:
	CHANS = []

print(CHANS)

@bot.event
async def on_ready():
    print("Logged in")

@bot.event
async def on_message(message):
	if message.channel.id not in CHANS:
		return

	content = message.content
	attachments = message.attachments
	
	guild_id = str(message.guild.id)
	guild_name = message.guild.name
	message_id = message.id
	if len(content) > 0 or len(attachments) > 0:
		if len(content) <= 0:
			content = None
			
		print_content = content
		if print_content == None:
			print_content = "no message content"
		print("[msg][" + guild_id + "] " + print_content)
		if (len(attachments) > 0):
			print("    + " + str(len(attachments)) + " attachments")
		
		db.write_msg(database, message_id, content, guild_id, guild_name, len(attachments) > 0)
		
		for attachment in attachments:
			(attachment_id, file_name) = img.save(attachment.url)
			db.write_attachment(database, attachment_id, file_name, message_id)

web.setup(bot)
bot.run(DISCORD_TOKEN)
db.close(database)
