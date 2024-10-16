import sys, csv, time
import discord
from urllib.request import urlopen, HTTPError
from discord.ext import commands, tasks
from bs4 import BeautifulSoup 

intents = discord.Intents.default()
intents.message_content = True

# ==============
# Root Me Scrapper
# ==============

def split_words(list):
    # Liste des mois en français
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
        try:
            user_response = https_request(self.name)
            self.stats = get_user_stats(user_response)
            self.challenges = get_last_challenges(user_response)
            self.challenges = normalize_challenges(self.challenges)
        except HTTPError as e:
            self.stats = {}
            self.challenges = []
            print(f"{e}")

    def get_name(self):
        return self.name

    def get_stats(self):
        return self.stats
    
    def get_last_challenges(self):
        return self.challenges
    
    def __repr__(self):
        return f"{self.name} : {self.stats}, {self.challenges}"

# ================
# Bot
# ================

class CyberBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.user_data = {}  # Simple dict for user storage

    async def setup_hook(self) -> None:
        self.reload_rootme.start()

    async def on_ready(self):
        canal = self.get_channel(1295444773532074007)
        if canal is not None:
            await canal.send(f"Je suis en ligne !", delete_after=5)
        
    @tasks.loop(minutes=1)
    async def reload_rootme(self):
        self.user_data = {}
        user_names = csv_parsing('club.csv')
        for name in user_names:
            self.user_data[name] = User(name)
            time.sleep(2) # Avoid HTTP Error 429

    @reload_rootme.before_loop
    async def before_reload(self):
        await self.wait_until_ready()
            
# ================
# Bot instance
# ================

bot = CyberBot()

@bot.command()
async def bonjour(ctx):
    await ctx.send(f"Bonjour {ctx.author}!")

@bot.command()
async def club(ctx):
    msg = ""
    nb_members = len(bot.user_data)
    msg += f"Il y a actuellement {nb_members} personne(s) dans le Club Cyber : \n"
    for user in bot.user_data:
        msg += f"   - `{user}`.\n"
    await ctx.send(msg)

@bot.command()
async def add(ctx, username: str):
    with open('club.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=';')
        csvwriter.writerow([username])
    await ctx.send(f"L'utilisateur `{username}` a été ajouté au Club Cyber.")
    await bot.reload_rootme()


@bot.command()
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

@bot.command()
async def stats(ctx, username: str):
    msg = ""
    if username is not None and username in bot.user_data:
        stats = bot.user_data[username].get_stats()
        msg += f"Statistiques de `{username}` :\n"
        for key in stats:
            msg += f"   - {key} : `{stats[key]}`.\n"
        await ctx.send(msg)
    else:
        await ctx.send(f"Aucune donnée pour `{username}`.")

@bot.command()
async def chall(ctx, username: str):
    msg = ""
    if username is not None and username in bot.user_data:
        chall = bot.user_data[username].get_last_challenges()
        msg += f"Challenge(s) réalisé(s) par `{username}` :\n"
        for str in chall:
            msg += (f"   - `{str}`.\n")
        await ctx.send(msg)
    else:
        await ctx.send(f"Aucune donnée pour `{username}`.")

# Main
if __name__ == "__main__":
    bot.run(sys.argv[1])
