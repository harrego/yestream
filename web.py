import os
import db

import img

import pytz

from aiohttp import web
from discord.ext import commands, tasks

import jinja2
import aiohttp_jinja2

env = os.environ

HOST="0.0.0.0"
if "HOST" in env:
	HOST=env["HOST"]
PORT=3000
if "PORT" in env:
	PORT=int(env["PORT"])

app = web.Application()
routes = web.RouteTableDef()

STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
app.router.add_static('/static/', STATIC_PATH, name='static')

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")
app.router.add_static('/assets/', ASSETS_PATH, name='assets')

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates")))

def setup(bot, database, twitter_api):
	bot.add_cog(Webserver(bot, database, twitter_api))
	
class Webserver(commands.Cog):
	def __init__(self, bot, database, twitter_api):
		self.bot = bot
		self.web_server.start()
		print("[status][web server] started at " + HOST + ":" + str(PORT))
			
		def parse_db_msgs(database, msg):
			(con, cur) = database
			# format date
			eastern_tz = pytz.timezone("America/New_York")
			
			time = msg["date"].astimezone(eastern_tz)
			msg["date"] = time.strftime("%B %-d, %Y - %-I:%M%p ET")
			
			for tweet in msg["tweets"]:	
				tweet_time = tweet["date"].astimezone(eastern_tz)
				tweet["date"] = tweet_time.strftime("%B %-d, %Y - %-I:%M%p ET")
			
			# format text
			if "text" in msg:
				msg["ping"] = "@everyone" in msg["text"]
			else:
				msg["ping"] = False
				
			# format attachments
			for attachment in msg["attachments"]:
				attachment["url"] = "/static/" + attachment["id"] + "/" + attachment["file_name"]
				(filename, extension) = os.path.splitext(attachment["file_name"])
				extension = extension.lower()
				if extension == ".png" or extension == ".jpg" or extension == ".jpeg" or extension == ".gif":
					attachment["type"] = "img"
				elif extension == ".mp4":
					attachment["type"] = "vid"
				else:
					attachment["type"] = None
					
				if attachment["file_size"]:
					attachment["file_size_human"] = img.human_file_size(attachment["file_size"])
					
			return msg
			
		@routes.get("/")
		async def index(request):
			database = request.app["database"]
			twitter_api = request.app["twitter_api"]
			
			msgs = db.get_msgs(database, twitter_api)
			msgs = map(lambda msg: parse_db_msgs(database, msg), msgs)
		
			context = { "messages": msgs }
			response = aiohttp_jinja2.render_template("index.html", request, context=context)
			return response
		
		app["database"] = database
		app["twitter_api"] = twitter_api
		app.add_routes(routes)
		
	@tasks.loop()
	async def web_server(self):
		runner = web.AppRunner(app)
		await runner.setup()
		site = web.TCPSite(runner, host=HOST, port=PORT)
		await site.start()
		
	@web_server.before_loop
	async def web_server_before_loop(self):
		await self.bot.wait_until_ready()
