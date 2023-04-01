from datetime import datetime

import nextcord
import pandas as pd
from nextcord import SelectOption, SlashOption
from nextcord.ext import commands

from cmds import init_cmds
from cmds.create_thread import update_dropdown
from cmds.fix_interactions import fix_interactions

intents = nextcord.Intents.all()
intents.members = True
bot = nextcord.Client(intents=nextcord.Intents.all())

# Define an event listener for when the bot is ready
@bot.event
async def on_ready():
    # Set the bot's presence
    await bot.change_presence(activity=nextcord.Activity(type=5, name='a UTC competition'))
    
    # Print a message indicating that the bot is online
    print(f'Online: {datetime.now()}'[:27].replace('-', '/'))

    # Call the function to fix the interactions for existing messages
    await fix_interactions(bot, update_dropdown)

# Define an event listener for when the bot joins a new guild
@bot.event
async def on_guild_join(guild):
    pass

# Initialize the bot's commands using the init_cmds function from the cmds module
init_cmds(bot)



# Start the bot by running its event loop with the specified token
bot.run('')