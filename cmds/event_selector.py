import pandas as pd
from nextcord import SelectOption
from nextcord.ui import Select, View
from nextcord import Embed
from .submit import submit


async def dropdown_callback(interaction):
    # Stop interaction failed message
    await interaction.response.defer()

    # Get the selected option's label and value
    event_name, event_id = interaction.data['values'][0].split(",")

    # Create a new private thread
    thread_name = f"Submit {event_name}"
    thread = await interaction.channel.create_thread(name=thread_name, auto_archive_duration=1440)

    # Add the user who clicked the button to the thread
    await thread.add_user(interaction.user)

    # Call the submit function to handle the submission process
    await submit(thread, event_name=event_name, event_id=event_id)


async def update_event_selector(message):
    # Read the events data from the CSV file
    events_data_list = pd.read_csv("data/Events.tsv", sep='\t').to_dict("list")

    if len(events_data_list["name"]) > 0:
        # Create SelectOption objects for each event
        options = [SelectOption(label=event, value=f"{event},{eventId}") for event, eventId in zip(events_data_list["name"], events_data_list["event_id"])]


        # Create a Select object with the options
        dropdown = Select(placeholder="Select an option", options=options)

        # Set the dropdown callback function to the dropdown_callback function
        dropdown.callback = dropdown_callback

        # Create a View object and add the dropdown to it
        view = View(timeout=None)
        view.add_item(dropdown)

        # Edit the message with the new content and view
        await message.edit(view=view)
    else:
        # If no events are found in the CSV file, remove the view from the message
        await message.edit(view=None)


def init_event_selector(bot):
    @bot.slash_command(name="event_selector", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def event_selector(ctx):
        # Create an Embed object with information about the competition
        embed = Embed(title="Cubing Competition Information", color=0xffa500)
        embed.add_field(name="Event Selection", value="Select an event from the dropdown menu. Note that the events will change every day for each new round, so please check the dropdown menu regularly to see what events are available.")
        embed.add_field(name="Solve Submission", value="To submit your solves, please go to the private channel named `submit [event name]`, which will appear once you select an event. The scrambles for each solve will be revealed after you submit your previous solve in the same channel.")
        embed.add_field(name="Penalties", value="If you need to add a penalty to a solve, you can do so by using the penalty buttons located under each scramble in the private channel.")
        embed.add_field(name="Results", value="Results will be available after each round.")
        embed.add_field(name="Good Luck!", value="Have fun competing! If you have any questions, feel free to ask in the designated discussion channel.")

        # Send the embed to a channel or user
        msg = await ctx.send(embed=embed)

        # Fetch the message so I can get the ID because of a mysterious partial interaction message error 
        msg = await msg.fetch()

        # Update the message with the dropdown
        await update_event_selector(msg)

        # Write the guild ID, channel ID, message ID and the to the .tsv file
        with open('data/Messages.tsv', 'a') as file:
            file.write(f"{ctx.guild.id}\t{ctx.channel.id}\t{msg.id}\tupdate_event_selector\n")