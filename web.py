import os
import db

import pytz

from aiohttp import web
from discord.ext import commands, tasks

import jinja2
import aiohttp_jinja2

app = web.Application()
routes = web.RouteTableDef()

STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")
app.router.add_static('/static/', STATIC_PATH, name='static')

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(os.path.join(os.getcwd(), "templates")))

def setup(bot, database):
	bot.add_cog(Webserver(bot, database))
	
class Webserver(commands.Cog):
	def __init__(self, bot, database):
		self.bot = bot
		self.web_server.start()
		
		self.database = database
		(con, cur) = database
			
		def parse_db_msgs(msg):
			# format date
			eastern_tz = pytz.timezone("US/Eastern")
			time = msg["date"].astimezone(eastern_tz)
			msg["date"] = time.strftime("%B %-d, %Y - %-I:%M%p %Z")
			
			# format text
			if "text" in msg:
				msg["ping"] = "@everyone" in msg["text"]
			else:
				msg["ping"] = False
				
			# format attachments
			for attachment in msg["attachments"]:
				attachment["url"] = "/static/" + attachment["id"] + "/" + attachment["file_name"]
				(filename, extension) = os.path.splitext(attachment["file_name"])
				if extension == ".png" or extension == ".jpg" or extension == ".jpeg" or extension == ".gif":
					attachment["img"] = True
				else:
					attachment["img"] = False
			return msg
			
		@routes.get("/")
		async def index(request):
			msgs = db.get_msgs(database)
			msgs = map(parse_db_msgs, msgs)
		
			context = { "messages": msgs }
			response = aiohttp_jinja2.render_template("index.html", request, context=context)
			return response
			
		app.add_routes(routes)
		
	@tasks.loop()
	async def web_server(self):
		runner = web.AppRunner(app)
		await runner.setup()
		site = web.TCPSite(runner, host='0.0.0.0', port=3000)
		await site.start()
		
	@web_server.before_loop
	async def web_server_before_loop(self):
		await self.bot.wait_until_ready()
