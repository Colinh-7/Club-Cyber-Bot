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
        await self.reload_rootme.start() # Start the tasks loop

    @tasks.loop(minutes=10)
    async def reload_rootme(self):
        self.user_data = {}
        user_id = await rootme.csv_parsing('data/club.csv')
        for id in user_id:
            try:
                self.user_data[id] = User(id, self)
            except Exception as e:
                print(f"{id} removed.")