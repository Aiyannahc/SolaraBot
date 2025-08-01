
import discord
from discord.ext import commands, tasks
import random
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Globals
user_blessings = {}
last_ritual_time = {}
last_battle_time = {}
battle_limits = {}
waifu_drops_channel = None
quote_channel = None
waifus = [
    # Sample - keep adding until there are 150
    "Motoko Kusanagi", "Lana Kane", "Lois Griffin", "Raven", "Yoruichi Shihouin",
    "Diane (Seven Deadly Sins)", "Jessica Rabbit", "Francine Smith", "Faye Valentine",
    "Esdeath", "Shego", "Stella Vermillion", "Velma (Velma series)", "Delilah (Inside Job)",
    "Marceline", "Kuvira", "Queen Tyr’ahnee", "Miss Pauling", "Cammy White", "Lady Tsunade"
] * 8  # Replicating sample to reach approx 150

ritual_sayings = [
    "Your goddess is pleased with your offerings. Gain +1 blessing.",
    "Your flame burns bright. +2 blessings.",
    "The stars align in your favor. Gain +3 blessings.",
    "A mischievous spirit meddles in your ritual. Lose -1 blessing.",
    "Your devotion wavers. -2 blessings.",
    "The void whispers encouragement. +1 blessing.",
    "You stepped on a sacred sigil. -3 blessings.",
    "You danced beautifully for the divine. +2 blessings.",
    "You forgot the sacred words. -1 blessing.",
    "You lit the incense just right. +1 blessing.",
    "An elder approves your chant. +2 blessings.",
    "You broke a sacred urn. -2 blessings.",
    "A comet passed overhead. +3 blessings.",
    "The flames spat at your feet. -1 blessing.",
    "A butterfly landed on your hand. +1 blessing.",
    "The ritual circle glows brightly. +2 blessings.",
    "You slipped on sacred oil. -2 blessings.",
    "You sang off-key. -1 blessing.",
    "You summoned a minor deity. +3 blessings.",
    "You nailed the offering dance. +2 blessings."
]

confess_outcomes = [
    "You are forgiven. +2 blessings.",
    "Your sins are many. -2 blessings.",
    "The goddess laughs. +1 blessing.",
    "Your confession was weak. -1 blessing.",
    "You cried sincerely. +2 blessings.",
    "You confessed nothing. -2 blessings.",
    "The spirits nod. +1 blessing.",
    "Lightning strikes behind you. -1 blessing.",
    "Your heart is pure. +3 blessings.",
    "Your lies are obvious. -2 blessings.",
    "You tremble. +1 blessing.",
    "You collapse in guilt. -1 blessing.",
    "The candle flickers. +2 blessings.",
    "You howl your sins. +1 blessing.",
    "The altar hums. +3 blessings.",
    "You scream into the void. -2 blessings.",
    "You are cradled by the divine. +2 blessings.",
    "You hide nothing. +1 blessing.",
    "You repent too late. -2 blessings.",
    "The goddess accepts your truth. +3 blessings."
]

quotes = [
    "“Even stars fade eventually.” – Unknown",
    "“Don’t trust a god who doesn’t laugh.” – Temple Scribble",
    "“You dropped this 👑.”",
    "“If chaos had a mother, she’d be fabulous.”",
    "“Your vibe is celestial.”",
    "“Pray you don’t meet her hungry.”",
    "“Blessed are the baddies.”",
    "“In her absence, even the sun dims.”",
    "“Forgiveness is divine. Petty is eternal.”",
    "“You look like trouble. She likes that.”",
    "“Once you worship chaos, peace feels boring.”",
    "“The goddess gives, the goddess drags.”",
    "“Miracles are just well-timed explosions.”",
    "“Sacrifice now, slay later.”",
    "“Only the devout get extra lives.”",
    "“The stars gossip about you.”",
    "“Divine timing hits different.”",
    "“May your coffee be strong and your enemies weak.”",
    "“Every saint has a scandal.”",
    "“Repent? No. Rebrand.”"
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_quote.start()

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(GUILD_ID)
    role = discord.utils.get(guild.roles, name="Embers")
    if role:
        try:
            await member.add_roles(role)
        except discord.Forbidden:
            print("Missing permissions to add roles.")

@bot.command()
async def ritual(ctx):
    user_id = ctx.author.id
    now = datetime.utcnow()
    last_used = last_ritual_time.get(user_id, datetime.min)

    if now - last_used < timedelta(days=1):
        await ctx.send(f"{ctx.author.mention} You may only perform the ritual once per day.")
        return

    last_ritual_time[user_id] = now
    result = random.choice(ritual_sayings)
    change = int([int(s) for s in result.split() if s.lstrip('-').isdigit()][0])
    user_blessings[user_id] = user_blessings.get(user_id, 0) + change
    await ctx.send(f"{ctx.author.mention} {result} Total blessings: {user_blessings[user_id]}")

@bot.command()
async def confess(ctx, *, text: str):
    outcome = random.choice(confess_outcomes)
    change = int([int(s) for s in outcome.split() if s.lstrip('-').isdigit()][0])
    user_id = ctx.author.id
    user_blessings[user_id] = user_blessings.get(user_id, 0) + change
    await ctx.send(f"{ctx.author.mention} {outcome} Total blessings: {user_blessings[user_id]}")

@bot.command()
async def battle(ctx, member: discord.Member):
    user_id = ctx.author.id
    now = datetime.utcnow()
    last_time = last_battle_time.get(user_id, datetime.min)
    count = battle_limits.get(user_id, 0)

    if now - last_time > timedelta(days=1):
        battle_limits[user_id] = 0

    if count >= 5:
        await ctx.send(f"{ctx.author.mention} You’ve reached the daily battle limit.")
        return

    last_battle_time[user_id] = now
    battle_limits[user_id] += 1
    outcome = random.choice(["win", "lose", "tie"])

    if outcome == "win":
        user_blessings[user_id] = user_blessings.get(user_id, 0) + 2
        user_blessings[member.id] = user_blessings.get(member.id, 0) - 2
        await ctx.send(f"{ctx.author.mention} won divine favor over {member.mention}! (+2/-2)")
    elif outcome == "lose":
        user_blessings[user_id] = user_blessings.get(user_id, 0) - 2
        user_blessings[member.id] = user_blessings.get(member.id, 0) + 2
        await ctx.send(f"{ctx.author.mention} lost divine favor to {member.mention}. (-2/+2)")
    else:
        await ctx.send(f"{ctx.author.mention} and {member.mention} are evenly matched. No blessings exchanged.")

@bot.command()
async def dailyquote(ctx):
    global quote_channel
    quote_channel = ctx.channel
    await ctx.send(random.choice(quotes))

@tasks.loop(hours=24)
async def daily_quote():
    if quote_channel:
        await quote_channel.send(random.choice(quotes))

@bot.command()
async def setwaifuchannel(ctx):
    global waifu_drops_channel
    waifu_drops_channel = ctx.channel
    await ctx.send(f"Waifu drops will now occur in {ctx.channel.mention}")

@bot.command()
async def setquotechannel(ctx):
    global quote_channel
    quote_channel = ctx.channel
    await ctx.send(f"Daily quotes will now appear in {ctx.channel.mention}")

@bot.command()
async def collection(ctx):
    await ctx.send(f"{ctx.author.mention} Your claimed waifus: (feature WIP)")

bot.run(TOKEN)
