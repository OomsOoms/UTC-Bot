import nextcord
from nextcord.ext import commands
import commands as cmds
from dotenv import load_dotenv
import os

load_dotenv()

intents = nextcord.Intents.default()
intents.messages = True

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            cmds.views(self)
            
            self.persistent_views_added = True

        await self.change_presence(activity=nextcord.Activity(name="UTC", type=nextcord.ActivityType.competing))

        print(f"Logged in as {self.user} (ID: {self.user.id})")

        #await cmds.scrape_records() # TODO: Make it send records every 10 minutes after checking they have not already been sentj

bot = Bot(intents=intents) 

cmds.cmds(bot)

@bot.slash_command(name='ping', description="Play ping pong with the bot's latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency}ms')

bot.run(os.getenv("BOT_TOKEN"))
