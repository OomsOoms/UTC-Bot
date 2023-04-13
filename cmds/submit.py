from nextcord.ui.view import View
import pandas as pd
import nextcord
import pickle
import sys


# Load the events and formats data using Pandas
events_df = pd.read_csv("data/Events.tsv", delimiter='\t')
formats_df = pd.read_csv("data/Formats.tsv", delimiter='\t')
competitions_df = pd.read_csv("data/Competitions.tsv", sep="\t")
schedules_df = pd.read_csv("data/Schedules.tsv", sep="\t")
scrambles_df = pd.read_csv("data/Scrambles.tsv", sep="\t")



class UserSubmit:
    def __init__(self):
        self.thread_list = {}

class ThreadObject:

    def __init__(self, thread_id, event_id):
        self.thread_id = thread_id
        self.event_id = event_id
        self.competition_id = competitions_df[competitions_df["active_day"] != 0].iloc[0]["competition_id"]
        self.scramble_num = 0
        self.results = []
        self.format = events_df.loc[events_df['event_id'] == event_id]['format'].values[0]


        # Find the schedule for the active day of the active competition
        active_day = competitions_df[competitions_df["competition_id"] == self.competition_id].iloc[0]["active_day"]
        active_schedule = schedules_df[(schedules_df["competition_id"] == self.competition_id) & (schedules_df["day_number"] == active_day)]

        # Find the event format/type and solve count
        for idx, row in active_schedule.iterrows():
            row_dict = dict(row)
            if row_dict["event_id"] == event_id:
                self.round_num = row_dict["round"]
                break

        self.average_id = events_df.loc[events_df['event_id'] == event_id, 'average_id'].values[0]
        self.solve_count = formats_df.loc[formats_df['id'] == self.average_id, 'solve_count'].values[0]


# Define the name of the pickle file
PICKLE_FILE_PATH = "data/user_submit.pickle"

# Load the UserSubmit object from the pickle file
try:
    with open(PICKLE_FILE_PATH, "rb") as f:
        user_submit = pickle.load(f)
        
except:
    # Handle the case where the file is empty or corrupted
    print(f"Error: {PICKLE_FILE_PATH} is empty or corrupted. Creating a new UserSubmit object.")
    user_submit = UserSubmit()

    with open(PICKLE_FILE_PATH, "wb") as f:
        pickle.dump(user_submit, f)

print(f"UserSubmit object loaded: {sys.getsizeof(user_submit)} bytes")


def get_thread_object(thread, event_id=None, increment=True):
    if (thread.id) in user_submit.thread_list:
        thread_object = user_submit.thread_list[thread.id]
    
    else:
        # Create and store the object in the dictionary for faster access in future calls. cant be pickled if the thread object is passed though
        thread_object = ThreadObject(thread.id, event_id)
        user_submit.thread_list[thread.id] = thread_object
    
    if increment:
        # Starts on 0 so it is returned as 1 the first time
        thread_object.scramble_num += 1

    # Save the object in the pickle file so it is up to date
    with open(PICKLE_FILE_PATH, "wb") as f:
        pickle.dump(user_submit, f)
        
    return thread_object


class EmbedModal(nextcord.ui.Modal):
    def __init__(self, thread_object):
        super().__init__(f"Submit Solve {thread_object.scramble_num}")

        # create TextInput for scramble
        self.results = nextcord.ui.TextInput(label=f"Scramble {thread_object.scramble_num}", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms" if thread_object.format == "time" else "Number" if thread_object.format == "number" else "cubes solved/cubes attempted mm:ss")
        self.add_item(self.results)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        thread = interaction.channel
        msg = interaction.message

        # Create "Submit" button
        submitted_button = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.primary, disabled=True)
        
        view=View()
        view.add_item(submitted_button)

        # Update the message with the view
        await msg.edit(view=view)

        # event_id is only needed on object creation
        await submit(thread, result=self.results.value)


class SubmitModalView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Submit", style=nextcord.ButtonStyle.primary, custom_id="ResultSelectorView:submit"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        thread = interaction.channel
        thread_object = get_thread_object(thread=thread, increment=False)
        await interaction.response.send_modal(EmbedModal(thread_object))

class ConfirmModalView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Confirm", style=nextcord.ButtonStyle.success, custom_id="ResultSelectorView:confirm"
    )
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        thread = interaction.channel
        msg = interaction.message

        # Create "Submit" button
        submitting_button = nextcord.ui.Button(label="Submitting...", style=nextcord.ButtonStyle.success, disabled=True)
        
        view=View()
        view.add_item(submitting_button)

        # Update the message with the view
        await msg.edit(view=view)
        await thread.delete()


async def submit(thread, event_name=None, event_id=None, result=False):

    thread_object = get_thread_object(thread=thread, event_id=event_id)
    
    if result:
        thread_object.results.append(result)

    if thread_object.scramble_num == 1:
        await thread.send("Additional information")

    if thread_object.scramble_num > thread_object.solve_count:
        embed = nextcord.Embed(title=f"{thread_object.event_id} - {thread_object.round_num} round")
        embed.add_field(name="Solves", value = "\n".join(str(solve) for solve in thread_object.results))
        embed.add_field(name="Average", value="12.34")
        msg = await thread.send(embed=embed, view=ConfirmModalView())

    else:
        scramble = scrambles_df.loc[(scrambles_df['competition_id'] == thread_object.competition_id) &
                                (scrambles_df['event_id'].astype(str) == str(thread_object.event_id)) &
                                (scrambles_df['scramble_num'].astype(int) == thread_object.scramble_num) &
                                (scrambles_df['round_num'].astype(str) == str(thread_object.round_num))].iloc[0]['scramble']
        
        await thread.send(f"**Scramble {thread_object.scramble_num}:**\n{scramble}", view=SubmitModalView())