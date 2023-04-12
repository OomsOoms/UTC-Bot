from nextcord.ui.view import View
import pandas as pd
import nextcord
import pickle
import sys
import asyncio


# Load the events and formats data using Pandas
events_df = pd.read_csv("data/Events.tsv", delimiter='\t')
formats_df = pd.read_csv("data/Formats.tsv", delimiter='\t')

class UserSubmit:
    def __init__(self):
        self.thread_list = {}

class ThreadObject:

    def __init__(self, thread_id, event_id):
        self.thread_id = thread_id
        self.event_id = event_id
        self.competition_id = "CubeClash2023"
        self.round_num = 1
        self.scramble_num = 0
        self.results = []

        # Find the event format/type and solve count
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


def get_thread_object(thread, event_id):
    if (thread.id) in user_submit.thread_list:
        thread_object = user_submit.thread_list[thread.id]
    
    else:
        # Create and store the object in the dictionary for faster access in future calls. cant be pickled if the thread object is passed though
        thread_object = ThreadObject(thread.id, event_id)
        user_submit.thread_list[thread.id] = thread_object
    
    # Starts on 0 so it is returned as 1 the first time
    thread_object.scramble_num += 1

    # Save the object in the pickle file so it is up to date
    with open(PICKLE_FILE_PATH, "wb") as f:
        pickle.dump(user_submit, f)
        
    return thread_object


class EmbedModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Submit Solve x")

        # create TextInput for scramble
        self.results = nextcord.ui.TextInput(label="<Scramble>", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms")
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
        msg = interaction.message
        await interaction.response.send_modal(EmbedModal())

class ConfirmModalView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Confirm", style=nextcord.ButtonStyle.success, custom_id="ResultSelectorView:confirm"
    )
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer()
        thread = interaction.channel
        await thread.send("Submitting...")
        await asyncio.sleep(1)
        await thread.delete()


async def submit(thread, event_name=None, event_id=None, result=False):

    thread_object = get_thread_object(thread, event_id)

    if result:
        thread_object.results.append(result)

    if thread_object.scramble_num == 1:
        await thread.send("Additional information")

    if thread_object.scramble_num > thread_object.solve_count:
        embed = nextcord.Embed(title="3x3 - First round", description=thread_object.results)
        msg = await thread.send(embed=embed, view=ConfirmModalView())

    else:
        await thread.send("Scramble", view=SubmitModalView())