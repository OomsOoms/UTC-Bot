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
        self.image_links = {}
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


async def submit(thread, event_name=None, event_id=None, result=False):

    thread_object = get_thread_object(thread, event_id)

    if result:
        thread_object.results.append(result)

    if thread_object.scramble_num == 1:
        await thread.send("Additional information")

    if thread_object.scramble_num > thread_object.solve_count:
        embed = nextcord.Embed(title="3x3 - First round", description=thread_object.results)
        msg = await thread.send(embed=embed)

        await update_submit_button(msg)

        with open('data/Messages.tsv', "a") as messages:
            messages.write(f"{thread.guild.id}\t{thread.id}\t{msg.id}\tupdate_submit_button\n")

    else:
        msg = await thread.send(f"<Scramble {thread_object.scramble_num}>")

        await update_confirm_button(msg)

        with open('data/Messages.tsv', "a") as messages:
            messages.write(f"{thread.guild.id}\t{thread.id}\t{msg.id}\tupdate_confirm_button\n")


class EmbedModal(nextcord.ui.Modal):
    def __init__(self, msg):
        super().__init__("Submit Solve x")
        self.msg = msg

        # create TextInput for scramble
        self.results = nextcord.ui.TextInput(label="<Scramble>", min_length=2, max_length=128, required=True, placeholder="mm:ss.ms")
        self.add_item(self.results)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        thread = interaction.channel
        message = interaction.message

        # remove the message ID from the "Messages.tsv" file
        messages = pd.read_csv('data/Messages.tsv', sep='\t')

        # get the index of the row that matches the message ID and delete the row from the DataFrame
        index = messages[messages['message_id'] == message.id].index[0]
        messages = messages.drop(index)

        # write the updated DataFrame back to the file
        messages.to_csv('data/Messages.tsv', sep='\t', index=False)

        # disable the button
        await update_confirm_button(self.msg, True)

        # event_id is only needed on object creation
        await submit(thread, result=self.results.value)

        


# define the callback functions for each button
async def confirm_callback(interaction: nextcord.Interaction, msg):
    await interaction.response.send_modal(EmbedModal(msg))
    

    
async def update_confirm_button(msg, disabled=False):
    # Create "Submit" button
    confirm_button = nextcord.ui.Button(label="Submit" if not disabled else "Submitted", style=nextcord.ButtonStyle.primary, disabled=disabled)

    # Add the call back for each button    
    confirm_button.callback = lambda i: confirm_callback(i, msg)

    # Add buttons to a view
    view = View(timeout=None)
    view.add_item(confirm_button)

    # Update the message with the view
    await msg.edit(view=view)

async def submit_callback(interaction: nextcord.Interaction):
    await interaction.response.defer()
    thread = interaction.channel
    await thread.send("Submitting...")
    await asyncio.sleep(1)
    await thread.delete()
    # remove the message ID from the "Messages.tsv" file
    messages = pd.read_csv('data/Messages.tsv', sep='\t')

    # get the index of the row that matches the message ID and delete the row from the DataFrame
    index = messages[messages['message_id'] == interaction.message.id].index[0]
    messages = messages.drop(index)

    # write the updated DataFrame back to the file
    messages.to_csv('data/Messages.tsv', sep='\t', index=False)

async def update_submit_button(msg):
    submit_button = nextcord.ui.Button(label="Submit", style=nextcord.ButtonStyle.success)
    edit_button = nextcord.ui.Button(label="Edit response", style=nextcord.ButtonStyle.secondary)

    submit_button.callback = submit_callback

    view = View(timeout=None)
    view.add_item(submit_button)
    view.add_item(edit_button)

    await msg.edit(view=view)


"""
async def send_image(keys, thread):
    # Check if the image link is already in the dictionary
    if keys in user_submit.image_links:
        # If the link is found, send it
        link = user_submit.image_links[keys]
        await thread.send(link)
    else:
        # If the link is not found, find the image and upload it
        filename = "images/"
        for x in keys:
            filename += f"{x}, "
        filename = f"{filename[:-2]}.png"
        # replace with your code to find the image and upload it to Discord
        with open(filename, "rb") as f:
            image = nextcord.File(f)
            message = await thread.send(file=image)
            link = message.attachments[0].url
            user_submit.image_links[keys] = link
        # delete the image file after uploading
        os.remove(filename)
"""
