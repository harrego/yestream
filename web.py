from aiohttp import web
from discord.ext import commands, tasks

app = web.Application()
routes = web.RouteTableDef()

def setup(bot):
	bot.add_cog(Webserver(bot))
	
class Webserver(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.web_server.start()
			
		@routes.get("/")
		async def index(req):
			return web.Response(text="mule")
			
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
