import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json

DATA_PATH = "/data/data.json" if os.getenv("RAILWAY_ENVIRONMENT") else "data.json"

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discordbot.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '.', intents = intents, case_insensitive = True, help_command = None)
bot.user_data = {}

def load_data():
    try:
        with open(DATA_PATH, "r") as file:
            content = file.read().strip()
            bot.user_data = json.loads(content) if content else {}
    except FileNotFoundError:
        bot.user_data = {}
    except json.JSONDecodeError:
        print("⚠️ data.json is corrupted. Starting with empty data.")
        bot.user_data = {}

def save_data():
    os.makedirs("/data", exist_ok=True)

    with open(DATA_PATH, "w") as file:
        json.dump(bot.user_data, file, indent=4)

bot.save_data = save_data

@bot.event
async def on_ready():
    try:
        load_data()
        await bot.load_extension("cogs.stats")
        await bot.load_extension("cogs.addBuff")
        await bot.load_extension("cogs.attributesHandler")
        await bot.load_extension("cogs.inventory_manager")
        await bot.load_extension("cogs.rollManager")
        await bot.load_extension("cogs.System")
        print("DATA FILE EXISTS:", os.path.exists("/data/data.json"))
        print("Bot online!")
    except Exception as e:
        print("ERROR IN on_ready:", e)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)


load_data()
bot.run(token, log_handler = handler, log_level = logging.DEBUG)