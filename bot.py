import discord
from discord.ext import commands
import requests
import random
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()
TOKEN = os.getenv("MTQ4MTcxMTUzODkzODA1MjcyMA.GG4EM6.LB_Xx6n0PQrYXsZjRYjNSeNXrDZxeo3AQOsll8")

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

    url = "https://api.jolpi.ca/ergast/f1/2026/results.json"
    data = requests.get(url).json()

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
# 📅 Season Schedule Command
# ==============================

@bot.command()
async def schedule(ctx):

    url = "https://api.jolpi.ca/ergast/f1/seasons.json"
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
async def track(ctx, city: str):
    # The URL for all circuits
    url = "https://api.jolpi.ca/ergast/f1/circuits.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                circuits = data["MRData"]["CircuitTable"]["Circuits"]

                # Loop through circuits to find a match by locality (city)
                for circuit in circuits:
                    location = circuit["Location"]["locality"]
                    country = circuit["Location"]["country"]

                    if city.lower() in location.lower():
                        embed = discord.Embed(
                            title=f"{circuit['circuitName']}",
                            color=0x00ff00
                        )
                        embed.add_field(name="City", value=location)
                        embed.add_field(name="Country", value=country)
                        embed.add_field(name="Circuit ID", value=circuit["circuitId"])
                        embed.add_field(name="Latitude", value=circuit["Location"]["lat"])
                        embed.add_field(name="Longitude", value=circuit["Location"]["long"])
                        
                        # Add link to circuit info if available
                        if "url" in circuit:
                            embed.url = circuit["url"]

                        await ctx.send(embed=embed)
                        return

                # If no circuit found
                await ctx.send("No circuit found for that city.")
            else:
                await ctx.send("Failed to connect to API.")

bot.run("MTQ4MTcxMTUzODkzODA1MjcyMA.GG4EM6.LB_Xx6n0PQrYXsZjRYjNSeNXrDZxeo3AQOsll8 ")