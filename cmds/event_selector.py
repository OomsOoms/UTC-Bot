import nextcord
import pickle
import pandas as pd
from nextcord import Embed
from .submit import submit

# Load data
events_df = pd.read_csv("data/Events.tsv", sep="\t")
schedules_df = pd.read_csv("data/Schedules.tsv", sep='\t')

def update_dropdown():
    competitions_df = pd.read_csv("data/Competitions.tsv", sep="\t")
    # Find the active competition
    active_competition = competitions_df[competitions_df["active_day"] != 0].iloc[0]["competition_id"]

    # Find the schedule for the active day of the active competition
    active_day = competitions_df[competitions_df["competition_id"] == active_competition].iloc[0]["active_day"]
    active_schedule = schedules_df[(schedules_df["competition_id"] == active_competition) & (schedules_df["day_number"] == active_day)]

    # Get the event IDs from the active schedule
    event_ids = active_schedule["event_id"].tolist()

    # Filter the events data to only include the events with the IDs from the active schedule
    active_events_data = events_df[events_df["event_id"].astype(str).isin([str(event_id) for event_id in event_ids])]

    # Create the select menu options
    options = [nextcord.SelectOption(label=event_name, value=f"{event_id},{event_name}") for event_name, event_id in zip(active_events_data["name"], active_events_data["event_id"])]

    return options

class EventSelectorView(nextcord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # Define the select menu
    @nextcord.ui.select(
        placeholder="Select an option", options=update_dropdown(), custom_id="EventSelectorView:dropdown"
    )
    async def dropdown(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):


        event_id, event_name  = interaction.data['values'][0].split(",")

        # Load UserSubmit data from pickle file
        with open("data/user_submit.pickle", "rb") as f:
            user_submit = pickle.load(f)

        competitions_df = pd.read_csv("data/Competitions.tsv", sep="\t")

        competition_id = competitions_df[competitions_df["active_day"] != 0].iloc[0]["competition_id"]

        active_day = competitions_df[competitions_df["active_day"] != 0].iloc[0]["active_day"]
        
        # Filter the schedules DataFrame based on the filtering criteria
        filtered_schedule = schedules_df[(schedules_df['competition_id'].astype(str) == str(competition_id)) &
                                    (schedules_df['event_id'].astype(str) == str(event_id)) &
                                    (schedules_df['day_number'].astype(str) == str(active_day))]
        
        round_type = filtered_schedule['round'].values[0]






        results = pd.read_csv('data/Results.tsv', dtype={'pos': int, 'value_2': 'Int64', 'value_3': 'Int64', 'value_4': 'Int64', 'value_5': 'Int64'}, sep='\t')

        event_results = results[(results['competition_id'].astype(str) == str(competition_id)) & 
                        (results['event_id'].astype(str) == str(event_id)) & 
                        (results['round_type'].astype(str) == str(round_type))]
        event_results = event_results.sort_values(by="average", key=lambda x:x.astype(int), ascending=True)

        # Filter the schedules DataFrame based on the filtering criteria
        filtered_schedule = schedules_df[(schedules_df['competition_id'].astype(str) == str(competition_id)) &
                                    (schedules_df['event_id'].astype(str) == str(event_id)) &
                                    (schedules_df['round'].astype(str) == str(round_type))]

        num_highlight = filtered_schedule['advance'].values[0]

        if num_highlight < 1:
            num_highlight = num_highlight*len(event_results)


        # Filter the rows that match the specified competition ID and event ID
        matches = schedules_df[(schedules_df['competition_id'] == competition_id) & (schedules_df['event_id'] == event_id)]

        # Extract the "round" values for each matching row
        rounds = matches['round']
        # if there is only one round 
        special = False if len(rounds) == 1 else True

        # Initialize a flag to indicate if the user is in the current round
        in_current_round = True

        if interaction.user.id not in event_results['user_id'].head(int(num_highlight)).tolist() and str(round_type) != "1" and special:
            in_current_round = False
            

        else:
            # Check if the select data matches any thread object and if they are in the current round
            for thread_object in user_submit.thread_list.values():
                    if (thread_object.user_id == interaction.user.id and
                        thread_object.event_id == thread_object.event_id and
                        thread_object.competition_id == competitions_df[competitions_df["active_day"] != 0].iloc[0]["competition_id"] and
                        thread_object.round_type == round_type):

                        thread = self.bot.get_channel(thread_object.thread_id)
                        # Match found, do something with the thread object
                        if thread is None:
                            await interaction.send("You have already submitted this event!", ephemeral=True)
                            in_current_round = False
                        else:
                            await interaction.send(f"You already have a thread for this event! https://discord.com/channels/{thread_object.guild_id}/{thread_object.thread_id}", ephemeral=True)
                            in_current_round = False

                        break

        # Check the flag before creating a new thread
        if in_current_round:
            # Create a new private thread
            thread = await interaction.channel.create_thread(name=f"Submit {event_name}", auto_archive_duration=None, type=nextcord.ChannelType.private_thread)

            # Add the user who clicked the button to the thread
            await thread.add_user(interaction.user)

            # Call the submit function to handle the submission process
            await submit(thread, event_name=event_name, event_id=event_id, interaction=interaction)
        else:
            await interaction.response.send_message("You are not in this round", ephemeral=True)
        await interaction.response.defer()

# Define the check function
def is_admin(ctx):
    return ctx.author.guild_permissions.administrator

def init_event_selector(bot):
    @bot.slash_command(name="event-selector", description="Creates a private thread for the user who clicks the button in the dropdown")
    async def event_selector(ctx):
        if not ctx.user.guild_permissions.administrator:
            await ctx.response.send_message("You are not authorized to run this command.", ephemeral=True)
        else:
            # Create an Embed object with information about the competition
            embed = Embed(title="Cubing Competition Information", color=0xffa500)
            embed.add_field(name="Event Selection", value="Select an event from the dropdown menu. Note that the events will change every day for each new round, so please check the dropdown menu regularly to see what events are available.")
            embed.add_field(name="Solve Submission",value="To submit your solves, please go to the private channel named `submit [event name]`, which will appear once you select an event. The scrambles for each solve will be revealed after you submit your previous solve in the same channel.")
            embed.add_field(name="Penalties", value="If you need to add a penalty to a solve, you can do so by using the penalty buttons located under each scramble in the private channel.")
            embed.add_field(name="Results", value="Results will be available after each round.")
            embed.add_field(name="Good Luck!", value="Have fun competing! If you have any questions, feel free to ask in the designated discussion channel.")



            # Send the embed to a channel or user
            msg = await ctx.send(embed=embed, view=EventSelectorView(bot))

            msg = await msg.fetch()

            with open('data/Messages.tsv', "a") as messages:
                messages.write(f"{ctx.channel.id}\t{msg.id}\n")

