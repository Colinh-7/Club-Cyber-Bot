from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument

class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Affiche les statistiques Root Me d'un membre.")
    async def stats(self, ctx, username: str):
        msg = ""
        if username is not None and username in self.bot.user_data:
            stats = await self.bot.user_data[username].get_stats()
            msg += f"Statistiques de `{username}` :\r"
            for key in stats:
                msg += f"- {key} : `{stats[key]}`.\r"
            await ctx.send(msg)
        else:
            await ctx.send(f"Aucune donnée pour `{username}`.")

    @commands.command(help="Affiche les derniers challenges Root Me d'un membre.")
    async def chall(self, ctx, username: str):
        msg = ""
        if username is not None and username in self.bot.user_data:
            chall = await self.bot.user_data[username].get_last_challenges()
            msg += f"Challenge(s) réalisé(s) par `{username}` :\r"
            for str in chall:
                msg += (f"- `{str}`.\r")
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