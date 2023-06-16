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
            

class SubmitButton(nextcord.ui.View):
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

async def submit(interaction, thread):

    embed = nextcord.Embed(title=f"Infomation", description="""Below you will find a scramble for a the event you selected. Once you've solved it, click the "SUBMIT" button below the scramble to input your time. A text input field will then prompt you to enter your time in the appropriate format. If you receive a plus 2 write your original time +2. For example, if your final time is 4.25 seconds and you receive a plus 2, input 4.25+2 as your time.

After submitting your time, the next scramble will automatically appear. Once you've completed the entire average, click the green "SUBMIT" button to submit your average time.

If you get DNF, input "DNF" without the quotes in the time submission field.""")
        
    await thread.send(f"<@{interaction.user.id}>", embed=embed)


    if thread_object.scramble_num > thread_object.solve_count:

        print(thread_object.results)
        if thread_object.event_id != "333mbf":
            thread_object.results = [int(x) for x in thread_object.results]
            max_val = max(thread_object.results)
            fuckinghelpme = sorted([max_val+1 if t == -1 else t for t in thread_object.results])

            trimmed_times = fuckinghelpme[max(0, thread_object.trim[0]):min(thread_object.solve_count, thread_object.solve_count - thread_object.trim[1])]
        
        else:
            trimmed_times = thread_object.results

        count_minus_ones = thread_object.results.count(-1)

        if count_minus_ones > thread_object.trim[1]:
            thread_object.average = -1
            average = "DNF"
        else:
            if thread_object.event_id == "333mbf":
                average = "N/A"

            else:
                print(trimmed_times)
                trimmed_times = [int(time) for time in trimmed_times]
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
        #print(thread_object.competition_id, "comp")
        #print(thread_object.event_id, "event")
        #print(thread_object.scramble_num, "scram")
        #print(thread_object.round_type, "round")
        #print(scrambles_df)
        scramble = scrambles_df.loc[(scrambles_df['competition_id'].astype(str) == str(thread_object.competition_id)) &
                                (scrambles_df['event_id'].astype(str) == str(thread_object.event_id)) &
                                (scrambles_df['scramble_num'].astype(str) == str(thread_object.scramble_num)) &
                                (scrambles_df['round_type'].astype(str) == str(thread_object.round_type))].iloc[0]['scramble']
        
        if event_id == "333mbf":
            with open('333mbf scrambles.txt', 'rb') as file:
                # Create a File object with the file
                file = nextcord.File(file)

                # Send the file as an attachment
                await thread.send(file=file, view=SubmitButton())

        else:
            await thread.send(f"**Scramble {thread_object.scramble_num}:**\n{scramble}", view=SubmitButton())
