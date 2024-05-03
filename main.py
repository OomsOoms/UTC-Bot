import os
import platform

import nextcord
from nextcord.ext.commands import Bot
from dotenv import load_dotenv

from utils.custom_logger import CustomLogger
from cogs import cogs


logger = CustomLogger(__name__)

intents = nextcord.Intents.default()
intents.messages = True


class Bot(Bot):
    def __init__(self) -> None:
        super().__init__(intents=intents)

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user.name}")
        logger.info(f"Nextcord API version: {nextcord.__version__}")
        logger.info(f"Python version: {platform.python_version()}")
        logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")

        self.load_extensions(cogs)
        await self.change_presence(activity=nextcord.Activity(name="UTC", type=nextcord.ActivityType.competing))

        await self.sync_application_commands(guild_id=988085977719402536)
        logger.info("Synced application commands")


load_dotenv()

bot = Bot()

# This ensures that the bot will have the 'Supports Commands' badge as cogs do not count towards this
@bot.slash_command(name='ping', description="Play ping pong with the bot's latency")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! Latency: {latency}ms')

bot.run(os.getenv("TOKEN"))
