import nextcord
from nextcord.ext import commands

from  persistent_view import *
from cmds import init_cmds

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(PersistentView())
            self.persistent_views_added = True

        print(f"Logged in as {self.user} (ID: {self.user.id})")

intents = nextcord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

init_cmds(bot)

# Start the bot by running its event loop with the specified token
bot.run('OTgyNjEzMTY1MTk4MTU1ODg2.G0yARb.Fbifbsa7ErTA4v1dzeyxWzWGipzRwIEMfLCljk')
