import sys
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents = intents)

@bot.command()
async def bonjour(ctx):
    await ctx.send(f"Bonjour {ctx.author}")
    
@bot.command()
async def prouveur(ctx):
    await ctx.send(f"Miguel le GOAT.")

bot.run(sys.argv[1])