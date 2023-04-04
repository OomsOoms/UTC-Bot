import nextcord
from nextcord.ui.view import View
import pandas as pd
import pickle

events = pd.read_csv('data/Events.tsv', sep='\t')
formats = pd.read_csv('data/Formats.tsv', sep='\t')
messages = pd.read_csv('data/Messages.tsv', sep='\t')
scrambles = pd.read_csv('data/Scrambles.tsv', sep='\t')
object_db = open('data/submit_cycles_db.pickle', 'rb+')


# define the callback functions for each button
async def confirm_callback(interaction: nextcord.Interaction):
    thread = interaction.channel
    message = interaction.message

    # disable the buttons
    await update_button(message, True)
    # remove the message ID from the "Messages.tsv" file

    await submit(thread)



async def plus_two_callback(interaction: nextcord.Interaction):
    await interaction.send("Pressed")

async def dnf_callback(interaction: nextcord.Interaction):
    await interaction.send("Pressed")

# Update the message with the three buttons
async def update_button(message, disabled=False):
    # Create "OK", "+2", and "DNF" buttons
    confirm_button = nextcord.ui.Button(label="OK", style=nextcord.ButtonStyle.green, disabled=disabled)
    confirm_button.callback = confirm_callback

    plus_two_button = nextcord.ui.Button(label="+2", style=nextcord.ButtonStyle.grey, disabled=disabled)
    plus_two_button.callback = plus_two_callback
        
    dnf_button = nextcord.ui.Button(label="DNF", style=nextcord.ButtonStyle.red, disabled=disabled)
    dnf_button.callback = dnf_callback

    # Add buttons to a view
    view = View()
    view.add_item(confirm_button)
    view.add_item(plus_two_button)
    view.add_item(dnf_button)

    # Update the message with the view
    await message.edit(view=view)

    
class SubmitCycle:

    def __init__(self, thread, event_id):
        if event_id != None: self.event_id = event_id
        self.scramble_num = 1
        self.ids = [thread.guild.id, thread.id]
        self.event_data = events[events['event_id'] == event_id]
        self.format = formats[formats['id'].isin(self.event_data["average_id"])]
        #self.num_solves = self.format["solve_count"].item()
        
        
    def get_scramble(self):
        if False:#self.scramble_num > int(self.num_solves):
            # Average is over
            pass
        
        else:
            round_num = 1 # Temp, round managment not figured out yet
            # Filter the dataframe to only include rows that match the specified criteria
            scramble = scrambles[(scrambles['competition_id'] == "2023WEEK6") & 
                                    (scrambles['event_id'].astype(str) == str(self.event_id)) & 
                                    (scrambles['scramble_num'] == self.scramble_num) & 
                                    (scrambles['round_num'] == round_num)].iloc[0]
            
            self.scramble_num += 1

            return scramble['scramble']


# A dictionary that maps (guild_id, thread_id) tuples to SubmitCycle objects
submit_cycles = {}

def get_submit_cycle(thread, event_id):
    # Check if a SubmitCycle object already exists in the dictionary
    if (thread.id) in submit_cycles:
        return submit_cycles[thread.id]
    
    # Check if a SubmitCycle object exists in the database
    try:
        submit_cycles_db = pickle.load(object_db)
    except EOFError:
        submit_cycles_db = {}

    if (thread.id) in submit_cycles_db:
        submit_cycle = submit_cycles_db[thread.id]
        # Store the object in the dictionary for faster access in future calls
        submit_cycles[thread.id] = submit_cycle
        return submit_cycle
    
    # Otherwise, create a new SubmitCycle object and store it in the dictionary and database
    submit_cycle = SubmitCycle(thread, event_id)
    submit_cycles[thread.id] = submit_cycle
    pickle.dump(submit_cycles, object_db)
    return submit_cycle

# The submit function
async def submit(thread, event_id=None):

    # Get the SubmitCycle object for this thread
    submit_cycle = get_submit_cycle(thread, event_id)

    # Use the SubmitCycle object to get the scramble
    scramble = submit_cycle.get_scramble()

    # Send the scramble image and text
    await thread.send("an image of the scramble")
    msg = await thread.send(scramble)

    # Update the message with the buttons
    await update_button(msg)
    # Write the guild ID, channel ID, and message ID to a file
    with open('data/Messages.tsv', "a") as messages:
        messages.write(f"{thread.guild.id}\t{thread.id}\t{msg.id}\tupdate_button\n")
    