import sys, csv, json, os
import discord, time
import asyncio
from datetime import datetime
from urllib.request import urlopen, HTTPError
from discord.ext import commands, tasks
from discord.ext.commands import MissingRequiredArgument, has_role
from bs4 import BeautifulSoup 

intents = discord.Intents.default()
intents.message_content = True
ROLE_ADMIN = "Admin"
CHALLENGES_FILE = "data/challenges.json"
LOGS_CHANNEL = 1296481389209714785
WEEKLY_CHANNEL = 1296481389067370513

# ==============
# Root Me Scrapper
# ==============

def split_words(list):
    # Month of the year in french
    month = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    new = []
    for temp in list:
        done = False
        for m in month:
            if m in temp:
                part= temp.split(m)
                new.append(part[0])
                new.append(m)
                done = True
                break
        if not done:
            new.append(temp)
    return new

def normalize_challenges(list):
    new = []
    for tmp in list:
        line = ""
        if ('>' not in tmp and '<' not in tmp):
            for word in tmp:
                line += word
                line += " "
            new.append(line)
    return new
            
# CSV parsing
def csv_parsing(file):
    users = []
    with open(file, 'r', newline='') as csvfile:
        dict_read = csv.reader(csvfile, delimiter=';')
        for line in dict_read:
            users.append(line[0])
        return users
        
# Web response from the request
def https_request(username):
    url = f"https://www.root-me.org/{username}"
    page = urlopen(url)
    return BeautifulSoup(page.read().decode("utf-8"), 'html.parser')

# Get user's profile stats
def get_user_stats(userpage):
    stats = {}
    row = userpage.find_all("div", {"class": "small-6 medium-3 columns text-center"})
    for line in row:
        array = line.get_text().split()
        stats[array[1]] = array[0]
    return stats

# Get user's last challenges
def get_last_challenges(userpage):
    challenges = []
    find = False
    challenge_section = None

    sections = userpage.find_all("div", class_= "t-body tb-padding")
    for section in sections:
        activity = section.find_all("h3")
        for a in activity:
            if a.get_text().find("Activité") > -1:
                find = True
                break
        if find :
            challenge_section = section
            break
    
    if challenge_section != None :
        challenge_section = challenge_section.find_all("li")

        for line in challenge_section:
            challenges.append(split_words(line.get_text().split()))

    return challenges

# ===============
# User
# ===============

class User:
    def __init__(self, name):
        self.name = name
        self.stats = {}
        self.challenges = []
        
        self.logs_channel = bot.get_channel(LOGS_CHANNEL)

        asyncio.create_task(self.load_user_data())

    async def load_user_data(self):
        while True:
            try:
                user_response = https_request(self.name)
                self.stats = get_user_stats(user_response)
                self.challenges = get_last_challenges(user_response)
                self.challenges = normalize_challenges(self.challenges)

                embed = discord.Embed(
                    title=f"Root Me LOGS",
                    description=f"Chargement des données de **{self.name}** réussi.",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Club Cyber Bot - Logs")
                await self.logs_channel.send(embed=embed)

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

                    await self.logs_channel.send(embed=embed)

                await asyncio.sleep(2)

    async def get_name(self):
        return self.name

    async def get_stats(self):
        return self.stats

    async def get_last_challenges(self):
        return self.challenges

    async def __repr__(self):
        return f"{self.name} : {self.stats}, {self.challenges}"

# ================
# Bot
# ================

class CyberBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.user_data = {}  # Simple dict for user storage
        self.challenge_tasks = {}

    async def setup_hook(self):
        self.reload_rootme.start()

    async def on_ready(self):
        # For Cyberbot TEST Server
        canal = self.get_channel(1295444773532074007)
        if canal is not None:
            await canal.send(f"Je suis en ligne !", delete_after=5)
        
    @tasks.loop(minutes=10)
    async def reload_rootme(self):
        self.user_data = {}
        user_names = csv_parsing('data/club.csv')
        for name in user_names:
            self.user_data[name] = User(name)
            await asyncio.sleep(2) # Avoid HTTP Error 429

    @reload_rootme.before_loop
    async def before_reload(self):
        await self.wait_until_ready()

# ===============
# JSON File
# ===============

def is_json_file_empty(file_path):
    if (os.path.exists(file_path)):
        if os.stat(file_path).st_size == 0:  # Fichier vide
            return True
    return False

def load_challenges():
    if (os.path.exists(CHALLENGES_FILE) and not is_json_file_empty(CHALLENGES_FILE)):
        with open(CHALLENGES_FILE, "r") as f:
            return json.load(f)
    else:
        return {"ongoing_challenges": [], "completed_challenges": []}

def save_challenges(challenges):
    with open(CHALLENGES_FILE, "w") as f:
        json.dump(challenges, f, indent=4)
            
# ================
# Bot Commands
# ================

bot = CyberBot()

@bot.command(help="Dis bonjour !")
async def bonjour(ctx):
    await ctx.send(f"Bonjour {ctx.author}!")

# ====================== Club infos ======================

@bot.command(help="Affiche les membres du club.")
async def club(ctx):
    msg = ""
    nb_members = len(bot.user_data)
    msg += f"Il y a actuellement {nb_members} personne(s) dans le Club Cyber : \r"
    for user in bot.user_data:
        msg += f"- `{user}`.\r"
    await ctx.send(msg)

@bot.command(help="Affiche tous les challenges terminés par le club.")
async def history(ctx):
    
    challenges = load_challenges()
    
    completed_challenges = challenges.get("completed_challenges", [])

    if not completed_challenges:
        await ctx.send("Aucun défi n'a encore été terminé.")
        return

    embed = discord.Embed(
        title="Weekly Challenges Terminés",
        description="Voici la liste des challenges qui ont été effectués jusqu'à présent :",
        color=discord.Color.blue()
    )

    for challenge in completed_challenges:
        embed.add_field(name=challenge["challenge"], value=f"Lien : {challenge['link']}\nDate : {challenge['date_added']}", inline=False)

    await ctx.send(embed=embed)

# ====================== Users management ======================

@bot.command(has_role="Admin", help="Ajoute un membre au club.")
@has_role(ROLE_ADMIN)
async def add(ctx, username: str):
    with open('club.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';')
        csvwriter.writerow([username])
    await ctx.send(f"L'utilisateur `{username}` a été ajouté au Club Cyber.")
    await bot.reload_rootme()


@bot.command(has_role="Admin", help="Enlève un membre du club.")
@has_role(ROLE_ADMIN)
async def rm(ctx, username: str):
    users = csv_parsing('club.csv') # Get all users
    if username in users:
        users.remove(username) # Remove users from CSV
        with open('club.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=';')
            for user in users:
                csvwriter.writerow([user])  # Write all users except user who have been removed
        await ctx.send(f"L'utilisateur `{username}` a été enlevé du Club Cyber.")
        await bot.reload_rootme()
    else:
        await ctx.send(f"L'utilisateur `{username}` n'existe pas dans le Club Cyber.")

@bot.command(help="Refresh les données des membres du club.")
async def reload(ctx) :
    await bot.reload_rootme()

# ====================== Users info ======================

@bot.command(help="Affiche les statistiques Root Me d'un membre.")
async def stats(ctx, username: str):
    msg = ""
    if username is not None and username in bot.user_data:
        stats = await bot.user_data[username].get_stats()
        msg += f"Statistiques de `{username}` :\r"
        for key in stats:
            msg += f"- {key} : `{stats[key]}`.\r"
        await ctx.send(msg)
    else:
        await ctx.send(f"Aucune donnée pour `{username}`.")

@bot.command(help="Affiche les derniers challenges Root Me d'un membre.")
async def chall(ctx, username: str):
    msg = ""
    if username is not None and username in bot.user_data:
        chall = await bot.user_data[username].get_last_challenges()
        msg += f"Challenge(s) réalisé(s) par `{username}` :\r"
        for str in chall:
            msg += (f"- `{str}`.\r")
        await ctx.send(msg)
    else:
        await ctx.send(f"Aucune donnée pour `{username}`.")

# ====================== Weekly challenges ======================

async def weekly_challenge_wait(ctx, challenge, chall_link, current_time):
    try:
        await asyncio.sleep(30)
        
        one_week_later = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
        challenges = load_challenges()

        # Remove challenge from ongoing chall
        for ch in challenges["ongoing_challenges"]:
            if ch["challenge"] == challenge and ch["link"] == chall_link:
                challenges["ongoing_challenges"].remove(ch)
                ch["date_completed"] = one_week_later
                challenges["completed_challenges"].append(ch)
                break
        
        save_challenges(challenges)
            
        embed = discord.Embed(
            title="Weekly Challenge terminé !",
            description=f"Une semaine s'est écoulée depuis le défi '{challenge}'",
            color=discord.Color.red()
        )
            
        embed.add_field(name="Défi", value=challenge, inline=True)
        embed.add_field(name="Lien du défi", value=f"[Cliquez ici pour accéder au défi]({chall_link})", inline=False)
        embed.add_field(name="Défi lancé le", value=current_time, inline=True)
        embed.add_field(name="Date actuelle", value=one_week_later, inline=True)
        embed.set_footer(text="Club Cyber Bot - Weekly Challenges")
            
        channel = bot.get_channel(WEEKLY_CHANNEL)
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

        channel = bot.get_channel(LOGS_CHANNEL)
        await channel.send(embed=embed)
        #await ctx.send(embed=embed)

@bot.command(help="Ajoute un challenge à la semaine.")
@has_role(ROLE_ADMIN)
async def weekly(ctx, challenge: str, chall_link: str):
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    challenges = load_challenges() # from json

    challenges["ongoing_challenges"].append({
        "challenge": challenge,
        "link": chall_link,
        "date_added": current_time
    })
    
    save_challenges(challenges)
        
    embed = discord.Embed(
        title="Weekly Challenge ajouté !",
        description=f"Un nouveau défi a été ajouté : **{challenge}**",
        color=discord.Color.green()
    )
        
    embed.add_field(name="Défi", value=challenge, inline=False)
    embed.add_field(name="Lien du défi", value=f"[Cliquez ici pour accéder au défi]({chall_link})", inline=False)
    embed.add_field(name="Date d'ajout", value=current_time, inline=False)
    embed.set_footer(text="Club Cyber Bot - Weekly Challenges")
    
    channel = bot.get_channel(WEEKLY_CHANNEL)   
    await channel.send(embed=embed)
    #await ctx.send(embed=embed)

    task = asyncio.create_task(weekly_challenge_wait(ctx, challenge, chall_link, current_time))
    bot.challenge_tasks[challenge] = task
        
@bot.command(help="Arrête un challenge en cours.")
@has_role(ROLE_ADMIN)
async def stop(ctx, challenge: str):
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    challenges = load_challenges()

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

    save_challenges(challenges)
    
    # Cancel the tasks
    if challenge in bot.challenge_tasks:
        bot.challenge_tasks[challenge].cancel()
        del bot.challenge_tasks[challenge]
    
    channel = bot.get_channel(WEEKLY_CHANNEL)
    
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
        
# ====================== Errors handling ======================
@weekly.error
async def weekly_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Usage : !weekly <NOM_CHALLENGE> <LIEN_CHALLENGE>")

@add.error
async def add_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Usage : !add <UTILISATEUR_ROOT_ME>")

@rm.error
async def rm_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Usage : !rm <UTILISATEUR_ROOT_ME>")

@stats.error
async def stats_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Usage : !stats <UTILISATEUR_ROOT_ME>")

@chall.error
async def chall_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Usage : !chall <UTILISATEUR_ROOT_ME>")

@stop.error
async def chall_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Usage : !stop <NOM_CHALLENGE>")


# Main
if __name__ == "__main__":
    try:
        bot.run(sys.argv[1])
    except IndexError:
        print(f"Error : missing API Key or Token. Try \"{sys.argv[0]} <KEY/TOKEN>\"")
        sys.exit(1) 
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        sys.exit(1)