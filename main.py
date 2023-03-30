import nextcord
from nextcord.ext import commands
from datetime import datetime

from cmds import init_cmds

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
            guild_id, channel_id, message_id = line.split(',')  # Split guild ID, channel ID, and message ID
            guild = bot.get_guild(int(guild_id))
            if guild is None:
                print(f"Failed to get guild {guild_id}")
                continue
            channel = guild.get_channel(int(channel_id))
            if channel is None:
                print(f"Failed to get channel {channel_id} in guild {guild.name}")
                continue
            message = await channel.fetch_message(int(message_id))
            await message.edit(content='Fixed interaction!')
        except (nextcord.NotFound, nextcord.Forbidden, ValueError):
            print(f"Failed to fix interaction for line: {line}")



OTgyNjEzMTY1MTk4MTU1ODg2
@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Activity(type=5, name='a UTC competition'))
    print(f'Online: {datetime.now()}'[:27].replace('-', '/'))

    # Call the function to fix the interactions
    await fix_interactions()Fbifbsa7ErTA4v1dzeyxWzWGipzRwIEMfLCljk

@bot.event
async def on_guild_join(guild):
    pass

init_cmds(bot)

bot.run('.G0yARb.')
