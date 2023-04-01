import nextcord
from .create_thread import update_dropdown
from .submit import update_button

# Define an asynchronous function to fix interactions for existing messages
async def fix_interactions(bot):
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
            # Split the line into guild ID, channel ID, message ID, and function name
            guild_id, channel_id, message_id, function_name = line.split(',')
            
            # Get the guild object using the ID
            guild = bot.get_guild(int(guild_id))
            if guild is None:
                print(f"Failed to get guild {guild_id}")
                continue
            
            # Get the channel object using the ID
            channel = guild.get_channel(int(channel_id))
            if channel is None:
                thread = guild.get_thread(int(channel_id))
                if thread is None:
                    print(f"Failed to get channel or thread {channel_id} in guild {guild.name}")
                    continue
                else:
                    channel = thread

            # Fetch the message object using the ID
            message = await channel.fetch_message(int(message_id))
                        
            # Get the function object using the function name
            update_function = globals().get(function_name)
            if update_function is None or not callable(update_function):
                print(f"Invalid update function: {function_name}")
                continue
            
            # Update the message with the new SelectOption objects
            await update_function(message)
        
        # Catch exceptions that might occur while fixing interactions
        except (nextcord.NotFound, nextcord.Forbidden, ValueError) as e:
            print(f"Failed to fix interaction for line: {line}. Error: {e}")
