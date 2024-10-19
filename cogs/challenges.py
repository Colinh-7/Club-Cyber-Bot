from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, has_role
import asyncio , discord
from datetime import datetime
from includes import club_json

ROLE_ADMIN = "Admin"
WEEKLY_CHANNEL = 1296481389067370513
LOGS_CHANNEL = 1296481389209714785

class ChallengesCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def weekly_challenge_wait(self, ctx, challenge, chall_link, current_time):
        try:
            await asyncio.sleep(30)
            
            one_week_later = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
            challenges = club_json.load_challenges()

            # Remove challenge from ongoing chall
            for ch in challenges["ongoing_challenges"]:
                if ch["challenge"] == challenge and ch["link"] == chall_link:
                    challenges["ongoing_challenges"].remove(ch)
                    ch["date_completed"] = one_week_later
                    challenges["completed_challenges"].append(ch)
                    break
            
            club_json.save_challenges(challenges)
                
            embed = discord.Embed(
                title="Weekly Challenge terminé !",
                description=f"Une semaine s'est écoulée depuis le défi '{challenge}'",
                color=discord.Color.red()
            )
                
            embed.add_field(name="Nom du défi", value=challenge, inline=True)
            embed.add_field(name="Lien du défi", value=f"[Cliquez ici pour accéder au défi]({chall_link})", inline=False)
            embed.add_field(name="Défi lancé le", value=current_time, inline=False)
            embed.add_field(name="Date actuelle", value=one_week_later, inline=True)
            embed.set_footer(text="Club Cyber Bot - Weekly Challenges")
                
            channel = self.bot.get_channel(WEEKLY_CHANNEL)
            await channel.send(embed=embed)
            #await ctx.send(embed=embed)

        except asyncio.CancelledError:

            embed = discord.Embed(
                title="CHALLENGES LOGS",
                description="Un défi a été interrompu prématurément.",
                color=discord.Color.red()
            )
        
            embed.add_field(name="Nom du Défi", value=challenge, inline=False)
            embed.add_field(name="Lien du Défi", value=chall_link, inline=False)
            embed.add_field(name="Statut", value="Interrompu", inline=True)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(name="Date d'Interruption", value=current_time, inline=True)

            embed.set_footer(text="Club Cyber Bot - Logs")

            channel = self.bot.get_channel(LOGS_CHANNEL)
            await channel.send(embed=embed)
            #await ctx.send(embed=embed)

    @commands.command(help="Ajoute un challenge à la semaine.")
    @has_role(ROLE_ADMIN)
    async def weekly(self, ctx, challenge: str, chall_link: str):
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        challenges = club_json.load_challenges() # from json

        challenges["ongoing_challenges"].append({
            "challenge": challenge,
            "link": chall_link,
            "date_added": current_time
        })
        
        club_json.save_challenges(challenges)
            
        embed = discord.Embed(
            title="Weekly Challenge ajouté !",
            description=f"Un nouveau défi a été ajouté : **{challenge}**",
            color=discord.Color.green()
        )
            
        embed.add_field(name="Nom du défi", value=challenge, inline=True)
        embed.add_field(name="Lien du défi", value=f"[Cliquez ici pour accéder au défi]({chall_link})", inline=False)
        embed.add_field(name="Date d'ajout", value=current_time, inline=False)
        embed.set_footer(text="Club Cyber Bot - Weekly Challenges")
        
        channel = self.bot.get_channel(WEEKLY_CHANNEL)   
        await channel.send(embed=embed)
        #await ctx.send(embed=embed)

        task = asyncio.create_task(self.weekly_challenge_wait(ctx, challenge, chall_link, current_time))
        self.bot.challenge_tasks[challenge] = task
            
    @commands.command(help="Arrête un challenge en cours.")
    @has_role(ROLE_ADMIN)
    async def stop(self, ctx, challenge: str):
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        challenges = club_json.load_challenges()

        # Check if some challenges are currently active
        if "ongoing_challenges" not in challenges:
            await ctx.send("Il n'y a aucun défi en cours.")
            return

        # Delete challenge from ongoing challenge
        challenge_found = None
        for ch in challenges["ongoing_challenges"]:
            if ch["challenge"] == challenge:
                challenge_found = ch
                challenges["ongoing_challenges"].remove(ch)
                break
        
        if not challenge_found:
            await ctx.send(f"Le défi **{challenge}** n'a pas été trouvé dans les défis en cours.")
            return

        club_json.save_challenges(challenges)
        
        # Cancel the tasks
        if challenge in self.bot.challenge_tasks:
            self.bot.challenge_tasks[challenge].cancel()
            del self.bot.challenge_tasks[challenge]
        
        channel = self.bot.get_channel(WEEKLY_CHANNEL)
        
        embed = discord.Embed(
            title="Challenge annulé !",
            description=f"Le challenge **{challenge}** a été arrêté manuellement.",
            color=discord.Color.orange()
        )
        
        embed.add_field(name="Défi", value=challenge, inline=True)
        embed.add_field(name="Date d'arrêt", value=current_time, inline=True)
        embed.set_footer(text="Club Cyber Bot - Weekly Challenges")
        
        await channel.send(embed=embed)

        # For admins
        await ctx.send(f"Le défi **{challenge}** a été arrêté avec succès.")

    @weekly.error
    async def weekly_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !weekly <NOM_CHALLENGE> <LIEN_CHALLENGE>")

    @stop.error
    async def chall_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !stop <NOM_CHALLENGE>")

async def setup(bot):
    await bot.add_cog(ChallengesCommands(bot))
        