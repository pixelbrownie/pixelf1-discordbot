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
    
    # 2026 F1 Schedule
    schedule_2026 = [
        ("Mar 07", "Australian Grand Prix", "Melbourne"),
        ("Mar 15", "Chinese Grand Prix", "Shanghai"),
        ("Mar 28", "Japanese Grand Prix", "Suzuka"),
        ("May 03", "Miami Grand Prix", "Miami"),
        ("May 24", "Canadian Grand Prix", "Montreal"),
        ("Jun 07", "Monaco Grand Prix", "Monaco"),
        ("Jun 14", "Spanish Grand Prix", "Barcelona"),
        ("Jun 28", "Austrian Grand Prix", "Spielberg"),
        ("Jul 05", "British Grand Prix", "Silverstone"),
        ("Jul 19", "Belgian Grand Prix", "Spa"),
        ("Jul 26", "Hungarian Grand Prix", "Budapest"),
        ("Aug 23", "Dutch Grand Prix", "Zandvoort"),
        ("Sep 06", "Italian Grand Prix", "Monza"),
        ("Sep 13", "Spanish Grand Prix", "Madrid"),
        ("Sep 26", "Azerbaijan Grand Prix", "Baku"),
        ("Oct 11", "Singapore Grand Prix", "Singapore"),
        ("Oct 25", "United States Grand Prix", "Austin"),
        ("Nov 01", "Mexico City Grand Prix", "Mexico"),
        ("Nov 08", "São Paulo Grand Prix", "Brazil"),
        ("Nov 21", "Las Vegas Grand Prix", "Las Vegas"),
        ("Nov 29", "Qatar Grand Prix", "Qatar"),
        ("Dec 06", "Abu Dhabi Grand Prix", "Abu Dhabi")
    ]

    embed = discord.Embed(
        title="🏎️ 2026 F1 Season Schedule",
        description="Complete Formula 1 2026 calendar",
        color=0xe10600
    )

    for date, race_name, location in schedule_2026:
        embed.add_field(
            name=race_name,
            value=f"📅 {date} | 📍 {location}",
            inline=False
        )

    embed.set_footer(text="Total: 22 races")
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
    url = "https://api.jolpi.ca/ergast/f1/current.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                races = data["MRData"]["RaceTable"]["Races"]

                query = place.lower()
                for race in races:
                    circuit = race["Circuit"]
                    city = circuit["Location"]["locality"].lower()
                    country = circuit["Location"]["country"].lower()
                    circuit_name = circuit["circuitName"].lower()

                    # Match against city, country, or circuit name
                    if (query in city or query in country or query in circuit_name):
                        embed = discord.Embed(
                            title=circuit["circuitName"],
                            color=0x00ff00
                        )
                        embed.add_field(name="City", value=circuit["Location"]["locality"])
                        embed.add_field(name="Country", value=circuit["Location"]["country"])
                        embed.add_field(name="Circuit ID", value=circuit["circuitId"])
                        embed.add_field(name="Latitude", value=circuit["Location"]["lat"])
                        embed.add_field(name="Longitude", value=circuit["Location"]["long"])
                        embed.add_field(name="Race Date", value=race["date"])
                        await ctx.send(embed=embed)
                        return

                # If nothing matched
                await ctx.send(f"No circuit found for '{place}'. Try using city, country, or circuit name.")
            else:
                await ctx.send("Failed to connect to API.")

# ==============================
# 📰 F1 News Command
# ==============================
@bot.command()
async def news(ctx):
    try:
        # Use a simpler approach with ESPN F1 news RSS feed
        url = "https://www.espn.com/espn/rss/f1/story/_/id"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Simple XML parsing for RSS feed
                    import re
                    # Extract titles from RSS items
                    titles = re.findall(r'<title>(.*?)</title>', content)
                    # Remove the first title which is usually the feed title
                    titles = titles[1:6]  # Get next 5 titles
                    
                    if titles:
                        embed = discord.Embed(
                            title="📰 Latest F1 News",
                            description="Here are the latest Formula 1 headlines from ESPN:",
                            color=0xe10600
                        )
                        
                        for i, title in enumerate(titles, 1):
                            # Clean up title (remove CDATA and HTML entities)
                            clean_title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title)
                            clean_title = re.sub(r'&amp;', '&', clean_title)
                            clean_title = re.sub(r'&lt;', '<', clean_title)
                            clean_title = re.sub(r'&gt;', '>', clean_title)
                            
                            embed.add_field(name=f"News {i}", value=clean_title, inline=False)
                        
                        embed.set_footer(text="Source: ESPN F1")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("Unable to parse news at the moment.")
                else:
                    await ctx.send("Failed to fetch news from ESPN.")
                    
    except Exception as e:
        # Fallback to a simple message if RSS fails
        embed = discord.Embed(
            title="📰 F1 News",
            description="For the latest Formula 1 news, visit:",
            color=0xe10600
        )
        embed.add_field(name="Official F1 Website", value="https://www.formula1.com/en/latest/all.html", inline=False)
        embed.add_field(name="ESPN F1", value="https://www.espn.com/f1/", inline=False)
        embed.add_field(name="BBC Sport F1", value="https://www.bbc.com/sport/formula1", inline=False)
        
        await ctx.send(embed=embed)

bot.run(TOKEN)

