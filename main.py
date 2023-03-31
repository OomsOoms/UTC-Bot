from datetime import datetime

import nextcord
import pandas as pd
from nextcord import SelectOption, SlashOption
from nextcord.ext import commands

from cmds import init_cmds
from cmds.create_thread import update_message

intents = nextcord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def fix_interactions():
    try:
        with open('message_ids.txt', 'r') as file:
            lines = file.read().splitlines()
    except FileNotFoundError:
        print("File not found: message_ids.txt")
        return

    for line in lines:
        try:
            guild_id, channel_id, message_id = line.split(',')
            guild = bot.get_guild(int(guild_id))
            if guild is None:
                print(f"Failed to get guild {guild_id}")
                continue
            channel = guild.get_channel(int(channel_id))
            if channel is None:
                print(f"Failed to get channel {channel_id} in guild {guild.name}")
                continue
            message = await channel.fetch_message(int(message_id))
            events_data_list = pd.read_csv("events_data.csv").to_dict("list")
            options = [SelectOption(label=event, value=event) for event in events_data_list["event_name"]]
            await update_message(message, options)
        except (nextcord.NotFound, nextcord.Forbidden, ValueError):
            print(f"Failed to fix interaction for line: {line}")





@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Activity(type=5, name='a UTC competition'))
    print(f'Online: {datetime.now()}'[:27].replace('-', '/'))

    # Call the function to fix the interactions
    await fix_interactions()

@bot.event
async def on_guild_join(guild):
    pass

init_cmds(bot)

bot.run('OTgyNjEzMTY1MTk4MTU1ODg2.G0yARb.Fbifbsa7ErTA4v1dzeyxWzWGipzRwIEMfLCljk')
