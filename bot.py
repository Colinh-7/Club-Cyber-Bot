import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents = intents)

token = os.environ['TOKEN_BOT_DISCORD']
bot.run(token)