import traceback

from TOKEN import BOT_TOKEN
import requests
from bs4 import BeautifulSoup
import pickle
import discord
from discord.ext import tasks, commands
from discord import app_commands
import os


# https://discord.com/api/oauth2/authorize?client_id=1093681310763057214&permissions=277025414208&scope=bot



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
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@tasks.loop(seconds=15)
async def main_loop():
    try:

        print("Starting Loop ...")

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
            try:

                column_modname = columns[0].get_text()

            except:
                column_modname = "Couldnt find modname."

            try:
                column_modurl = base_url_for_link + columns[2].find("a").get("href")
            except:
                column_modurl = "Couldnt find url."

            try:
                #print(str(columns[1]))
                column_text_unfinished = str(columns[1]).replace("<br/>", "\n").replace("<br>", "\n")
                #print(column_text_unfinished)
                column_text = BeautifulSoup(column_text_unfinished, 'html.parser').get_text()
                #column_text = columns[1].get_text()
            except:
                column_text = "No text found."

            try:
                column_writer = columns[2].get_text()
            except:
                column_writer = "No writer found."

            try:
                column_xago = columns[3].get_text()
            except:
                pass

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
                print("Is known.")
                pass
            else:
                print("Is new.")

                subscriber = load_cache(f'data{os.sep}data.pickle')

                print("Loaded subscriber successfully.")

                for xattribute, xvalue in subscriber.items():

                    if subscriber[xattribute] == value["messagereciever"]:
                        print(f"Found a notification for {subscriber[xattribute]}")
                        # if is not
                        # This checks if the msg writer is the one getting notified and doesn't send a dm then
                        if subscriber[xattribute] == value["writer"]:
                            print(f"{subscriber[xattribute]} is {value['writer']}")
                            pass
                        else:
                            if len(value["text"]) >= 500:
                                toshorten = value["text"]
                                shortend = toshorten[:400]
                                shortend = shortend + " ..."
                                value["text"] = shortend
                            print(value["text"].encode("utf-8"))
                            user = await bot.fetch_user(xattribute)

                            embed = discord.Embed(title="New comment on moddb!", url=value["modurl"], color=0xffffff)
                            embed.set_thumbnail(url="https://mods.vintagestory.at/web/img/vsmoddb-logo-s.png")
                            embed.add_field(name="Mod:", value=value["modname"], inline=False)
                            embed.add_field(name="From:", value=value["writer"], inline=False)
                            embed.add_field(name="Comment:", value=value["text"], inline=False)

                            await user.send(embed=embed)

                    if subscriber[xattribute] in value["text"]:
                        #print(value["modname"])
                        #print(value["text"])
                        # if is not
                        # This checks if the msg writer is the one getting notified and doesn't send a dm then


                        if len(value["text"]) >= 500:
                            secnd_toshorten = value["text"]
                            secnd_shortend = secnd_toshorten[:400]
                            secnd_shortend = secnd_shortend + " ..."
                            value["text"] = secnd_shortend

                        user = await bot.fetch_user(xattribute)

                        embed_ping = discord.Embed(title="New mention on moddb!", url=value["modurl"], color=0xffffff)
                        embed_ping.set_thumbnail(url="https://mods.vintagestory.at/web/img/vsmoddb-logo-s.png")
                        embed_ping.add_field(name="Mod:", value=value["modname"], inline=False)
                        embed_ping.add_field(name="From:", value=value["writer"], inline=False)
                        embed_ping.add_field(name="Comment:", value=value["text"], inline=False)

                        await user.send(embed=embed_ping)










                old_data[attribute] = value

        save_cache(old_data, f'data{os.sep}database.pickle')

        print("... Successfully ending loop.")
    except Exception:
        print("Error in main loop! Following Error happened:")
        traceback.print_exc()









@bot.tree.command(name="link")
@app_commands.describe(modauthorname = "Enter your Modname from the ModDB.")
async def link(interaction: discord.Interaction, modauthorname: str):
    msg_author = interaction.user.id
    print(f"Linked {msg_author} to {modauthorname}")
    data = load_cache(f'data{os.sep}data.pickle')
    try:
        data[str(msg_author)] = str(modauthorname)
        #print(data)
        save_cache(data, f'data{os.sep}data.pickle')
    except:
        print("Failed Saving")

    embed_link = discord.Embed(title="Linked your ModDB Account.", color=0xffffff)
    embed_link.set_thumbnail(url="https://mods.vintagestory.at/web/img/vsmoddb-logo-s.png")
    embed_link.add_field(name="You have linked your discord to your ModDB account:", value=modauthorname, inline=False)
    await interaction.response.send_message(embed=embed_link)

@bot.tree.command(name="unlink")
@app_commands.describe(modauthorname = "Enter your Modname from the ModDB.")
async def unlink(interaction: discord.Interaction, modauthorname: str):
    msg_author = interaction.user.id
    print(f"Unlinked {msg_author} to {modauthorname}")
    data = load_cache(f'data{os.sep}data.pickle')
    try:
        del data[str(msg_author)]
        #print(data)
        save_cache(data, f'data{os.sep}data.pickle')
    except:
        print("Failed Saving")
    embed_link = discord.Embed(title="Unlinked your ModDB Account.", color=0xffffff)
    embed_link.set_thumbnail(url="https://mods.vintagestory.at/web/img/vsmoddb-logo-s.png")
    embed_link.add_field(name="You have unlinked your discord to your ModDB account:", value=modauthorname, inline=False)
    await interaction.response.send_message(embed=embed_link)



















bot.run(BOT_TOKEN)
