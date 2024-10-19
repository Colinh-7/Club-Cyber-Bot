import includes.rootme_scrapper as scrapper
import asyncio, discord
from urllib.request import HTTPError

LOGS_CHANNEL = 1296481389209714785

class User:
    def __init__(self, name, bot):
        self.name = name
        self.stats = {}
        self.challenges = []
        self.bot = bot
        asyncio.create_task(self.load_user_data())

    async def load_user_data(self):
        await self.bot.wait_until_ready() # Wait for the bot to be ready
        self.logs_channel = self.bot.get_channel(LOGS_CHANNEL)

        while True:
            try:
                user_response = scrapper.https_request(self.name)
                self.stats = scrapper.get_user_stats(user_response)
                self.challenges = scrapper.get_last_challenges(user_response)
                self.challenges = scrapper.normalize_challenges(self.challenges)

                embed = discord.Embed(
                    title=f"Root Me LOGS",
                    description=f"Chargement des données de **{self.name}** réussi.",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Club Cyber Bot - Logs")
                await self.logs_channel.send(embed=embed, delete_after=30)

                break 

            except HTTPError as e:
                self.stats = {}
                self.challenges = []

                if self.logs_channel:
                    embed = discord.Embed(
                        title=f"Root Me LOGS",
                        description=f"Erreur lors de la récupération des données pour l'utilisateur **{self.name}**.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Erreur", value=str(e), inline=False)
                    embed.set_footer(text="Club Cyber Bot - Logs")

                    await self.logs_channel.send(embed=embed, delete_after=30)

                await asyncio.sleep(2)

    async def get_name(self):
        return self.name

    async def get_stats(self):
        return self.stats

    async def get_last_challenges(self):
        return self.challenges

    async def __repr__(self):
        return f"{self.name} : {self.stats}, {self.challenges}"