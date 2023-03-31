import pandas as pd
from nextcord import SelectOption, SlashOption
from nextcord.ui import Select
from nextcord.ui.view import View


async def update_message(message, options):
    # Create the dropdown and add it to a View
    dropdown = Select(placeholder="Select an option", options=options)
    view = View()
    view.add_item(dropdown)

    # Edit the message with the new content and view
    await message.edit(content="Please select an event:", view=view)


def init_create_thread(bot):
    @bot.slash_command(name="create_thread", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def create_thread(ctx):
        events_data_list = pd.read_csv("events_data.csv").to_dict("list")
        options = [SelectOption(label=event, value=event) for event in events_data_list["event_name"]]

        class CreateButton:
            def __init__(self, options):
                async def dropdown_callback(ctx):
                    # Stop interaction failed message
                    await ctx.response.defer()
                    
                    # Get the selected option
                    selected_option = ctx.data["values"][0]

                    ## Check if the user has already competed in the event
                    #if ctx.user.id in events_data_list["user_id"] and selected_option in events_data_list["event_name"]:
                    #    await ctx.send(f"You have already competed in {selected_option}.")
                    #    return

                    # Create a new private thread
                    thread_name = f"{ctx.user.name}'s thread for {selected_option}"
                    thread = await ctx.channel.create_thread(name=thread_name, auto_archive_duration=1440)

                    # Add the user who clicked the button to the thread
                    await thread.add_user(ctx.user)

                    # Send a message to the thread
                    await thread.send(f"Welcome {ctx.user.mention}! This is your private thread for {selected_option}.")

                self.dropdown = Select(placeholder="Select an option", options=options)
                self.dropdown.callback = dropdown_callback # type: ignore
        

        #ctx.response.defer()

        # Send the message and get the sent message object
        message = await ctx.send("Please select an event:")

        print(message.id)

        # Write the guild ID, channel ID, and message ID to the file
        with open('message_ids.txt', 'a') as file:
            file.write(f"{ctx.guild.id},{ctx.channel.id},{message.id}\n")
            print(message.id)

        view = View()
        view.add_item(CreateButton(options).dropdown)

        # Update the message with the dropdown
        await update_message(message, options)


