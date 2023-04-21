import nextcord
from nextcord.ext import commands
import cmds.__init__ as __init__

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            __init__.views(bot)
            self.persistent_views_added = True

        await self.change_presence(activity=nextcord.Activity(name="DCC", type=nextcord.ActivityType.competing))



        print(f"Logged in as {self.user} (ID: {self.user.id})")

intents = nextcord.Intents.default()
intents.messages = True

bot = Bot(intents=intents)

__init__.cmds(bot)

# Start the bot by running its event loop with the specified token
bot.run('OTgyNjEzMTY1MTk4MTU1ODg2.G0yARb.Fbifbsa7ErTA4v1dzeyxWzWGipzRwIEMfLCljk')
