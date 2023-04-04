from nextcord.ui.view import View
import nextcord
import pickle
import os

    
class UserSubmit:

    def __init__(self):
        self.scramble_links = {}
        self.thread_list = {}


# Define the name of the pickle file
PICKLE_FILE_PATH = "data/user_submit.pickle"


# Load the UserSubmit object from the pickle file
try:
    with open(PICKLE_FILE_PATH, "rb") as f:
        user_submit = pickle.load(f)
except EOFError:
    # Handle the case where the file is empty or corrupted
    print(f"Error: {PICKLE_FILE_PATH} is empty or corrupted. Creating a new UserSubmit object.")
    user_submit = UserSubmit()

    with open(PICKLE_FILE_PATH, "wb") as f:
        pickle.dump(user_submit, f)


class ThreadObject:

    def __init__(self, thread, event_id):
        self.thread = thread
        self.event_id = event_id


def get_thread_object(thread, event_id):
    if (thread.id) in user_submit.thread_list:
        #with open(PICKLE_FILE_PATH, "wb") as f: # cant save as it would cause the pickling to fail as you cant pickle an object with an object as an atribute
        #    pickle.dump(user_submit, f)
        return user_submit.thread_list[thread.id]
    
    else:
        # Create and store the object in the dictionary for faster access in future calls
        thread_object = ThreadObject(thread, event_id)
        user_submit.thread_list[thread.id] = thread_object
        return thread_object


async def send_image(thread_object):
    # Check if the image link is already in the dictionary
    key = (thread_object.event_id, thread_object.round_num, thread_object.scramble_num)
    if key in thread_object.scramble_links:
        # If the link is found, send it
        link = thread_object.scramble_links[key]
        await thread_object.thread.send(link)
    else:
        # If the link is not found, find the image and upload it
        filename = f"{key}.png"
        # replace with your code to find the image and upload it to Discord
        with open(filename, "rb") as f:
            image = nextcord.File(f)
            message = await thread_object.thread.send(file=image)
            link = message.attachments[0].url
            thread_object.scramble_links[key] = link
        # delete the image file after uploading
        os.remove(filename)


async def submit(thread, event_id=None):

    thread_object = get_thread_object(thread, event_id)

    #await send_image(thread_object) # not going to test this until there is images
    msg = await thread.send(thread_object)

    await update_button(msg)

    with open('data/Messages.tsv', "a") as messages:
        messages.write(f"{thread.guild.id}\t{thread.id}\t{msg.id}\tupdate_button\n")


# define the callback functions for each button
async def confirm_callback(interaction: nextcord.Interaction):
    thread = interaction.channel
    message = interaction.message

    # disable the buttons
    await update_button(message, True)
    # remove the message ID from the "Messages.tsv" file

    # event_id is only needed on object creation
    await submit(thread)

async def plus_two_callback(interaction: nextcord.Interaction):
    await interaction.send("+2")

async def dnf_callback(interaction: nextcord.Interaction):
    await interaction.send("DNF")
    

async def update_button(message, disabled=False):
    # Create "OK", "+2", and "DNF" buttons
    confirm_button = nextcord.ui.Button(label="OK", style=nextcord.ButtonStyle.green, disabled=disabled)
    plus_two_button = nextcord.ui.Button(label="+2", style=nextcord.ButtonStyle.grey, disabled=disabled)
    dnf_button = nextcord.ui.Button(label="DNF", style=nextcord.ButtonStyle.red, disabled=disabled)

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
