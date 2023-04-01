import pandas as pd
from nextcord import SelectOption
from nextcord.ui import Select
from nextcord.ui.view import View
from nextcord import Embed

from .submit import submit


async def dropdown_callback(interaction):
    # Stop interaction failed message
    await interaction.response.defer()

    # Get the selected option
    selected_option = interaction.data["values"][0]

    # Create a new private thread
    thread_name = f"Submit {selected_option}"
    thread = await interaction.channel.create_thread(name=thread_name, auto_archive_duration=1440)

    # Add the user who clicked the button to the thread
    await thread.add_user(interaction.user)

    # Send a message to the thread
    await thread.send(f"Welcome {interaction.user.mention}! This is your private thread for submitting {selected_option} results!")

    await submit(interaction, thread)

async def update_dropdown(message):
    events_data_list = pd.read_csv("events_data.csv").to_dict("list")
    if len(events_data_list["event_name"]) > 0:
        options = [SelectOption(label=event, value=event) for event in events_data_list["event_name"]]

        dropdown = Select(placeholder="Select an option", options=options)
        dropdown.callback = dropdown_callback

        view = View()
        view.add_item(dropdown)

        # Edit the message with the new content and view
        await message.edit(view=view)
    else:
        await message.edit(view=None)


def init_create_thread(bot):
    @bot.slash_command(name="create_thread", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def create_thread(ctx):

        # Create an embed instance
        embed = Embed(title="Cubing Competition Information", color=0xffa500)

        # Add description to the embed
        embed.add_field(name="Event Selection", value="Select an event from the dropdown menu. Note that the events will change every day for each new round, so please check the dropdown menu regularly to see what events are available.")

        # Add submission information to the embed
        embed.add_field(name="Solve Submission", value="To submit your solves, please go to the private channel named `submit [event name]`, which will appear once you select an event. The scrambles for each solve will be revealed after you submit your previous solve in the same channel.")

        # Add penalty information to the embed
        embed.add_field(name="Penalties", value="If you need to add a penalty to a solve, you can do so by using the penalty buttons located under each scramble in the private channel.")

        # Add result information to the embed
        embed.add_field(name="Results", value="Results will be available after each round.")

        # Add good luck message to the embed
        embed.add_field(name="Good Luck!", value="Have fun competing! If you have any questions, feel free to ask in the designated discussion channel.")

        # Send the embed to a channel or user
        msg = await ctx.send(embed=embed)

        msg = await msg.fetch()

        # Update the message with the dropdown
        await update_dropdown(msg)

        # Write the guild ID, channel ID, and message ID to the file
        with open('message_ids.txt', 'a') as file:
            file.write(f"{ctx.guild.id},{ctx.channel.id},{msg.id},update_dropdown\n")