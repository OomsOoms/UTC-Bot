from nextcord.ui.view import View
import nextcord
import asyncio


def convert_time(raw_time, thread_object):
    if thread_object.event_id == "333mbf":
        # Extract the "cubes solved" part from the raw time
        cubes_solved = raw_time.split()[0]
        raw_time = raw_time.split()[1]

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

        if thread_object.event_id == "333mbf":
            return f"{cubes_solved} {seconds}{ms}"
        else:
            return f"{seconds}{ms}"

    except:
        if "dnf" in raw_time.lower():
            return -1
        
        else:
            return False


class EmbedModal(nextcord.ui.Modal):
    def __init__(self, thread_object):
        super().__init__(f"Submit Solve {thread_object.scramble_num}")
        self.thread_object = thread_object

        self.results = nextcord.ui.TextInput(label=f"Scramble {thread_object.scramble_num}", min_length=2, max_length=128, required=True, placeholder=thread_object.format)
        self.add_item(self.results)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer()
        thread = interaction.channel
        msg = interaction.message

        converted_time = convert_time(self.results.value, self.thread_object)

        
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

            thread_object = ""#get_thread_object(thread=thread, increment=False)

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
            

class SubmitButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label="Submit", style=nextcord.ButtonStyle.primary, custom_id="ResultSelectorView:submit"
    )
    async def submit(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    
async def submit(interaction, thread, competition_object):

    embed = nextcord.Embed(title="Info", description="""Follow WCA competitions as closely as possible. Use the appropriate inspection time for the event and a stackmat if possible\n
    - Follow the scramble\n
    - Submit the time\n
    - The next scramble will be revealed\n
    Syntax""")
        
    await thread.send(f"<@{interaction.user.id}>", embed=embed)

    await thread.send("Scramble", view=SubmitButton())
