import includes.rootme_scrapper as rootme
import asyncio, discord
from urllib.request import HTTPError

LOGS_CHANNEL = 1296481389209714785
DELETE_TIME = 600
semaphore = asyncio.Semaphore(1)

class User:
    def __init__(self, name, bot):
        self.name = name
        self.data = {}
        self.challenges = []
        self.bot = bot
        asyncio.create_task(self.load_user_data())

    async def load_user_data(self):
        await self.bot.wait_until_ready() # Wait for the bot to be ready
        self.logs_channel = self.bot.get_channel(LOGS_CHANNEL)
        attempt = 0
        
        while attempt < 5:
            try:
                async with semaphore :
                    user_info = await rootme.get_auteur_info(self.name, self.bot.rootme_token)
                self.challenges = user_info.pop("validations")
                self.data = user_info
                embed = discord.Embed(
                    title=f"Root Me LOGS",
                    description=f"Chargement des données de **{self.name}** réussi.",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=f"https://www.root-me.org/{self.data["logo_url"]}")
                embed.set_footer(text="Club Cyber Bot - Logs", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")

                #print(f"{self.name}'s data : LOADED.")
                await self.logs_channel.send(embed=embed, delete_after=DELETE_TIME)

                break 

            except HTTPError as e:
                self.challenges = {}
                self.data = {"score":-1}
                if self.logs_channel:
                    embed = discord.Embed(
                        title=f"Root Me LOGS",
                        description=f"Erreur lors de la récupération des données pour l'utilisateur **{self.name}**.",
                        color=discord.Color.red()
                    )
                    embed.add_field(name="Erreur", value=str(e), inline=False)
                    embed.set_footer(text="Club Cyber Bot - Logs", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")

                    #print(f"{self.name}'s data : {e}.")
                    await self.logs_channel.send(embed=embed, delete_after=DELETE_TIME)
                attempt += 1
    async def get_name(self):
        return self.name

    async def get_data(self):
        return self.data

    async def get_last_challenges(self):
        return self.challenges

    async def __repr__(self):
        return f"{self.name} : {self.data}, {self.challenges}"