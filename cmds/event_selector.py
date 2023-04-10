import nextcord
import pandas as pd
from nextcord import Embed
from .submit import submit


# Load data
competitions_df = pd.read_csv("data/Competitions.tsv", sep="\t")
schedules_df = pd.read_csv("data/Schedules.tsv", sep="\t")
events_df = pd.read_csv("data/Events.tsv", sep="\t")


class EventSelectorView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    # Read the competitions data
    competitions_data = pd.read_csv("data/Competitions.tsv", sep="\t")

    # Find the active competition
    active_competition = competitions_data[competitions_data["active_day"] != False].iloc[0]["competition_id"]

    # Read the schedules data
    schedules_data = pd.read_csv("data/Schedules.tsv", sep="\t")

    # Find the schedule for the active day of the active competition
    active_day = competitions_data[competitions_data["competition_id"] == active_competition].iloc[0]["active_day"]
    active_schedule = schedules_data[(schedules_data["competition_id"] == active_competition) & (schedules_data["day_number"] == active_day)]

    # Get the event IDs from the active schedule
    event_ids = active_schedule["event_id"].tolist()

    # Read the events data
    events_data = pd.read_csv("data/Events.tsv", sep="\t")

    # Filter the events data to only include the events with the IDs from the active schedule
    active_events_data = events_data[events_data["event_id"].isin(event_ids)]

    # Create the select menu options
    options = [nextcord.SelectOption(label=event_name, value=f"{event_id},{event_id}") for event_name, event_id in zip(active_events_data["name"], active_events_data["event_id"])]


    @nextcord.ui.select(
        placeholder="Select an option", options=options, custom_id="EventSelectorView:dropdown"
    )
    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        # Stop interaction failed message
        await interaction.response.defer()

        # Get the selected option's label and value
        event_name, event_id = interaction.data['values'][0].split(",")

        # Create a new private thread
        thread = await interaction.channel.create_thread(name=f"Submit {event_name}", auto_archive_duration=1440)

        # Add the user who clicked the button to the thread
        await thread.add_user(interaction.user)

        # Call the submit function to handle the submission process
        await submit(thread, event_name=event_name, event_id=event_id)


def init_event_selector(bot):
    @bot.slash_command(name="event_selector", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def event_selector(ctx):
        # Create an Embed object with information about the competition
        embed = Embed(title="Cubing Competition Information", color=0xffa500)
        embed.add_field(name="Event Selection", value="Select an event from the dropdown menu. Note that the events will change every day for each new round, so please check the dropdown menu regularly to see what events are available.")
        embed.add_field(name="Solve Submission",value="To submit your solves, please go to the private channel named `submit [event name]`, which will appear once you select an event. The scrambles for each solve will be revealed after you submit your previous solve in the same channel.")
        embed.add_field(name="Penalties", value="If you need to add a penalty to a solve, you can do so by using the penalty buttons located under each scramble in the private channel.")
        embed.add_field(name="Results", value="Results will be available after each round.")
        embed.add_field(name="Good Luck!", value="Have fun competing! If you have any questions, feel free to ask in the designated discussion channel.")

        # Send the embed to a channel or user
        await ctx.send(embed=embed, view=EventSelectorView())