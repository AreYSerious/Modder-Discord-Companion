from TOKEN import BOT_TOKEN
import requests
from bs4 import BeautifulSoup
import pickle
import discord
from discord.ext import tasks, commands
from discord import app_commands
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
    main_loop.start()

@tasks.loop(seconds=15)
async def main_loop():


    base_url_for_link = "https://mods.vintagestory.at"
    url = 'https://mods.vintagestory.at/home'

    # Load the previous content from a pickle file if it exists

    data = {}

    # Make a request to the website
    response = requests.get(url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table on the webpage
    table = soup.find('table')

    # Find all rows in the table and skip the header row if present
    rows = table.find_all('tr')[1:]

    messages = []
    modauthors = []

    # Loop through the rows and extract the data
    for row in rows:
        # Find all columns in the row
        columns = row.find_all('td')

        # Extract the data from the columns
        column_modname = columns[0].get_text()
        column_modurl = base_url_for_link + columns[2].find("a").get("href")
        column_text = columns[1].get_text()
        column_writer = columns[2].get_text()
        column_xago = columns[3].get_text()
        # Do whatever you need to do with the data
        message = "Comment on " + column_modname + " from " + column_writer + ": " + column_text
        messages.append(message)

        modautorfinder_baseurl = "https://mods.vintagestory.at/api/mods?orderby=downloads&text="
        modautorfinder_modname_reformat = str(column_modname).replace(" ", "%20")
        modautorfinder_response = modautorfinder_baseurl + modautorfinder_modname_reformat
        modautorfinder_data = requests.get(modautorfinder_response).json()

        # Extracting Data from JsonAPI
        modautorfinder_author = modautorfinder_data["mods"][0]["author"]
        modauthors.append(modautorfinder_author)
        # print(modautorfinder_author)
        # print("")

        data[message] = {"modname": column_modname, "modurl": column_modurl, "text": column_text,
                         "writer": column_writer, "ago": column_xago, "messagereciever": modautorfinder_author}
        # print(data)

    # new data = data

    old_data = load_cache(f'data{os.sep}database.pickle')

    for attribute, value in data.items():
        if attribute in old_data:
            # print("Is known.")
            pass
        else:
            # print("Is new.")

            subscriber = load_cache(f'data{os.sep}data.pickle')
            print(subscriber)

            if value["messagereciever"] in subscriber:
                user = await bot.fetch_user(subscriber[value["messagereciever"]])

                embed = discord.Embed(title="New comment on moddb!", url=value["modurl"], color=0xffffff)
                embed.set_thumbnail(url="https://mods.vintagestory.at/web/img/vsmoddb-logo-s.png")
                embed.add_field(name="Mod:", value=value["modname"], inline=False)
                embed.add_field(name="From:", value=value["writer"], inline=False)
                embed.add_field(name="Comment:", value=value["text"], inline=False)

                await user.send(embed=embed)

            old_data[attribute] = value

    save_cache(old_data, f'data{os.sep}database.pickle')


bot.run(BOT_TOKEN)
