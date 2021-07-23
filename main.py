import math
import discord
from discord.ext import commands
import os
import db
import img
import web
import re
import time
from datetime import datetime
import math
import metadata

database = db.connect()

env = os.environ

# twitter setup
def twitter_env_setup():
	TWITTER_KEYS = ["TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET", "TWITTER_ACCESS_TOKEN_KEY", "TWITTER_ACCESS_TOKEN_SECRET"]
	args = []
	for KEY in TWITTER_KEYS:
		value = env.get(KEY)
		if value == None:
			return None
		args.append(value)
	return metadata.twitter_setup(*args)
twitter_api = twitter_env_setup()
print(twitter_api)
if twitter_api:
	print("[status][twitter] api enabled")

# bot setup
bot = commands.Bot(command_prefix=".")

DISCORD_TOKEN = env.get("DISCORD_TOKEN")
CHANS = env.get("DISCORD_CHANS")
if CHANS:
	CHANS = list(map(lambda x: int(x), CHANS.split(",")))
else:
	CHANS = []

@bot.event
async def on_ready():
    print("[status][discord] logged in")

@bot.event
async def on_message(message):
	if message.channel.id not in CHANS:
		return

	content = message.content
	attachments = message.attachments
	
	
	message_id = message.id
	message_date = int(message.created_at.timestamp())
	guild_id = str(message.guild.id)
	guild_channel = message.channel.name
	guild_name = message.guild.name

	if len(content) > 0 or len(attachments) > 0:
		if len(content) <= 0:
			content = None
			
		print_content = content
		if print_content == None:
			print_content = "no message content"
		print("[msg][" + guild_id + "] " + print_content)
		if (len(attachments) > 0):
			print("    + " + str(len(attachments)) + " attachments")
		
		db.write_msg(database, message_id, message_date, content, guild_id, guild_name, guild_channel, len(attachments) > 0)
		
		for attachment in attachments:
			(attachment_id, file_name) = img.save(attachment.url)
			db.write_attachment(database, attachment_id, file_name, message_id)
			
		links = re.findall(r'(https?://[^\s]+)', content)
		for link in links:
			# only ignore link if twitter api is active
			if twitter_api:
				twitter_search = re.match(r'(https?:\/\/)?(www.)?twitter.com\/\w+\/status\/[0-9]+', link)
				if twitter_search:
					continue
			(title, description) = metadata.site_metadata(link)
			db.write_link(database, link, int(math.floor(time.time())), title, description)
			
		if twitter_api:
			tweet_ids = metadata.tweet_ids_from_str(content)
			for tweet_id in tweet_ids:
				status = metadata.tweet_metadata(twitter_api, tweet_id)
				if status == None:
					continue
				db.write_raw_tweet(database, status)

web.setup(bot, database, twitter_api)
bot.run(DISCORD_TOKEN)
db.close(database)
