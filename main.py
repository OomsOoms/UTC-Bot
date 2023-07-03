import nextcord
from nextcord.ext import commands
import utc_cmds.__init__ as __init__
from dotenv import load_dotenv
import os
from utc_cmds.create_competition import Competition

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            __init__.views(bot)
            self.persistent_views_added = True

        await self.change_presence(activity=nextcord.Activity(name="UTC", type=nextcord.ActivityType.competing))

        print(f"Logged in as {self.user} (ID: {self.user.id})")

intents = nextcord.Intents.default()
intents.messages = True

bot = Bot(intents=intents)

__init__.cmds(bot)

@bot.slash_command(name='ping', description="Play ping pong with the bot's latency")
async def ping(ctx):
    # Measure the bot's latency in milliseconds
    latency = round(bot.latency * 1000)
    # Send a message to the user showing the bot's latency
    await ctx.send(f'Pong! Latency: {latency}ms')

load_dotenv() # Envoriment variables
bot.run(os.getenv("TEST_BOT_TOKEN"))
