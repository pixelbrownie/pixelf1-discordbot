import discord
from discord.ext import commands
import requests
import random
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()
TOKEN = os.getenv("TOKEN")

from keep_alive import keep_alive
keep_alive()  # starts the tiny web server

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is connected to race control!")

# !nextgp
# ==============================
# 🏁 Next Grand Prix Command
# ==============================

@bot.command()
async def nextgp(ctx):

    url = "https://api.jolpi.ca/ergast/f1/current/next.json"

    response = requests.get(url)
    data = response.json()

    race = data["MRData"]["RaceTable"]["Races"][0]

    race_name = race["raceName"]
    circuit = race["Circuit"]["circuitName"]
    location = race["Circuit"]["Location"]["locality"]
    country = race["Circuit"]["Location"]["country"]
    date = race["date"]

    embed = discord.Embed(
        title="🏁 Next Grand Prix",
        color=0xe10600
    )

    embed.add_field(name="Race", value=race_name, inline=False)
    embed.add_field(name="Circuit", value=circuit)
    embed.add_field(name="Location", value=f"{location}, {country}")
    embed.add_field(name="Date", value=date)

    await ctx.send(embed=embed)

# !driver <driver_name>
# ==============================
# 👨‍✈️ Driver Info Command
# ==============================

@bot.command()
async def driver(ctx, name: str):
    url = "https://api.jolpi.ca/ergast/f1/current/drivers.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            drivers = data["MRData"]["DriverTable"]["Drivers"]

            for d in drivers:
                if name.lower() in d["familyName"].lower():
                    embed = discord.Embed(title=f"{d['givenName']} {d['familyName']}", color=0xff0000)
                    embed.add_field(name="Nationality", value=d["nationality"])
                    embed.add_field(name="DOB", value=d["dateOfBirth"])
                    embed.add_field(name="Code", value=d.get("code", "N/A"))
                    if "url" in d:
                        embed.url = d["url"]
                    await ctx.send(embed=embed)
                    return
            await ctx.send("Driver not found.")

# !results
# ==============================
# 🏆 Race Results Command
# ==============================

@bot.command()
async def results(ctx):
    url = "https://api.jolpi.ca/ergast/f1/current/last/results.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            race = data["MRData"]["RaceTable"]["Races"][0]

            embed = discord.Embed(
                title=f"🏁 {race['raceName']} Results",
                color=0xe10600
            )

            for result in race["Results"][:3]:
                position = result["position"]
                driver = result["Driver"]["givenName"] + " " + result["Driver"]["familyName"]
                team = result["Constructor"]["name"]

                embed.add_field(
                    name=f"P{position}",
                    value=f"{driver} ({team})",
                    inline=False
                )

            await ctx.send(embed=embed)

# !schedule
# ==============================
# 📅 Schedule Command
# ==============================

@bot.command()
async def schedule(ctx):
    
    url = "https://api.jolpi.ca/ergast/f1/current.json"

    data = requests.get(url).json()

    races = data["MRData"]["RaceTable"]["Races"]

    embed = discord.Embed(
        title="🏎️ F1 Season Schedule",
        color=0xe10600
    )

    for race in races[:10]:
        embed.add_field(
            name=race["raceName"],
            value=race["date"],
            inline=False
        )

    await ctx.send(embed=embed)

# trivia command
import trivia

@bot.command()
async def f1trivia(ctx):

    q = random.choice(trivia.questions)

    await ctx.send(f"❓ {q[0]}")

# memes command
import memes

@bot.command()
async def radio(ctx):

    msg = random.choice(memes.memes)

    await ctx.send(f"📻 {msg}")

# ==============================
# 🏟️ Track Info Command
# ==============================
@bot.command()
async def track(ctx, place: str):
    url = "https://api.jolpi.ca/ergast/f1/circuits.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                circuits = data["MRData"]["CircuitTable"]["Circuits"]

                query = place.lower()
                for circuit in circuits:
                    city = circuit["Location"]["locality"].lower()
                    country = circuit["Location"]["country"].lower()

                    # Match against city or country
                    if query in city or query in country:
                        embed = discord.Embed(
                            title=circuit["circuitName"],
                            color=0x00ff00
                        )
                        embed.add_field(name="City", value=circuit["Location"]["locality"])
                        embed.add_field(name="Country", value=circuit["Location"]["country"])
                        embed.add_field(name="Circuit ID", value=circuit["circuitId"])
                        embed.add_field(name="Latitude", value=circuit["Location"]["lat"])
                        embed.add_field(name="Longitude", value=circuit["Location"]["long"])
                        await ctx.send(embed=embed)
                        return

                # If nothing matched
                await ctx.send(f"No circuit found for '{place}'. Try using the country name too.")
            else:
                await ctx.send("Failed to connect to API.")

bot.run(TOKEN)