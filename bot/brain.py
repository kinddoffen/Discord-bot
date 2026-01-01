import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import json
import random
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

dataFile = "/data/games.json"

def loadData():
    try:
        with open(dataFile, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def saveData(data):
    with open(dataFile, "w") as f:
        json.dump(data, f, indent=2)

@bot.event
async def on_ready():
    print(f"{bot.user.name} Active")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command()
async def hei(ctx):
    await ctx.send(f"Hei, {ctx.author.mention}!")

@bot.command()
async def mygames(ctx):
    user = str(ctx.author)
    data = loadData()
    games = data.get(user, [])
    if games:
        await ctx.send(f"Dine spill: {', '.join(games)}")
    else:
        await ctx.send(f"{ctx.author.mention} har ingen registrerte spill.")

@bot.command()
async def addgame(ctx, *, game):
    user = str(ctx.author)
    data = loadData()
    data.setdefault(user, [])
    if game not in data[user]:
        data[user].append(game)
        saveData(data)
        await ctx.send(f"{game} er lagt til {ctx.author.mention} sitt biblotek!")
    else:
        await ctx.send(f"{ctx.author.mention} har allerede {game} registrert i systemmet")

@bot.command()
async def removegame(ctx, *, game):
    user = str(ctx.author)
    data = loadData()
    
    if user not in data or game not in data[user]:
        await ctx.send(f"{ctx.author.mention} har ikke lagt til {game} ennå.")
        return
    
    data[user].remove(game)

    if not data[user]:
        del data[user]
    
    saveData(data)
    await ctx.send(f"{game} er fjernet fra {ctx.author.mention} sitt biblotek")

@bot.command()
async def velgspill(ctx):
    data = loadData()
    if not data:
        await ctx.send("Ingen spill registrert ennå.")
        return
    allSets = [set(g) for g in data.values()]
    common = set.intersection(*allSets) if allSets else set()
    if common:
        game = random.choice(list(common))
        await ctx.send(f"{ctx.message.guild.default_role} kan spille {game}")
    else:
        await ctx.send("Ingen felles spill registrert.")

@bot.command()
async def poll(ctx, *, question_and_options):
    try:
        parts = [part.strip() for part in question_and_options.split("|")]
        if len(parts) < 3:
            await ctx.send(f"{ctx.author.mention} du må skrive et spørsmål og minst to alternativer. F.eks \n!poll Hva skal vi spille? | REPO | Roblox.")
            return
        
        question = parts[0]
        options = parts[1:]

        emoji = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        if len(options) > len(emoji):
            await ctx.send("Max 10 alternativer støttes.")
            return
        
        description = ""
        for i, option in enumerate(options):
            description += f"{emoji[i]} {option}\n"

        embed = discord.Embed(title=question, description=description)
        pollMessage = await ctx.send(embed=embed)

        for i in range(len(options)):
            await pollMessage.add_reaction(emoji[i])
    
    except Exception as e:
        await ctx.send(f"Noe gikk galt: {e}")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)