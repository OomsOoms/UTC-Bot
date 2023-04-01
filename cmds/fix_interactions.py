import nextcord

# Define an asynchronous function to fix interactions for existing messages
async def fix_interactions(bot, update_fucntion):
    try:
        # Read the message IDs from a file
        with open('message_ids.txt', 'r') as file:
            lines = file.read().splitlines()
    except FileNotFoundError:
        print("File not found: message_ids.txt")
        return

    # Iterate over each line in the file
    for line in lines:
        try:
            # Split the line into guild ID, channel ID, and message ID
            guild_id, channel_id, message_id = line.split(',')
            
            # Get the guild object using the ID
            guild = bot.get_guild(int(guild_id))
            if guild is None:
                print(f"Failed to get guild {guild_id}")
                continue
            
            # Get the channel object using the ID
            channel = guild.get_channel(int(channel_id))
            if channel is None:
                print(f"Failed to get channel {channel_id} in guild {guild.name}")
                continue
            
            # Fetch the message object using the ID
            message = await channel.fetch_message(int(message_id)) # type: ignore
                        
            # Update the message with the new SelectOption objects
            await update_fucntion(message)
        
        # Catch exceptions that might occur while fixing interactions
        except (nextcord.NotFound, nextcord.Forbidden, ValueError):
            print(f"Failed to fix interaction for line: {line}")