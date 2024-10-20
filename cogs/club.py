import csv, discord
from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument
from includes import rootme_scrapper as rootme
from includes import club_json

ROLE_ADMIN = "Admin"

class ClubCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Affiche les membres du club.")
    async def club(self, ctx):
        msg = ""
        nb_members = len(self.bot.user_data)
        msg += f"Il y a actuellement {nb_members} personne(s) dans le Club Cyber :\r"
        for user in self.bot.user_data:
            msg += f"- `{user}`.\r"
        await ctx.send(msg)

    @commands.command(help="Ajoute un membre au club.")
    @commands.has_role(ROLE_ADMIN)
    async def add(self, ctx, username: str):
        if (rootme.check_if_user_exists(username)):
            with open('data/club.csv', 'a', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=';')
                csvwriter.writerow([username])
            await ctx.send(f"L'utilisateur `{username}` a été ajouté au Club Cyber.")
            await self.bot.reload_rootme()
        else:
            await ctx.send(f"L'utilisateur `{username}` ne semble pas existé.")

    @commands.command(help="Enlève un membre du club.")
    @commands.has_role(ROLE_ADMIN)
    async def rm(self, ctx, username: str):
        users = rootme.csv_parsing('data/club.csv')
        if username in users:
            users.remove(username)
            with open('data/club.csv', 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=';')
                for user in users:
                    csvwriter.writerow([user])
            await ctx.send(f"L'utilisateur `{username}` a été enlevé du Club Cyber.")
            await self.bot.reload_rootme()
        else:
            await ctx.send(f"L'utilisateur `{username}` n'existe pas dans le Club Cyber.")
        
    @commands.command(help="Affiche tous les challenges terminés par le club.")
    async def history(self, ctx):
        challenges = club_json.load_challenges()
        
        completed_challenges = challenges["completed_challenges"]

        if not completed_challenges:
            await ctx.send("Aucun défi n'a encore été terminé.")
            return

        embed = discord.Embed(
            title="Weekly Challenges Terminés",
            description="Voici la liste des challenges qui ont été effectués jusqu'à présent :",
            color=discord.Color.blue()
        )

        for challenge in completed_challenges:
            embed.add_field(name=challenge, value=f"- Lien : {completed_challenges[challenge]["link"]}\n- Date : {completed_challenges[challenge]["date_added"]}", inline=False)
        
        embed.set_footer(text="Club Cyber Bot", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")

        await ctx.send(embed=embed)
    
    @add.error
    async def add_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !add <UTILISATEUR_ROOT_ME>")

    @rm.error
    async def rm_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !rm <UTILISATEUR_ROOT_ME>")

async def setup(bot):
    await bot.add_cog(ClubCommands(bot))
