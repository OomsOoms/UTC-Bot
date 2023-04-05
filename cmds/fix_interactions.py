import nextcord
import pandas as pd
from .create_thread import update_dropdown
from .submit import update_button

async def fix_interactions(bot):
    # Load message IDs from a TSV file
    try:
        df = pd.read_csv('data/Messages.tsv', sep='\t')
    except (FileNotFoundError, pd.errors.EmptyDataError):
        print("Failed to load message IDs from file.")
        return

    # Iterate over each row in the dataframe
    for i, row in df.iterrows():
        guild_id, channel_id, message_id, function_name = row

        # Fetch the relevant guild and channel objects
        guild = bot.get_guild(int(guild_id))
        channel = guild.get_channel(int(channel_id)) or guild.get_thread(int(channel_id))

        if channel is None:
            print(f"Failed to get channel or thread {channel_id} in guild {guild.name}")
            df.drop(i, inplace=True)
            continue

        # Fetch the message object and the relevant update function
        try:
            message = await channel.fetch_message(int(message_id))
            update_function = globals().get(function_name)
        except (nextcord.NotFound, nextcord.Forbidden, ValueError):
            print(f"Failed to fetch message {message_id} in channel {channel_id}")
            df.drop(i, inplace=True)
            continue

        if not callable(update_function):
            print(f"Invalid update function: {function_name}")
            continue

        # Update the message with the new SelectOption objects
        await update_function(message)

    # Save the updated TSV file
    df.to_csv("data/Messages.tsv", sep='\t', index=False)
    print("All interactions fixed")
