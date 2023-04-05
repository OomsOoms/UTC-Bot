from datetime import datetime
import pandas as pd
import nextcord

from cmds import init_cmds
from cmds.fix_interactions import fix_interactions

intents = nextcord.Intents.all()
intents.members = True
bot = nextcord.Client(intents=intents)

init_cmds(bot)

# Define an event listener for when the bot is ready
@bot.event
async def on_ready():
    # Call the fu5nction to fix the interactions for existing messages
    await fix_interactions(bot)

    # Set the bot's presence
    await bot.change_presence(activity=nextcord.Activity(type=5, name='Cube Clash 2023'))
    
    # Print a message indicating that the bot is online
    print(f'Online: {datetime.now()}'[:27].replace('-', '/'))

# Start the bot by running its event loop with the specified token
bot.run('OTgyNjEzMTY1MTk4MTU1ODg2.G0yARb.Fbifbsa7ErTA4v1dzeyxWzWGipzRwIEMfLCljk')
