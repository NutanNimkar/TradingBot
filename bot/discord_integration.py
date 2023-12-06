import discord
from discord.ext import commands
from bot.commands import check_stock_price
from dotenv import load_dotenv
import os

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True 
bot = commands.Bot(command_prefix='!',intents=intents)

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user.name}')

def start_bot():
    bot.add_command(check_stock_price)
    bot.run(DISCORD_BOT_TOKEN)
