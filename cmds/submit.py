from nextcord.ui.view import View
import pandas as pd
import nextcord
import pickle
import sys
import asyncio


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

    def __init__(self, thread_id, event_id, interaction):
        self.thread_id = thread_id
        self.event_id = event_id
        self.user_id = interaction.user.id
        self.guild_id = interaction.guild.id
        self.competition_id = competitions_df[competitions_df["active_day"] != 0].iloc[0]["competition_id"]
        self.scramble_num = 0
        self.results = []
        self.average = None

        
        # Find the schedule for the active day of the active competition
        active_day = competitions_df[competitions_df["competition_id"] == self.competition_id].iloc[0]["active_day"]
        print(active_day)
        active_schedule = schedules_df[(schedules_df["competition_id"] == self.competition_id) & (schedules_df["day_number"] == active_day)]

        print(active_schedule)

        # Find the event format/type and solve count
        for idx, row in active_schedule.iterrows():
            row_dict = dict(row)
            if row_dict["event_id"] == event_id:
                self.round_type = row_dict["round"]
                break
                    
        
        self.format = events_df.loc[events_df['event_id'] == event_id]["format"].values[0]
        self.average_id = events_df.loc[events_df['event_id'] == event_id]["average_id"].values[0]
        self.solve_count = formats_df.loc[formats_df['id'] == self.average_id]["solve_count"].values[0]
        self.trim = [formats_df.loc[formats_df['id'] == self.average_id]["trim_fastest_n"].values[0], formats_df.loc[formats_df['id'] == self.average_id]["trim_slowest_n"].values[0]]


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


def get_thread_object(thread, event_id=None, increment=True, interaction=None):
    if (thread.id) in user_submit.thread_list:
        thread_object = user_submit.thread_list[thread.id]
    
    else:
        # Create and store the object in the dictionary for faster access in future calls. cant be pickled if the thread object is passed though
        thread_object = ThreadObject(thread.id, event_id, interaction=interaction)
        user_submit.thread_list[thread.id] = thread_object
    
    if increment:
        # Starts on 0 so it is returned as 1 the first time
        thread_object.scramble_num += 1

    # Save the object in the pickle file so it is up to date
    with open(PICKLE_FILE_PATH, "wb") as f:
        pickle.dump(user_submit, f)
        
    return thread_object

def convert_time(raw_time):
    try:
        penalty = 2 if "+2" in raw_time else 0

        raw_time = raw_time.replace("+2", "")

        # First, split the time into minutes and seconds, if applicable
        time_parts = raw_time.split(":")

        if len(time_parts) == 1:
            # If there are no minutes, just use the raw time as the seconds
            seconds = float(raw_time)
        else:
            # Otherwise, convert the minutes and seconds to seconds
            minutes = int(time_parts[0])
            seconds = float(time_parts[1])
            seconds += minutes * 60

        if int(seconds) < 0:
            return False

        seconds, ms = str(seconds).split(".")

        seconds = str(int(seconds) + penalty)

        ms = ms[:2]

        ms = f"{ms}0" if len(ms) == 1 else ms

        return f"{seconds}{ms}"
    
    except:
        if "dnf" in raw_time.lower():
            return -1
        
        else:
            return False



class EmbedModal(nextcord.ui.Modal):
    def __init__(self, thread_object):
        super().__init__(f"Submit Solve {thread_object.scramble_num}")

        self.results = nextcord.ui.TextInput(label=f"Scramble {thread_object.scramble_num}", min_length=2, max_length=128, required=True, placeholder=thread_object.format)
        self.add_item(self.results)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        thread = interaction.channel
        msg = interaction.message

        converted_time = int(convert_time(self.results.value))

        if converted_time:
            # event_id is only needed on object creation
            await submit(thread, result=converted_time)

            # Create "Submit" button
            submitted_button = nextcord.ui.Button(label="Submitted", style=nextcord.ButtonStyle.primary, disabled=True)
            
            view=View()
            view.add_item(submitted_button)

            # Update the message with the view
            await msg.edit(view=view)
        else:
            await interaction.send("Invalid format", ephemeral=True)


class SubmitModalView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Submit", style=nextcord.ButtonStyle.primary, custom_id="ResultSelectorView:submit"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        thread = interaction.channel
        thread_object = get_thread_object(thread=thread, increment=False)

        if interaction.user.id == get_thread_object(thread=thread, increment=False).user_id:
            await interaction.response.send_modal(EmbedModal(thread_object))

        else:
            await interaction.send("This is not your thread!", ephemeral=True)

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

        try:
            # Create "Submit" button
            submitting_button = nextcord.ui.Button(label="Submitting...", style=nextcord.ButtonStyle.success, disabled=True)

            view=View()
            view.add_item(submitting_button)

            # Update the message with the view
            await msg.edit(view=view)
            
            await asyncio.sleep(1)

            thread_object = get_thread_object(thread=thread, increment=False)

            best = min([result for result in thread_object.results if result != -1])

            pos = 1

            values_list = "\t".join(str(solve) for solve in thread_object.results)

            with open("data/Results.tsv", 'a+') as file:
                file.write(f"{thread_object.competition_id}\t{thread_object.event_id}\t{thread_object.user_id}\t{thread_object.guild_id}\t{pos}\t{thread_object.round_type}\t{thread_object.average}\t{str(best)}\t{values_list}\n")

            await thread.delete()

        except Exception as error:
            print(error)
            # Create "Submit" button
            view=ConfirmModalView()

            # Update the message with the view
            await msg.edit(view=view)
        
            await interaction.send("There was an error proccessing your request. Please try again.", ephemeral=True)


async def submit(thread, event_name=None, event_id=None, result=False, user_id=None, interaction=None):

    thread_object = get_thread_object(thread=thread, event_id=event_id, interaction=interaction)
    
    if result:
        thread_object.results.append(result)

    if thread_object.scramble_num == 1:
        embed = nextcord.Embed(title=f"Infomation", description="""Below you will find a scramble for a the event you selected. Once you've solved it, click the "SUBMIT" button below the scramble to input your time. A text input field will then prompt you to enter your time in the appropriate format. If you receive a plus 2 write your original time +2. For example, if your final time is 4.25 seconds and you receive a plus 2, input 4.25+2 as your time.

After submitting your time, the next scramble will automatically appear. Once you've completed the entire average, click the green "SUBMIT" button to submit your average time.

If you get DNF, input "DNF" without the quotes in the time submission field.""")
        await thread.send(embed=embed)

    if thread_object.scramble_num > thread_object.solve_count:

        sorted_times = sorted(thread_object.results)
        max_val = max(thread_object.results)
        fuckinghelpme = sorted([max_val+1 if t == -1 else t for t in thread_object.results])

        trimmed_times = fuckinghelpme[max(0, thread_object.trim[0]):min(thread_object.solve_count, thread_object.solve_count - thread_object.trim[1])]
        

        count_minus_ones = thread_object.results.count(-1)

        if count_minus_ones > thread_object.trim[1]:
            thread_object.average = -1
            average = "DNF"
        else:
            mean = sum(trimmed_times) // len(trimmed_times) if len(trimmed_times) > 0 else 0
            thread_object.average = str(mean)


            average = f"{thread_object.average[:-2]}.{thread_object.average[-2:]}" if thread_object.average != -1 else "DNF"

        formatted_results = ["DNF" if solve == -1 else f"{str(solve)[:-2]}.{str(solve)[-2:]}" for solve in thread_object.results]

        if thread_object.round_type == 1:
            round = "First Round"
        elif thread_object.round_type == 2:
            round = "First Round"
        else:
            round = "Final"

        embed = nextcord.Embed(title=f"{round} round")
        embed.add_field(name="Solves", value = "\n".join(str(solve) for solve in formatted_results))
        embed.add_field(name="Average", value=str(average))
        await thread.send(embed=embed, view=ConfirmModalView())

    else:
        print(thread_object.competition_id, "comp")
        print(thread_object.event_id, "event")
        print(thread_object.scramble_num, "scram")
        print(thread_object.round_type, "round")
        #print(scrambles_df)
        scramble = scrambles_df.loc[(scrambles_df['competition_id'].astype(str) == str(thread_object.competition_id)) &
                                (scrambles_df['event_id'].astype(str) == str(thread_object.event_id)) &
                                (scrambles_df['scramble_num'].astype(str) == str(thread_object.scramble_num)) &
                                (scrambles_df['round_type'].astype(str) == str(thread_object.round_type))].iloc[0]['scramble']

        await thread.send(f"**Scramble {thread_object.scramble_num}:**\n{scramble}", view=SubmitModalView())
