from ast import main
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()


DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if DISCORD_BOT_TOKEN is None:
    print("Error: Discord bot token not found in environment variables.")
    exit()

intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# Load extensions (cogs) if you have them
# bot.load_extension('my_cog')

# Load the bot's initial extensions (e.g., commands, events)
async def setup():
    await bot.load_extension('bot.commands')

@bot.event
async def on_ready():
    print(f'We have logged in as')
    await setup()
    await bot.start(DISCORD_BOT_TOKEN)

asyncio.run(on_ready())
