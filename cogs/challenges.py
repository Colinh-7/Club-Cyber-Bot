from discord.ext import commands
from discord.ext.commands import MissingRequiredArgument, has_role
import asyncio , discord
from datetime import datetime
from includes import club_json
from includes import rootme_scrapper as rootme
from urllib.error import HTTPError



ROLE_ADMIN = "Admin"
WEEKLY_CHANNEL = 1296481389067370513
LOGS_CHANNEL = 1296481389209714785

class ChallengesCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def weekly_challenge_wait(self, ctx, ch_info, current_time):
        try:
            await asyncio.sleep(604800) #604800
            
            one_week_later = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
            challenges = await club_json.load_challenges()

            # Remove challenge from ongoing chall
            if ch_info["titre"] in challenges["ongoing_challenges"]:
                ch = challenges["ongoing_challenges"].pop(ch_info["titre"])
                ch["date_completed"] = one_week_later
                challenges["completed_challenges"][ch_info["titre"]] = ch
            
                await club_json.save_challenges(challenges)
                
            embed = discord.Embed(
                title=f"**Weekly Challenge terminé : {ch_info["titre"]}**",
                description=f"Le défi **{ch_info["titre"]}** est maintenant terminé.",
                color=discord.Color.red()
            )

            embed.add_field(name="Lien du défi", value=f"[Cliquez ici pour voir le défi](https://www.root-me.org/{ch_info['url_challenge']})", inline=False)
            embed.add_field(name="Score", value=ch_info["score"], inline=True)
            embed.add_field(name="Difficulté", value=ch_info["difficulte"], inline=True)
            embed.add_field(name="Date de fin", value=current_time, inline=False)
            embed.set_footer(text="Club Cyber Bot - Weekly Challenges", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")
                
            channel = self.bot.get_channel(WEEKLY_CHANNEL)
            await channel.send(embed=embed)
            #await ctx.send(embed=embed)

        except asyncio.CancelledError:

            embed = discord.Embed(
                title="CHALLENGES LOGS",
                description="Un défi a été interrompu prématurément.",
                color=discord.Color.red()
            )
        
            embed.add_field(name="Nom du Défi", value=ch_info["titre"], inline=False)
            embed.add_field(name="Statut", value="Interrompu", inline=True)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(name="Date d'Interruption", value=current_time, inline=True)

            embed.set_footer(text="Club Cyber Bot - Logs", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")


            channel = self.bot.get_channel(LOGS_CHANNEL)
            await channel.send(embed=embed)
            #await ctx.send(embed=embed)

    @commands.command(help="Ajoute un challenge à la semaine.")
    @has_role(ROLE_ADMIN)
    async def weekly(self, ctx, challenge: str):
        
        try :
            ch_info = await rootme.get_challenge_info(challenge, self.bot.rootme_token)[0]
        except HTTPError as e:
            await ctx.send(f"Il semblerait que le challenge **{challenge}** n'existe pas.")
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        challenges = await club_json.load_challenges() # from json
        
        challenges["ongoing_challenges"][challenge] = ({
            "link": f"https://www.root-me.org/{ch_info["url_challenge"]}",
            "date_added": current_time
        })
        
        await club_json.save_challenges(challenges)
            
        embed = discord.Embed(
            title=f"**Weekly Challenge ajouté : {ch_info['titre']}**",
            description=f"*{ch_info['soustitre']}*",
            color=discord.Color.green()
        )

        embed.add_field(name="Lien du défi", value=f"[Cliquez ici pour accéder au défi](https://www.root-me.org/{ch_info['url_challenge']})", inline=False)
        embed.add_field(name="Rubrique", value=ch_info["rubrique"], inline=True)
        embed.add_field(name="Score", value=ch_info["score"], inline=True)
        embed.add_field(name="Difficulté", value=ch_info["difficulte"], inline=True)
        embed.add_field(name="Date d'ajout", value=current_time, inline=False)
        embed.set_footer(text="Club Cyber Bot - Weekly Challenges", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")

        channel = self.bot.get_channel(WEEKLY_CHANNEL)   
        await channel.send(embed=embed)

        #await ctx.send(embed=embed)

        task = asyncio.create_task(self.weekly_challenge_wait(ctx, ch_info , current_time))
        self.bot.challenge_tasks[challenge] = task
            
    @commands.command(help="Arrête un challenge en cours.")
    @has_role(ROLE_ADMIN)
    async def stop(self, ctx, challenge: str):
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        challenges = await club_json.load_challenges()

        # Check if some challenges are currently active
        if "ongoing_challenges" not in challenges:
            await ctx.send("Il n'y a aucun défi en cours.")
            return

        # Delete challenge from ongoing challenge
        if challenge in challenges["ongoing_challenges"]:
            challenges["ongoing_challenges"].pop(challenge)
        else:
            await ctx.send(f"Le défi **{challenge}** n'a pas été trouvé dans les défis en cours.")
            return

        await club_json.save_challenges(challenges)
        
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
        embed.set_footer(text="Club Cyber Bot - Weekly Challenges", icon_url="https://eijv.u-picardie.fr/wp-content/uploads/sites/14/2023/07/cropped-Logo-EIJV-32x32.jpg")

        
        await channel.send(embed=embed)

        # For admins
        await ctx.send(f"Le défi **{challenge}** a été arrêté avec succès.")

    @commands.command(help="Valide un challenge.")
    async def done(self, ctx, chall: str):
        challenges = await club_json.load_challenges()

        if chall in challenges["ongoing_challenges"]:
            current_chall = challenges["ongoing_challenges"][chall]
            
            # Check if completed_by exists
            if "completed_by" not in current_chall:
                current_chall["completed_by"] = {}

            if ctx.author.name not in current_chall["completed_by"]:
                current_chall["completed_by"][ctx.author.name] = {"completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                await club_json.save_challenges(challenges)
                await ctx.send(f"{ctx.author.mention} a validé le challenge **{chall}** !\nBien joué !")
            else:
                await ctx.send("Tu as déjà validé ce challenge.")
        else:
            await ctx.send(f"Il n'y pas de challenge **{chall}** en cours.")


    @weekly.error
    async def weekly_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !weekly <NOM_CHALLENGE> <LIEN_CHALLENGE>")

    @stop.error
    async def chall_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !stop <NOM_CHALLENGE>")

    @done.error
    async def done_error(ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Usage : !done <NOM_CHALLENGE>")

async def setup(bot):
    await bot.add_cog(ChallengesCommands(bot))
        