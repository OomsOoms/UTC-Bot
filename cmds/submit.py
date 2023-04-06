from nextcord.ui.view import View
import pandas as pd
import nextcord
import pickle
import sys
import os


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
    
    # Save the object in the pickle file so it is up to date
    with open(PICKLE_FILE_PATH, "wb") as f:
        pickle.dump(user_submit, f)

    # Starts on 0 so it is returned as 1 the first time
    thread_object.scramble_num += 1
    return thread_object


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


async def submit(thread, event_name=None, event_id=None):

    thread_object = get_thread_object(thread, event_id)

    if thread_object.scramble_num == 1:
        await send_image((thread_object.competition_id, thread_object.event_id, thread_object.round_num), thread)


    await thread.send(f"**Scramble {thread_object.scramble_num}:**")
    await send_image((thread_object.competition_id, thread_object.event_id, thread_object.round_num, thread_object.scramble_num), thread)
    msg = await thread.send("Penalties")

    await update_button(msg)

    with open('data/Messages.tsv', "a") as messages:
        messages.write(f"{thread.guild.id}\t{thread.id}\t{msg.id}\tupdate_button\n")

# Code that all buttons need to run
async def general_button_callback(interaction):
    thread = interaction.channel
    message = interaction.message

    # remove the message ID from the "Messages.tsv" file
    data = pd.read_csv('data/Messages.tsv', sep='\t')

    # get the index of the row that matches the message ID and delete the row from the DataFrame
    #index = data[data['message_id'] == message.id].index[0]
    #data = data.drop(index)

    # write the updated DataFrame back to the file
    data.to_csv('data/Messages.tsv', sep='\t', index=False)

    # event_id is only needed on object creation
    await submit(thread)

# define the callback functions for each button
async def confirm_callback(interaction: nextcord.Interaction):
    await update_button(interaction.message, selected="OK")
    await general_button_callback(interaction)
    await interaction.response.defer()
    
async def plus_two_callback(interaction: nextcord.Interaction):
    await update_button(interaction.message, selected="+2")
    await general_button_callback(interaction)
    await interaction.response.defer()

async def dnf_callback(interaction: nextcord.Interaction):
    await update_button(interaction.message, selected="DNF")
    await general_button_callback(interaction)
    await interaction.response.defer()
    
async def update_button(message, selected=None):

    # Create "OK", "+2", and "DNF" buttons
    confirm_button = nextcord.ui.Button(label="OK", style=nextcord.ButtonStyle.success)
    plus_two_button = nextcord.ui.Button(label="+2", style=nextcord.ButtonStyle.secondary)
    dnf_button = nextcord.ui.Button(label="DNF", style=nextcord.ButtonStyle.danger)

    # Set the style of the selected button to blue
    if selected == "OK":
        confirm_button.style = nextcord.ButtonStyle.primary
    elif selected == "+2":
        plus_two_button.style = nextcord.ButtonStyle.primary
    elif selected == "DNF":
        dnf_button.style = nextcord.ButtonStyle.primary

    # Add the call back for each button    
    confirm_button.callback = confirm_callback
    plus_two_button.callback = plus_two_callback
    dnf_button.callback = dnf_callback

    # Add buttons to a view
    view = View()
    view.add_item(confirm_button)
    view.add_item(plus_two_button)
    view.add_item(dnf_button)

    # Update the message with the view
    await message.edit(view=view)

