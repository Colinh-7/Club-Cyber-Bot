from discord.ext import commands, tasks
import discord
from includes import rootme_scrapper as rootme
from includes.user import User

intents = discord.Intents.default()
intents.message_content = True

class CyberBot(commands.Bot):

    def __init__(self, rootme_token):
        super().__init__(command_prefix="!", intents=intents)
        self.user_data = {}  # Simple dict for user storage
        self.challenge_tasks = {}  # Tasks for the weeklys
        self.rootme_token = rootme_token

    async def setup_hook(self):
        await self.load_extension("cogs.club")
        await self.load_extension("cogs.challenges")
        await self.load_extension("cogs.user_info")

    async def on_ready(self):
        await self.reload_rootme()

    async def reload_rootme(self):
        self.user_data = {}
        user_names = await rootme.csv_parsing('data/club.csv')

        for name in user_names:
            self.user_data[name] = User(name, self)

    @tasks.loop(minutes=10)
    async def periodic_reload_rootme(self):
        await self.reload_rootme()

    @periodic_reload_rootme.before_loop
    async def before_reload(self):
        await self.wait_until_ready()