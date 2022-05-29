import discord
from json import load
import sys, traceback
tokenFile = "token.json"
intents = discord.Intents.default()
intents.members = True
mainBot = discord.Bot(debug_guilds=load(open(tokenFile, "r"))["guild_id"], intents=intents)
mainCogs = ["ticketSys.ticketSys"]
@mainBot.event
async def on_ready():
    print("TICKET BOT IN RUNNING!")
if __name__ == '__main__':
    for cog in mainCogs:
        try:
            mainBot.load_extension(cog)
        except Exception as e:
            print(f"Error Loading {cog}", file=sys.stderr)
            traceback.print_exc()
mainBot.run(load(open(tokenFile, "r"))["token"])