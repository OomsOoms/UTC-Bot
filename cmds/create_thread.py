import pandas as pd
from nextcord.ui.view import View
from nextcord import SlashOption, SelectOption
from nextcord.ui import Select

def append_csv(event_data):
    new_data = pd.DataFrame(event_data) # Writing new results to CSV file
    new_data.to_csv("events_data.csv", mode='a', index=False, header=False)

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
                self.dropdown.callback = dropdown_callback

        view = View()
        view.add_item(CreateButton(options).dropdown)

        # Send the message and get the sent message object
        msg = await ctx.send("Please select an event:", view=view)
        msg = await ctx.send("hello")


        # Write the guild ID, channel ID, and message ID to the file
        with open('message_ids.txt', 'a') as file:
            file.write(f"{ctx.guild.id},{ctx.channel.id},{msg.id}\n")

