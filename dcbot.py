from TOKEN import BOT_TOKEN
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import pickle
import os

# function to load the cache
def load_cache(CACHE_FILE):
    try:
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# function to save the cache
def save_cache(cache, CACHE_FILE):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)





bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is running.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    msg_author = interaction.user
    user = await bot.fetch_user(msg_author.id)
    await user.send("Hi")
    print(msg_author)
    await interaction.response.send_message(f"Hi {interaction.user.mention}! This is a slash command!")

@bot.tree.command(name="link")
@app_commands.describe(modauthorname = "What should I say?")
async def link(interaction: discord.Interaction, modauthorname: str):
    msg_author = interaction.user.id
    print(msg_author)
    print(modauthorname)
    data = load_cache(f'data{os.sep}data.pickle')
    try:
        data[str(modauthorname)] = str(msg_author)
        print(data)
        save_cache(data, f'data{os.sep}data.pickle')
    except:
        print("Failed Saving")
    await interaction.response.send_message(f"{interaction.user.mention} Has been linked to {modauthorname}")

@bot.tree.command(name="unlink")
@app_commands.describe(modauthorname = "What should I say?")
async def unlink(interaction: discord.Interaction, modauthorname: str):
    msg_author = interaction.user.id
    print(msg_author)
    print(modauthorname)
    data = load_cache(f'data{os.sep}data.pickle')
    try:
        del data[str(modauthorname)]
        print(data)
        save_cache(data, f'data{os.sep}data.pickle')
    except:
        print("Failed Saving")
    await interaction.response.send_message(f"{interaction.user.mention} Has been linked to {modauthorname}")



bot.run(BOT_TOKEN)