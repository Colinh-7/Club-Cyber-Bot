from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument
import discord

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Affiche les statistiques Root Me d'un membre.")
    async def stats(self, ctx, username: str):
        for id in self.bot.user_data:
            if username == await self.bot.user_data[id].get_name() :
                stats = await self.bot.user_data[id].get_data()
                embed = discord.Embed(
                    title=f"**{stats['nom']}**", 
                    description=f"Statistiques de {stats['nom']}",
                    color=discord.Color.blue()
                )

                embed.add_field(name="ID Auteur", value=stats["id_auteur"], inline=False)
                embed.add_field(name="Position", value=stats["position"] if stats["position"] != "" else "Non classé", inline=True)
                embed.add_field(name="Score", value=stats["score"], inline=True)
                embed.add_field(name="Challenges", value=len(self.bot.user_data[id].challenges), inline=True)
                embed.add_field(name="Compromissions", value=len(stats["solutions"]), inline=True)
                embed.add_field(name="Membre", value="Oui" if stats["membre"] == "true" else "Non", inline=True)
                embed.add_field(name="Statut", value="Premium" if "pre" in stats["statut"] else "Gratuit", inline=True)
                embed.set_thumbnail(url=f"https://www.root-me.org/{stats['logo_url']}")
                embed.set_footer(text="Club Cyber Bot", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")
                await ctx.send(embed=embed)
                return 
        await ctx.send(f"Aucune donnée pour `{username}`.")

    @commands.command(help="Affiche les derniers challenges Root Me d'un membre.")
    async def chall(self, ctx, username: str):
        if username in self.bot.user_data:
            msg = f"Derniers challenges de **{username}** : \n"
            chall = await self.bot.user_data[username].get_last_challenges()
            for i in range(10):
                msg += f"* {chall[i]["titre"]}. ({chall[i]["date"]})\n"
            await ctx.send(msg)
        else:
            await ctx.send(f"Aucune donnée pour `{username}`.")

    @commands.command(help="Refresh les données des membres du club.")
    async def reload(self, ctx) :
        await self.bot.reload_rootme()

    @stats.error
    async def stats_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !stats <UTILISATEUR_ROOT_ME>")

    @chall.error
    async def chall_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !chall <UTILISATEUR_ROOT_ME>")

async def setup(bot):
    await bot.add_cog(UserCommands(bot))